import asyncio
import json
import logging
import time
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError, TelegramBadRequest
from aiogram.types import FSInputFile
from database.db import get_db
from keyboards.inline import get_sales_lead_actions

logger = logging.getLogger(__name__)


async def outbox_tick(bot: Bot):
    async with get_db() as db:
        row = await (await db.execute("SELECT * FROM notification_outbox WHERE status='queued' AND next_at<=? ORDER BY id LIMIT 1", (time.time(),))).fetchone()
    if not row:
        return False
    payload = json.loads(row["payload"])
    try:
        markup = get_sales_lead_actions(payload["lead_id"], "YANGI") if payload.get("lead_id") else None
        await bot.send_message(row["chat_id"], payload["text"], parse_mode="HTML", reply_markup=markup)
        async with get_db() as db:
            await db.execute("UPDATE notification_outbox SET status='sent',payload='{}' WHERE id=?", (row["id"],))
            await db.commit()
    except TelegramRetryAfter as exc:
        async with get_db() as db:
            await db.execute("UPDATE notification_outbox SET next_at=? WHERE id=?", (time.time() + exc.retry_after + 1, row["id"]))
            await db.commit()
        await asyncio.sleep(min(exc.retry_after, 30))
    except Exception as exc:
        attempts = row["attempts"] + 1
        status = "failed" if attempts >= 5 or isinstance(exc, (TelegramForbiddenError, TelegramBadRequest)) else "queued"
        async with get_db() as db:
            await db.execute("UPDATE notification_outbox SET attempts=?,status=?,next_at=?,error=? WHERE id=?", (attempts, status, time.time() + min(300, 2**attempts * 5), type(exc).__name__, row["id"]))
            await db.commit()
    return True


async def broadcast_tick(bot: Bot):
    async with get_db() as db:
        await db.execute("BEGIN IMMEDIATE")
        await db.execute("UPDATE broadcast_jobs SET status='finished' WHERE status IN ('queued','running') AND NOT EXISTS(SELECT 1 FROM broadcast_recipients r WHERE r.job_id=broadcast_jobs.id AND r.status IN ('queued','sending'))")
        row = await (await db.execute("""SELECT r.job_id,r.user_id,j.message,j.upload_id,u.path,u.kind
            FROM broadcast_recipients r JOIN broadcast_jobs j ON j.id=r.job_id
            LEFT JOIN web_uploads u ON u.id=j.upload_id
            WHERE r.status='queued' AND r.next_at<=? AND j.status IN ('queued','running')
            ORDER BY r.job_id,r.user_id LIMIT 1""", (time.time(),))).fetchone()
        if not row:
            await db.commit()
            return False
        await db.execute("UPDATE broadcast_recipients SET status='sending' WHERE job_id=? AND user_id=?", (row["job_id"], row["user_id"]))
        await db.execute("UPDATE broadcast_jobs SET status='running' WHERE id=?", (row["job_id"],))
        await db.commit()
    status, error, next_at = "sent", None, 0
    try:
        if row["upload_id"]:
            if not row["path"] or not Path(row["path"]).is_file():
                raise FileNotFoundError
            method = bot.send_photo if row["kind"] == "photo" else bot.send_video
            await method(chat_id=row["user_id"], **{row["kind"]: FSInputFile(row["path"])}, caption=row["message"], parse_mode=None)
        else:
            await bot.send_message(row["user_id"], row["message"], parse_mode=None)
    except TelegramRetryAfter as exc:
        status, next_at = "queued", time.time() + exc.retry_after + 1
        await asyncio.sleep(min(exc.retry_after, 30))
    except Exception as exc:
        status, error = "failed", type(exc).__name__
    async with get_db() as db:
        await db.execute("UPDATE broadcast_recipients SET status=?,error=?,next_at=? WHERE job_id=? AND user_id=?", (status, error, next_at, row["job_id"], row["user_id"]))
        await db.commit()
    return True


async def worker_loop(bot: Bot, tick):
    while True:
        try:
            active = await tick(bot)
            await asyncio.sleep(0.1 if active else 2)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("Background worker failed: %s", type(exc).__name__)
            await asyncio.sleep(5)
