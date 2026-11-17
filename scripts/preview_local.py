"""Start a local-only, isolated QA database; never connects to the real bot."""
import asyncio
import hashlib
import hmac
import json
import os
import secrets
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlencode, quote

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
preview_dir = Path(tempfile.mkdtemp(prefix="itlive-studio-preview-"))
token = "123456789:" + secrets.token_urlsafe(32)
os.environ.update(BOT_TOKEN=token, ADMINS="700000001", RUN_BOT="false", APP_URL="http://127.0.0.1:8010", BOT_USERNAME="", DATABASE_PATH=str(preview_dir / "preview.db"), UPLOAD_DIR=str(preview_dir / "uploads"))

from database.db import init_db, get_db
from database.models import Database


async def seed():
    await init_db()
    for uid, name in [(700000001, "Namuna Admin"), (700000002, "Namuna Sotuvchi"), (700000003, "Namuna Foydalanuvchi")]:
        await Database.add_or_update_user(uid, None, name)
    await Database.add_sales_rep(700000002, "Namuna Sotuvchi")
    courses = await Database.get_active_courses()
    for i, (name, status) in enumerate([("Namuna o‘quvchi A", "YANGI"), ("Namuna o‘quvchi B", "BOGLANILDI"), ("Namuna o‘quvchi C", "YOZILDI"), ("Namuna o‘quvchi D", "YANGI"), ("Namuna o‘quvchi E", "BEKOR_QILINDI")]):
        lead_id = await Database.create_lead(700000003, name, "+998900000000", 18 + i, "Toshkent shahri", courses[i % len(courses)]["name"], "Kechki")
        await Database.update_lead_status(lead_id, status)
    async with get_db() as db:
        await db.execute("UPDATE leads SET created_at=datetime('now','-1 day')")
        await db.commit()


def url(uid, name):
    data = {"auth_date": str(int(time.time())), "user": json.dumps({"id": uid, "first_name": name}, ensure_ascii=False), "query_id": secrets.token_hex(8)}
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    data["hash"] = hmac.new(secret, "\n".join(f"{k}={v}" for k, v in sorted(data.items())).encode(), hashlib.sha256).hexdigest()
    return "http://127.0.0.1:8010/#tgWebAppData=" + quote(urlencode(data), safe="")


if __name__ == "__main__":
    import uvicorn
    asyncio.run(seed())
    print("LOCAL QA ONLY. Synthetic database. Telegram polling and delivery disabled.", flush=True)
    for role, uid, name in [("admin", 700000001, "Namuna Admin"), ("sales", 700000002, "Namuna Sotuvchi"), ("user", 700000003, "Namuna Foydalanuvchi")]:
        print(role.upper() + "_URL=" + url(uid, name), flush=True)
    uvicorn.run("webapp.main:app", host="127.0.0.1", port=8010, access_log=False)
