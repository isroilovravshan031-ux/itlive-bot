import hashlib
import hmac
import json
import re
import secrets
import time
from urllib.parse import parse_qsl

from fastapi import Depends, Header, HTTPException
from config import ADMINS, BOT_TOKEN, INIT_DATA_MAX_AGE, SESSION_MAX_AGE
from database.db import get_db
from database.models import Database


def validate_init_data(raw: str, token: str = BOT_TOKEN, now: int | None = None) -> dict:
    """Verify Telegram's HMAC before reading any identity fields."""
    try:
        if not token or not raw or len(raw) > 16384:
            raise ValueError
        pairs = parse_qsl(raw, keep_blank_values=True, strict_parsing=True, max_num_fields=32)
        if len({key for key, _ in pairs}) != len(pairs):
            raise ValueError
        data = dict(pairs)
        received_hash = data.pop("hash")
        if not re.fullmatch(r"[0-9a-fA-F]{64}", received_hash):
            raise ValueError
        check = "\n".join(f"{key}={value}" for key, value in sorted(data.items()))
        secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, received_hash.lower()):
            raise ValueError
        current = int(time.time()) if now is None else now
        age = current - int(data["auth_date"])
        if age < -30 or age > INIT_DATA_MAX_AGE:
            raise ValueError
        user = json.loads(data["user"])
        if type(user.get("id")) is not int or not 0 < user["id"] < 2**63:
            raise ValueError
        if not isinstance(user.get("first_name"), str) or len(user["first_name"]) > 128:
            raise ValueError
        return user
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(401, "Telegram sessiyasi yaroqsiz yoki eskirgan. Mini appni qayta oching.") from None


async def role_for(user_id: int) -> str:
    if user_id in ADMINS:
        return "admin"
    return "sales" if await Database.is_sales_rep(user_id) else "user"


async def create_session(user: dict) -> tuple[str, dict]:
    name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()[:200]
    username = user.get("username") if isinstance(user.get("username"), str) else None
    await Database.add_or_update_user(user["id"], username, name)
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode()).hexdigest()
    now = int(time.time())
    async with get_db() as db:
        await db.execute("DELETE FROM web_sessions WHERE expires_at < ?", (now,))
        await db.execute("INSERT INTO web_sessions (token_hash,user_id,expires_at) VALUES (?,?,?)", (digest, user["id"], now + SESSION_MAX_AGE))
        await db.commit()
    return token, {"id": user["id"], "full_name": name, "username": username, "role": await role_for(user["id"])}


async def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Telegram orqali kiring.")
    token = authorization[7:]
    if len(token) > 128:
        raise HTTPException(401, "Sessiya yaroqsiz.")
    digest = hashlib.sha256(token.encode()).hexdigest()
    async with get_db() as db:
        row = await (await db.execute("SELECT u.* FROM web_sessions s JOIN users u ON u.user_id=s.user_id WHERE s.token_hash=? AND s.expires_at>?", (digest, int(time.time())))).fetchone()
    if not row:
        raise HTTPException(401, "Sessiya tugadi. Mini appni qayta oching.")
    user = dict(row)
    user["id"] = user.pop("user_id")
    user["role"] = await role_for(user["id"])
    return user


async def staff_user(user: dict = Depends(current_user)) -> dict:
    if user["role"] not in {"admin", "sales"}:
        raise HTTPException(403, "Bu amal faqat admin va sotuvchilar uchun.")
    return user


async def admin_user(user: dict = Depends(current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(403, "Bu amal faqat admin uchun.")
    return user
