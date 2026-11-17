import asyncio
import base64
from unittest.mock import AsyncMock

from conftest import apply, login
from database.db import get_db
from webapp.workers import broadcast_tick, outbox_tick


def test_lead_notifications_are_durable_escaped_and_acked(client, admin, learner, application):
    apply(client, learner, application)
    fake = AsyncMock()
    assert asyncio.run(outbox_tick(fake))
    assert "Test &lt;name&gt;" in fake.send_message.call_args.args[1]
    assert not asyncio.run(outbox_tick(fake))


def test_failed_notifications_remain_retryable(client, learner, application):
    apply(client, learner, application)
    fake = AsyncMock()
    fake.send_message.side_effect = ConnectionError()
    assert asyncio.run(outbox_tick(fake))

    async def read():
        async with get_db() as db:
            return dict(await (await db.execute("SELECT * FROM notification_outbox")).fetchone())
    row = asyncio.run(read())
    assert row["status"] == "queued" and row["attempts"] == 1 and row["error"] == "ConnectionError"


def test_broadcast_permissions_confirmation_idempotency_cancel_and_resume(client, admin, learner, monkeypatch):
    import webapp.main
    monkeypatch.setattr(webapp.main, "RUN_BOT", True)
    payload = {"message": "Hello class", "confirmed": True, "request_key": "test_broadcast_1234567"}
    assert client.post("/api/admin/broadcasts", headers=learner, json=payload).status_code == 403
    assert client.post("/api/admin/broadcasts", headers=admin, json={**payload, "confirmed": False}).status_code == 422
    result = client.post("/api/admin/broadcasts", headers=admin, json=payload)
    assert result.status_code == 201, result.text
    job = result.json()
    assert job["total"] == 2
    assert client.post("/api/admin/broadcasts", headers=admin, json=payload).json()["id"] == job["id"]
    fake = AsyncMock()
    assert asyncio.run(broadcast_tick(fake))
    summary = client.get("/api/admin/broadcasts", headers=admin).json()["items"][0]
    assert summary["sent"] == 1 and summary["remaining"] == 1
    assert client.post(f"/api/admin/broadcasts/{job['id']}/cancel", headers=admin).status_code == 200
    assert not asyncio.run(broadcast_tick(fake))
    assert client.get("/api/admin/broadcasts", headers=admin).json()["items"][0]["status"] == "cancelled"


def test_upload_validation_and_real_photo_broadcast(client, admin, monkeypatch):
    import webapp.main
    monkeypatch.setattr(webapp.main, "RUN_BOT", True)
    bad = client.post("/api/admin/uploads", headers=admin, files={"file": ("fake.png", b"<script>bad</script>", "image/png")})
    assert bad.status_code == 422
    photo = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6I2kAAAAASUVORK5CYII=")
    upload = client.post("/api/admin/uploads", headers=admin, files={"file": ("photo.png", photo, "image/png")})
    assert upload.status_code == 201
    payload = {"message": "Photo caption", "upload_id": upload.json()["id"], "confirmed": True, "request_key": "test_media_broadcast_1"}
    job = client.post("/api/admin/broadcasts", headers=admin, json=payload)
    assert job.status_code == 201
    fake = AsyncMock()
    assert asyncio.run(broadcast_tick(fake))
    fake.send_photo.assert_awaited_once()


def test_bot_disabled_does_not_send_broadcast(client, admin):
    assert client.post("/api/admin/broadcasts", headers=admin, json={"message": "No send", "confirmed": True, "request_key": "test_disabled_broadcast"}).status_code == 503
