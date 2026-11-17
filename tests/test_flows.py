import asyncio
import io
import uuid

import openpyxl
import pytest
from conftest import apply, login
from database.db import get_db


def test_learner_application_idempotency_and_privacy(client, admin, learner, application):
    key = uuid.uuid4().hex
    first = apply(client, learner, application, key)
    assert first.status_code == 201, first.text
    lead = first.json()
    assert lead["phone"] == "+998900000000"
    assert lead["kind"] == "trial"
    assert apply(client, learner, application, key).json()["id"] == lead["id"]
    assert len(client.get("/api/my/applications", headers=learner).json()["items"]) == 1
    stranger = login(client, 10003)
    assert client.get("/api/my/applications", headers=stranger).json()["items"] == []
    assert client.get("/api/staff/leads/" + str(lead["id"]), headers=stranger).status_code == 403
    update = {"status": "YOZILDI", "sales_notes": "Private sales note", "updated_at": lead["updated_at"]}
    assert client.patch(f"/api/staff/leads/{lead['id']}", headers=learner, json=update).status_code == 403
    response = client.patch(f"/api/staff/leads/{lead['id']}", headers=admin, json=update)
    assert response.status_code == 200, response.text
    assert response.json()["sales_notes"] == "Private sales note"
    assert client.patch(f"/api/staff/leads/{lead['id']}", headers=admin, json=update).status_code == 409
    own = client.get("/api/my/applications", headers=learner).json()["items"][0]
    assert own["status"] == "YOZILDI" and "sales_notes" not in own and "assigned_sales_id" not in own
    stats = client.get("/api/staff/statistics", headers=admin).json()
    assert stats["total"] == stats["today"] == stats["statuses"]["YOZILDI"] == 1


@pytest.mark.parametrize("field,value", [("age", 6), ("age", 91), ("phone", "123"), ("full_name", "  "), ("course_id", 999), ("time_preference", "wrong"), ("kind", "admin")])
def test_application_validation(client, learner, application, field, value):
    application[field] = value
    assert apply(client, learner, application).status_code in {404, 422}


def test_inactive_course_rejected_and_admin_crud(client, admin, learner, application):
    course = client.get("/api/bootstrap", headers=admin).json()["courses"][0]
    payload = {k: course[k] for k in ["name", "description", "duration", "price", "technologies", "is_active", "sort_order"]}
    payload["is_active"] = False
    assert client.put("/api/admin/courses/1", headers=admin, json=payload).status_code == 200
    assert 1 not in [c["id"] for c in client.get("/api/bootstrap", headers=learner).json()["courses"]]
    assert apply(client, learner, application).status_code == 404
    payload["name"] = "Test new course"
    assert client.post("/api/admin/courses", headers=learner, json=payload).status_code == 403
    result = client.post("/api/admin/courses", headers=admin, json=payload)
    assert result.status_code == 201
    new_id = result.json()["id"]
    assert client.delete(f"/api/admin/courses/{new_id}", headers=admin).status_code == 200


def test_search_pagination_and_feedback_permissions(client, admin, learner, application):
    for n in range(3):
        apply(client, learner, {**application, "full_name": f"Learner {n}"})
    search = client.get("/api/staff/leads?q=Learner%201", headers=admin).json()
    assert search["total"] == 1 and search["items"][0]["full_name"] == "Learner 1"
    page = client.get("/api/staff/leads?limit=1&offset=1", headers=admin).json()
    assert page["total"] == 3 and len(page["items"]) == 1
    assert client.get("/api/staff/leads?q=%25", headers=admin).json()["total"] == 0
    assert client.post("/api/feedback", headers=learner, json={"message": "Question about course"}).status_code == 201
    assert client.get("/api/admin/feedback", headers=learner).status_code == 403
    assert client.get("/api/admin/feedback", headers=admin).json()["items"][0]["message"] == "Question about course"


def test_settings_allowlist_links_and_shared_database(client, admin, learner):
    assert client.put("/api/admin/settings", headers=learner, json={"values": {"center_name": "Bad"}}).status_code == 403
    for values in [{"BOT_TOKEN": "bad"}, {"website": "javascript:alert(1)"}, {"latitude": "NaN"}, {"longitude": "181"}]:
        assert client.put("/api/admin/settings", headers=admin, json={"values": values}).status_code == 422
    assert client.put("/api/admin/settings", headers=admin, json={"values": {"center_name": "Updated Academy"}}).status_code == 200
    assert client.get("/api/bootstrap", headers=learner).json()["settings"]["center_name"] == "Updated Academy"
    from database.models import Database
    assert asyncio.run(Database.get_setting("center_name")) == "Updated Academy"


def test_quiz_matches_bot_answers(client, learner):
    result = client.post("/api/quiz/result", headers=learner, json={"answers": [0, 0, 0, 0, 0]})
    assert result.status_code == 200
    assert result.json()["direction"] == "backend" and result.json()["course_id"] == 1
    assert client.post("/api/quiz/result", headers=learner, json={"answers": [9, 0, 0, 0, 0]}).status_code == 422


def test_xlsx_exports_untrusted_text_as_literal(client, admin, learner, application):
    application["full_name"] = '=HYPERLINK("https://example.com")'
    apply(client, learner, application)
    result = client.get("/api/admin/export.xlsx", headers=admin)
    assert result.status_code == 200
    book = openpyxl.load_workbook(io.BytesIO(result.content))
    assert book.active["B2"].value == application["full_name"]
    assert book.active["B2"].data_type == "s"
    assert book.active.freeze_panes == "A2"


def test_export_can_be_sent_only_to_the_signed_in_admin(client, admin, learner, monkeypatch):
    from unittest.mock import AsyncMock
    import webapp.main
    fake = AsyncMock()
    monkeypatch.setattr(webapp.main.app.state, "bot", fake)
    assert client.post("/api/admin/export/telegram", headers=learner).status_code == 403
    assert client.post("/api/admin/export/telegram", headers=admin).status_code == 200
    assert fake.send_document.call_args.kwargs["chat_id"] == 10001


def test_contact_tracker_accepts_only_the_users_own_contact(client):
    from datetime import datetime, timezone
    from unittest.mock import AsyncMock
    from aiogram.types import Message, User, Contact, Chat
    from middlewares.user_tracker import UserTrackerMiddleware
    from database.models import Database
    user = User(id=10002, first_name="Contact Test", is_bot=False)
    tracker = UserTrackerMiddleware()
    handler = AsyncMock()
    def message(owner):
        return Message(message_id=1, date=datetime.now(timezone.utc), chat=Chat(id=10002,type="private"),from_user=user,
                       contact=Contact(phone_number="+998900000000", first_name="Contact", user_id=owner))
    asyncio.run(tracker(handler, message(10003), {}))
    assert asyncio.run(Database.get_user(10002))["phone"] is None
    asyncio.run(tracker(handler, message(10002), {}))
    assert asyncio.run(Database.get_user(10002))["phone"] == "+998900000000"


def test_rate_limit_applications_and_body_size(client, learner, application):
    for _ in range(5):
        assert apply(client, learner, application).status_code == 201
    assert apply(client, learner, application).status_code == 429
    assert client.post("/api/feedback", headers=learner, json={"message": "x" * 100000}).status_code == 413


def test_migrations_are_idempotent_and_health_works(client):
    from webapp.repository import migrate
    asyncio.run(migrate())
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/.env").status_code == 404
    assert client.get("/static/../../.env").status_code == 404
    assert "frame-ancestors" in client.get("/").headers["content-security-policy"]
