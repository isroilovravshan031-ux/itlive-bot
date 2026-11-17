import asyncio
import hashlib
import io
import json
import logging
import re
import time
import uuid
from collections import Counter, defaultdict, deque
from contextlib import asynccontextmanager
from html import unescape, escape
from pathlib import Path
from urllib.parse import urlparse

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BufferedInputFile, MenuButtonWebApp, WebAppInfo
from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from config import APP_URL, BASE_DIR, BOT_TOKEN, BOT_USERNAME, DEFAULT_SETTINGS, RUN_BOT, UPLOAD_DIR, ADMINS
from database.db import get_db, init_db
from database.models import Database
from handlers.quiz import QUIZ_QUESTIONS
from utils.text_helpers import FAQ_ITEMS, MENTORS_LIST
from webapp import repository as repo
from webapp.auth import admin_user, create_session, current_user, staff_user, validate_init_data
from webapp.schemas import BroadcastWrite, CourseWrite, FeedbackWrite, LeadCreate, LeadUpdate, QuizAnswers, SalesWrite, SettingsWrite, TelegramLogin
from webapp.workers import broadcast_tick, outbox_tick, worker_loop

logger = logging.getLogger(__name__)
STATIC_DIR = BASE_DIR / "miniapp" / "app"
PUBLIC_SETTINGS = set(DEFAULT_SETTINGS)
STATUSES = {"YANGI", "BOGLANILDI", "YOZILDI", "BEKOR_QILINDI"}
OWN_FIELDS = {"id", "full_name", "phone", "age", "region", "course_name", "time_preference", "status", "created_at", "updated_at", "kind"}
plain = lambda text: unescape(re.sub(r"<[^>]+>", "", text))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await repo.migrate()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    tasks = []
    bot = None
    app.state.bot_username = BOT_USERNAME
    if RUN_BOT:
        if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            raise RuntimeError("BOT_TOKEN must be configured before startup")
        if not APP_URL.startswith("https://"):
            raise RuntimeError("Set APP_URL to your public HTTPS domain (or generate RAILWAY_PUBLIC_DOMAIN)")
        from bot import create_dispatcher, setup_bot_commands
        bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
        try:
            me = await bot.get_me()
            app.state.bot_username = me.username
            await setup_bot_commands(bot)
            await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="Mini app", web_app=WebAppInfo(url=APP_URL)))
            # Do not discard updates accumulated during a deployment.
            await bot.delete_webhook(drop_pending_updates=False)
        except Exception:
            await bot.session.close()
            raise
        dp = create_dispatcher()
        tasks = [asyncio.create_task(dp.start_polling(bot, handle_signals=False, close_bot_session=False), name="telegram-polling"),
                 asyncio.create_task(worker_loop(bot, outbox_tick), name="notification-outbox"),
                 asyncio.create_task(worker_loop(bot, broadcast_tick), name="broadcast-worker")]
    app.state.runtime_tasks = tasks
    app.state.bot = bot
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        if bot:
            await bot.session.close()


