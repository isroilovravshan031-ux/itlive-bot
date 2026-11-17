import json
import time
from datetime import datetime, timezone
from html import escape

from fastapi import HTTPException
from config import ADMINS
from database.db import get_db
from webapp.schemas import LeadCreate, LeadUpdate


async def migrate():
    async with get_db() as db:
        columns = {r[1] for r in await (await db.execute("PRAGMA table_info(leads)")).fetchall()}
        if "kind" not in columns:
            await db.execute("ALTER TABLE leads ADD COLUMN kind TEXT NOT NULL DEFAULT 'course'")
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS web_sessions (
                token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL, expires_at INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_web_sessions_expiry ON web_sessions(expires_at);
            CREATE TABLE IF NOT EXISTS lead_requests (
                user_id INTEGER NOT NULL, request_key TEXT NOT NULL, lead_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, request_key)
            );
            CREATE TABLE IF NOT EXISTS notification_outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER NOT NULL,
                payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'queued',
                attempts INTEGER NOT NULL DEFAULT 0, next_at REAL NOT NULL DEFAULT 0,
                error TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_outbox_queue ON notification_outbox(status,next_at);
            CREATE TABLE IF NOT EXISTS web_uploads (
                id TEXT PRIMARY KEY, filename TEXT NOT NULL, path TEXT NOT NULL,
                kind TEXT NOT NULL, owner_id INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS broadcast_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, created_by INTEGER NOT NULL,
                message TEXT NOT NULL, upload_id TEXT, status TEXT NOT NULL DEFAULT 'queued',
                total INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS broadcast_recipients (
                job_id INTEGER NOT NULL, user_id INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'queued',
                next_at REAL NOT NULL DEFAULT 0, error TEXT, PRIMARY KEY(job_id,user_id)
            );
            CREATE INDEX IF NOT EXISTS idx_broadcast_queue ON broadcast_recipients(status,next_at);
            CREATE INDEX IF NOT EXISTS idx_leads_user ON leads(user_id,created_at);
            CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status,id);
        """)
        job_columns = {r[1] for r in await (await db.execute("PRAGMA table_info(broadcast_jobs)")).fetchall()}
        if "request_key" not in job_columns:
            await db.execute("ALTER TABLE broadcast_jobs ADD COLUMN request_key TEXT")
        await db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_broadcast_request ON broadcast_jobs(created_by,request_key)")
        # A Telegram request in flight at shutdown has no idempotency primitive.
        # Do not resend an uncertain broadcast recipient automatically.
        await db.execute("UPDATE broadcast_recipients SET status='failed',error='InterruptedDelivery' WHERE status='sending'")
        await db.commit()


async def enqueue(db, recipients, payload):
    for chat_id in set(recipients):
        await db.execute("INSERT INTO notification_outbox(chat_id,payload) VALUES (?,?)", (chat_id, json.dumps(payload, ensure_ascii=False)))


async def create_lead(user: dict, data: LeadCreate, request_key: str) -> dict:
    async with get_db() as db:
        await db.execute("BEGIN IMMEDIATE")
        previous = await (await db.execute("SELECT lead_id FROM lead_requests WHERE user_id=? AND request_key=?", (user["id"], request_key))).fetchone()
        if previous:
            row = await (await db.execute("SELECT * FROM leads WHERE id=?", (previous[0],))).fetchone()
            return dict(row)
        count = await (await db.execute("SELECT COUNT(*) FROM leads WHERE user_id=? AND created_at>datetime('now','-10 minutes')", (user["id"],))).fetchone()
        if count[0] >= 5:
            raise HTTPException(429, "Ko‘p ariza yuborildi. 10 daqiqadan keyin urinib ko‘ring.")
        course = await (await db.execute("SELECT * FROM courses WHERE id=? AND is_active=1", (data.course_id,))).fetchone()
        if not course:
            raise HTTPException(404, "Bu kurs hozir faol emas. Boshqa yo‘nalishni tanlang.")
        cursor = await db.execute("""INSERT INTO leads(user_id,full_name,phone,age,region,course_name,time_preference,kind)
            VALUES (?,?,?,?,?,?,?,?)""", (user["id"], data.full_name, data.phone, data.age, data.region, course["name"], data.time_preference, data.kind))
        lead_id = cursor.lastrowid
        await db.execute("INSERT INTO lead_requests VALUES (?,?,?)", (user["id"], request_key, lead_id))
        await db.execute("UPDATE users SET phone=? WHERE user_id=?", (data.phone, user["id"]))
        row = await (await db.execute("SELECT * FROM leads WHERE id=?", (lead_id,))).fetchone()
        lead = dict(row)
        text = (f"📝 <b>Yangi {'sinov darsi' if data.kind == 'trial' else 'kurs'} arizasi #{lead_id}</b>\n"
                f"👤 {escape(data.full_name)}\n📞 <code>{escape(data.phone)}</code>\n"
                f"🎂 {data.age} yosh\n📍 {escape(data.region)}\n"
                f"📚 {escape(course['name'])}\n⏰ {escape(data.time_preference)}\n"
                f"<a href=\"tg://user?id={user['id']}\">Telegram profili</a>")
        sales = await (await db.execute("SELECT telegram_id FROM sales_team WHERE is_active=1")).fetchall()
        await enqueue(db, [r[0] for r in sales] + ADMINS, {"text": text, "lead_id": lead_id})
        await db.commit()
        return lead


async def list_leads(status: str | None, query: str, offset: int, limit: int) -> dict:
    where, values = ["1=1"], []
    if status:
        where.append("l.status=?")
        values.append(status)
    if query:
        where.append("(l.full_name LIKE ? ESCAPE '\\' OR l.phone LIKE ? ESCAPE '\\' OR l.course_name LIKE ? ESCAPE '\\' OR CAST(l.id AS TEXT)=?)")
        term = "%" + query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        values.extend([term, term, term, query])
    condition = " AND ".join(where)
    async with get_db() as db:
        total = (await (await db.execute(f"SELECT COUNT(*) FROM leads l WHERE {condition}", values)).fetchone())[0]
        rows = await (await db.execute(f"SELECT l.*,s.full_name AS sales_person FROM leads l LEFT JOIN sales_team s ON l.assigned_sales_id=s.telegram_id WHERE {condition} ORDER BY l.id DESC LIMIT ? OFFSET ?", [*values, limit, offset])).fetchall()
        return {"items": [dict(r) for r in rows], "total": total, "offset": offset, "limit": limit}


async def update_lead(lead_id: int, user: dict, data: LeadUpdate) -> dict:
    async with get_db() as db:
        await db.execute("BEGIN IMMEDIATE")
        existing = await (await db.execute("SELECT * FROM leads WHERE id=?", (lead_id,))).fetchone()
        if not existing:
            raise HTTPException(404, "Ariza topilmadi.")
        if existing["updated_at"] != data.updated_at:
            raise HTTPException(409, "Bu ariza boshqa xodim tomonidan yangilangan. Qayta oching.")
        now = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        await db.execute("UPDATE leads SET status=?,sales_notes=?,assigned_sales_id=?,updated_at=? WHERE id=?", (data.status, data.sales_notes, user["id"], now, lead_id))
        if existing["status"] != data.status:
            labels = {"YANGI": "Yangi", "BOGLANILDI": "Siz bilan bog‘lanildi", "YOZILDI": "O‘qishga yozildi", "BEKOR_QILINDI": "Bekor qilindi"}
            await enqueue(db, [existing["user_id"]], {"text": f"📂 <b>Arizangiz #{lead_id} yangilandi</b>\n{escape(existing['course_name'] or '')}\nHolat: <b>{labels[data.status]}</b>"})
        await db.commit()
        return dict(await (await db.execute("SELECT * FROM leads WHERE id=?", (lead_id,))).fetchone())


async def statistics() -> dict:
    async with get_db() as db:
        counts = await (await db.execute("SELECT status,COUNT(*) AS count FROM leads GROUP BY status")).fetchall()
        statuses = {r["status"]: r["count"] for r in counts}
        today = (await (await db.execute("SELECT COUNT(*) FROM leads WHERE date(created_at,'+5 hours')=date('now','+5 hours')")).fetchone())[0]
        top = await (await db.execute("SELECT course_name,COUNT(*) AS count FROM leads GROUP BY course_name ORDER BY count DESC LIMIT 7")).fetchall()
        daily = await (await db.execute("SELECT date(created_at,'+5 hours') AS day,COUNT(*) AS count FROM leads WHERE created_at>=datetime('now','-7 days') GROUP BY day ORDER BY day")).fetchall()
        users = (await (await db.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
    return {"total": sum(statuses.values()), "today": today, "users": users, "statuses": statuses, "top_courses": [dict(r) for r in top], "daily": [dict(r) for r in daily]}


async def broadcast_summary(job_id: int | None = None):
    async with get_db() as db:
        condition, values = ("WHERE j.id=?", (job_id,)) if job_id else ("", ())
        rows = await (await db.execute(f"""SELECT j.id,j.message,j.upload_id,j.status,j.total,j.created_at,
            COALESCE(SUM(r.status='sent'),0) AS sent,COALESCE(SUM(r.status='failed'),0) AS failed,
            COALESCE(SUM(r.status IN ('queued','sending')),0) AS remaining
            FROM broadcast_jobs j LEFT JOIN broadcast_recipients r ON r.job_id=j.id {condition}
            GROUP BY j.id ORDER BY j.id DESC LIMIT 20""", values)).fetchall()
    result = [dict(r) for r in rows]
    for row in result:
        if row["remaining"] == 0 and row["status"] in {"running", "queued"}:
            row["status"] = "finished"
    return result