app = FastAPI(title="ITLive Mini App", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


class BodyTooLarge(HTTPException):
    def __init__(self):
        super().__init__(413, "Fayl yoki xabar hajmi juda katta.")


class BodyLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        limit = 21 * 1024 * 1024 if scope["path"] == "/api/admin/uploads" else 64 * 1024
        size = 0

        async def limited_receive():
            nonlocal size
            message = await receive()
            size += len(message.get("body", b""))
            if size > limit:
                raise BodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except BodyTooLarge:
            await JSONResponse({"detail": "Fayl yoki xabar hajmi juda katta."}, status_code=413)(scope, receive, send)


app.add_middleware(BodyLimitMiddleware)
rate_windows = defaultdict(deque)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        now = time.monotonic()
        key = (request.client.host if request.client else "unknown", request.url.path == "/api/auth/telegram")
        window = rate_windows[key]
        while window and window[0] < now - 60:
            window.popleft()
        if len(window) >= (30 if key[1] else 180):
            return JSONResponse({"detail": "So‘rovlar ko‘payib ketdi. Birozdan keyin urinib ko‘ring."}, status_code=429, headers={"Retry-After": "60"})
        window.append(now)
        if len(rate_windows) > 10000:
            for old_key in list(rate_windows):
                if not rate_windows[old_key] or rate_windows[old_key][-1] < now - 60:
                    del rate_windows[old_key]
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = ("default-src 'self'; script-src 'self' https://telegram.org; style-src 'self' 'unsafe-inline'; "
        "font-src 'self'; img-src 'self' blob: data:; media-src 'self' blob:; connect-src 'self'; "
        "frame-ancestors 'self' https://web.telegram.org https://*.telegram.org https://*.t.me; base-uri 'none'; form-action 'self'")
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    errors = [{"field": ".".join(str(x) for x in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return JSONResponse({"detail": "Kiritilgan ma’lumotlarni tekshiring.", "errors": errors}, status_code=422)


@app.get("/healthz")
async def health():
    try:
        async with get_db() as db:
            await db.execute("SELECT 1")
        if any(t.done() for t in getattr(app.state, "runtime_tasks", [])):
            return JSONResponse({"status": "degraded"}, status_code=503)
        return {"status": "ok"}
    except Exception:
        return JSONResponse({"status": "unavailable"}, status_code=503)


@app.get("/api/config")
async def public_config():
    return {"bot_username": getattr(app.state, "bot_username", BOT_USERNAME)}


@app.post("/api/auth/telegram")
async def login(data: TelegramLogin):
    user = validate_init_data(data.init_data)
    token, profile = await create_session(user)
    return {"token": token, "user": profile}


@app.post("/api/auth/logout")
async def logout(user=Depends(current_user), authorization: str = Header()):
    async with get_db() as db:
        await db.execute("DELETE FROM web_sessions WHERE token_hash=?", (hashlib.sha256(authorization[7:].encode()).hexdigest(),))
        await db.commit()
    return {"ok": True}


@app.get("/api/bootstrap")
async def bootstrap(user=Depends(current_user)):
    courses = await Database.get_all_courses() if user["role"] == "admin" else await Database.get_active_courses()
    settings = await Database.get_all_settings()
    return {"user": user, "courses": courses, "settings": {k: v for k, v in settings.items() if k in PUBLIC_SETTINGS}, "faq": FAQ_ITEMS, "mentors": MENTORS_LIST,
            "quiz": [{"question": plain(q["q"]), "options": [plain(label) for label, _ in q["options"]]} for q in QUIZ_QUESTIONS]}


@app.get("/api/my/applications")
async def my_applications(user=Depends(current_user)):
    items = await Database.get_user_leads(user["id"])
    return {"items": [{k: v for k, v in r.items() if k in OWN_FIELDS} for r in items]}


@app.post("/api/applications", status_code=201)
async def apply(data: LeadCreate, user=Depends(current_user), idempotency_key: str = Header(min_length=16, max_length=100)):
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", idempotency_key):
        raise HTTPException(422, "Ariza kaliti yaroqsiz. Sahifani yangilang.")
    lead = await repo.create_lead(user, data, idempotency_key)
    return {k: v for k, v in lead.items() if k in OWN_FIELDS}


@app.post("/api/feedback", status_code=201)
async def feedback(data: FeedbackWrite, user=Depends(current_user)):
    async with get_db() as db:
        await db.execute("BEGIN IMMEDIATE")
        count = (await (await db.execute("SELECT COUNT(*) FROM feedback WHERE user_id=? AND created_at>datetime('now','-10 minutes')", (user["id"],))).fetchone())[0]
        if count >= 5:
            raise HTTPException(429, "10 daqiqada 5 ta xabar yuborish mumkin.")
        cur = await db.execute("INSERT INTO feedback(user_id,full_name,username,message) VALUES (?,?,?,?)", (user["id"], user["full_name"], user.get("username"), data.message))
        await repo.enqueue(db, ADMINS, {"text": f"✍️ <b>Yangi fikr #{cur.lastrowid}</b>\n{escape(user['full_name'])}\n\n{escape(data.message)}"})
        await db.commit()
    return {"id": cur.lastrowid}


@app.post("/api/quiz/result")
async def quiz_result(data: QuizAnswers, user=Depends(current_user)):
    scores = Counter({k: 0 for k in ["backend", "frontend", "mobile", "design", "security"]})
    for question, answer in zip(QUIZ_QUESTIONS, data.answers):
        scores[question["options"][answer][1]] += 1
    winner = max(scores, key=scores.get)
    info = {"backend": ("Python Backend", "python", "Mantiqiy masalalar va serverlar bilan ishlash sizga yaqin."),
            "frontend": ("Frontend dasturlash", "frontend", "Vizual natijalar va interaktiv saytlar yaratish sizga mos."),
            "mobile": ("Flutter Mobile", "flutter", "Kundalik hayotni qulay qiladigan mobil ilovalar yarating."),
            "design": ("Grafik dizayn & UI/UX", "dizayn", "Ijodiy fikrlash va foydalanuvchi tajribasi sizning yo‘nalishingiz."),
            "security": ("Kiberxavfsizlik", "kiber", "Tizimlarni o‘rganish va himoya qilishga qiziqishingiz kuchli.")}[winner]
    active = await Database.get_active_courses()
    course = next((c for c in active if info[1] in c["name"].lower()), None)
    return {"direction": winner, "title": info[0], "description": info[2], "course_id": course["id"] if course else None}


@app.get("/api/staff/statistics")
async def stats(user=Depends(staff_user)):
    return await repo.statistics()


@app.get("/api/staff/leads")
async def leads(status: str | None = None, q: str = Query(default="", max_length=100), offset: int = Query(default=0, ge=0), limit: int = Query(default=30, ge=1, le=100), user=Depends(staff_user)):
    if status and status not in STATUSES:
        raise HTTPException(422, "Ariza holati noto‘g‘ri.")
    return await repo.list_leads(status, q, offset, limit)


@app.get("/api/staff/leads/{lead_id}")
async def lead_detail(lead_id: int, user=Depends(staff_user)):
    lead = await Database.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(404, "Ariza topilmadi.")
    return lead


@app.patch("/api/staff/leads/{lead_id}")
async def lead_update(lead_id: int, data: LeadUpdate, user=Depends(staff_user)):
    return await repo.update_lead(lead_id, user, data)


@app.post("/api/admin/courses", status_code=201)
async def course_create(data: CourseWrite, user=Depends(admin_user)):
    async with get_db() as db:
        values = data.model_dump()
        columns = list(values)
        cur = await db.execute(f"INSERT INTO courses({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})", list(values.values()))
        await db.commit()
        return dict(await (await db.execute("SELECT * FROM courses WHERE id=?", (cur.lastrowid,))).fetchone())


@app.put("/api/admin/courses/{course_id}")
async def course_update(course_id: int, data: CourseWrite, user=Depends(admin_user)):
    if not await Database.get_course_by_id(course_id):
        raise HTTPException(404, "Kurs topilmadi.")
    await Database.update_course(course_id, **data.model_dump())
    return await Database.get_course_by_id(course_id)


@app.delete("/api/admin/courses/{course_id}")
async def course_delete(course_id: int, user=Depends(admin_user)):
    if not await Database.get_course_by_id(course_id):
        raise HTTPException(404, "Kurs topilmadi.")
    await Database.delete_course(course_id)
    return {"ok": True}


@app.get("/api/admin/sales")
async def sales_list(user=Depends(admin_user)):
    return {"items": await Database.get_all_sales_reps()}


@app.post("/api/admin/sales", status_code=201)
async def sales_add(data: SalesWrite, user=Depends(admin_user)):
    if not await Database.add_sales_rep(data.telegram_id, data.full_name, data.phone):
        raise HTTPException(500, "Sotuvchi saqlanmadi. Qayta urinib ko‘ring.")
    return {"ok": True}


@app.delete("/api/admin/sales/{telegram_id}")
async def sales_remove(telegram_id: int, user=Depends(admin_user)):
    await Database.remove_sales_rep(telegram_id)
    return {"ok": True}


@app.get("/api/admin/feedback")
async def feedback_list(offset: int = Query(0, ge=0), user=Depends(admin_user)):
    async with get_db() as db:
        total = (await (await db.execute("SELECT COUNT(*) FROM feedback")).fetchone())[0]
        rows = await (await db.execute("SELECT * FROM feedback ORDER BY id DESC LIMIT 30 OFFSET ?", (offset,))).fetchall()
    return {"items": [dict(r) for r in rows], "total": total, "offset": offset}


@app.put("/api/admin/settings")
async def settings_save(data: SettingsWrite, user=Depends(admin_user)):
    for key, value in data.values.items():
        if key not in PUBLIC_SETTINGS or len(value) > (3000 if key in {"about_text", "discounts_text"} else 500) or not value:
            raise HTTPException(422, "Sozlama nomi yoki qiymati noto‘g‘ri.")
        if key in {"instagram", "telegram", "website", "youtube"}:
            url = urlparse(value)
            if url.scheme != "https" or not url.netloc or url.username or url.password:
                raise HTTPException(422, "Havola https:// bilan boshlansin.")
        if key in {"latitude", "longitude"}:
            try:
                number = float(value)
                bound = 90 if key == "latitude" else 180
                if not -bound <= number <= bound:
                    raise ValueError
            except ValueError:
                raise HTTPException(422, "Xarita koordinatasi noto‘g‘ri.") from None
    async with get_db() as db:
        await db.executemany("INSERT INTO bot_settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", list(data.values.items()))
        await db.commit()
    return {"ok": True}


async def workbook_content():
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    rows = await Database.get_all_leads_for_export()

    def build():
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "ITLive arizalar"
        ws.append(["ID", "Ism va familiya", "Telefon", "Yosh", "Hudud", "Kurs", "Qulay vaqt", "Holat", "Sotuvchi", "Izoh", "Yaratilgan", "Yangilangan"])
        fields = ["id", "full_name", "phone", "age", "region", "course_name", "time_preference", "status", "sales_person", "sales_notes", "created_at", "updated_at"]
        for row in rows:
            ws.append([row.get(key) for key in fields])
            for cell in ws[ws.max_row]:
                if isinstance(cell.value, str):
                    cell.data_type = "s"  # Never execute a user's text as a spreadsheet formula.
        for cell in ws[1]:
            cell.fill = PatternFill("solid", fgColor="65509A")
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(wrap_text=True)
        for i, width in enumerate([10, 28, 21, 9, 26, 35, 22, 22, 25, 48, 25, 30], 1):
            ws.column_dimensions[get_column_letter(i)].width = width
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        stream = io.BytesIO()
        wb.save(stream)
        return stream.getvalue()

    return await asyncio.to_thread(build)


@app.get("/api/admin/export.xlsx")
async def export_excel(user=Depends(admin_user)):
    content = await workbook_content()
    return Response(content, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": 'attachment; filename="itlive-leads.xlsx"'})


@app.post("/api/admin/export/telegram")
async def export_to_telegram(user=Depends(admin_user)):
    bot = getattr(app.state, "bot", None)
    if bot is None:
        raise HTTPException(503, "Telegramga yuborish uchun bot servisi ishlashi kerak.")
    content = await workbook_content()
    try:
        await bot.send_document(chat_id=user["id"], document=BufferedInputFile(content, filename="itlive-leads.xlsx"), caption="📊 ITLive — arizalar eksporti")
    except TelegramAPIError:
        raise HTTPException(502, "Fayl yetkazilmadi. Avval botni /start orqali ishga tushiring yoki Excelni yuklab oling.") from None
    return {"ok": True}


@app.post("/api/admin/uploads", status_code=201)
async def upload(file: UploadFile = File(), user=Depends(admin_user)):
    prefix = await file.read(32)
    if prefix.startswith(b"\xff\xd8\xff"):
        kind, extension, max_size = "photo", ".jpg", 10 * 1024 * 1024
    elif prefix.startswith(b"\x89PNG\r\n\x1a\n"):
        kind, extension, max_size = "photo", ".png", 10 * 1024 * 1024
    elif len(prefix) >= 12 and prefix[4:8] == b"ftyp":
        kind, extension, max_size = "video", ".mp4", 20 * 1024 * 1024
    else:
        await file.close()
        raise HTTPException(422, "JPG, PNG rasm yoki MP4 video tanlang.")
    upload_id = uuid.uuid4().hex
    destination = UPLOAD_DIR / (upload_id + extension)
    size = len(prefix)
    try:
        with destination.open("wb") as output:
            output.write(prefix)
            while chunk := await file.read(256 * 1024):
                size += len(chunk)
                if size > max_size:
                    raise HTTPException(413, "Rasm 10 MB, video 20 MB dan oshmasin.")
                output.write(chunk)
        async with get_db() as db:
            await db.execute("INSERT INTO web_uploads(id,filename,path,kind,owner_id) VALUES (?,?,?,?,?)", (upload_id, Path(file.filename or "media").name[:120], str(destination), kind, user["id"]))
            await db.commit()
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    return {"id": upload_id, "kind": kind, "size": size}


@app.post("/api/admin/broadcasts", status_code=201)
async def broadcast_create(data: BroadcastWrite, user=Depends(admin_user)):
    if not RUN_BOT:
        raise HTTPException(503, "Xabarnoma yuborish uchun bot servisi ishlashi kerak.")
    async with get_db() as db:
        await db.execute("BEGIN IMMEDIATE")
        previous = await (await db.execute("SELECT id FROM broadcast_jobs WHERE created_by=? AND request_key=?", (user["id"], data.request_key))).fetchone()
        if previous:
            return (await repo.broadcast_summary(previous[0]))[0]
        active = await (await db.execute("SELECT id FROM broadcast_jobs WHERE status IN ('queued','running') AND EXISTS(SELECT 1 FROM broadcast_recipients WHERE job_id=broadcast_jobs.id AND status IN ('queued','sending'))")).fetchone()
        if active:
            raise HTTPException(409, "Oldingi xabarnoma hali yakunlanmagan.")
        if data.upload_id:
            media = await (await db.execute("SELECT * FROM web_uploads WHERE id=? AND owner_id=?", (data.upload_id, user["id"]))).fetchone()
            if not media:
                raise HTTPException(404, "Media fayl topilmadi. Qayta tanlang.")
            if len(data.message) > 1024:
                raise HTTPException(422, "Rasm yoki video izohi 1024 belgidan oshmasin.")
        total = (await (await db.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
        cur = await db.execute("INSERT INTO broadcast_jobs(created_by,message,upload_id,total,request_key) VALUES (?,?,?,?,?)", (user["id"], data.message, data.upload_id, total, data.request_key))
        await db.execute("INSERT INTO broadcast_recipients(job_id,user_id) SELECT ?,user_id FROM users", (cur.lastrowid,))
        await db.commit()
    return (await repo.broadcast_summary(cur.lastrowid))[0]


@app.get("/api/admin/broadcasts")
async def broadcast_list(user=Depends(admin_user)):
    return {"items": await repo.broadcast_summary()}


@app.post("/api/admin/broadcasts/{job_id}/cancel")
async def broadcast_cancel(job_id: int, user=Depends(admin_user)):
    async with get_db() as db:
        await db.execute("BEGIN IMMEDIATE")
        await db.execute("UPDATE broadcast_jobs SET status='cancelled' WHERE id=? AND status IN ('queued','running')", (job_id,))
        await db.execute("UPDATE broadcast_recipients SET status='cancelled' WHERE job_id=? AND status='queued'", (job_id,))
        await db.commit()
    return {"ok": True}


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html", headers={"Cache-Control": "no-cache"})


app.mount("/static", StaticFiles(directory=STATIC_DIR, check_dir=False), name="static")
