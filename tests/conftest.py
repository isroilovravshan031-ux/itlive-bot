import hashlib
import hmac
import json
import os
import tempfile
import time
import uuid
from pathlib import Path
from urllib.parse import urlencode

import pytest

# Set every sensitive/configuration value before importing project modules.
# Tests never open the real local .env database or contact Telegram.
TEST_ROOT = Path(tempfile.mkdtemp(prefix="itlive-tests-"))
TEST_TOKEN = "123456789:" + "t" * 35
os.environ.update(BOT_TOKEN=TEST_TOKEN, ADMINS="10001", RUN_BOT="false", APP_URL="http://localhost", DATABASE_PATH=str(TEST_ROOT / "initial.db"), UPLOAD_DIR=str(TEST_ROOT / "uploads"))

from fastapi.testclient import TestClient
from webapp.main import app, rate_windows


def signed_data(user_id=10002, *, timestamp=None, **extra):
    data = {"auth_date": str(int(time.time()) if timestamp is None else timestamp), "query_id": uuid.uuid4().hex,
            "user": json.dumps({"id": user_id, "first_name": "Test", "last_name": str(user_id)}, separators=(",", ":"))}
    data.update(extra)
    secret = hmac.new(b"WebAppData", TEST_TOKEN.encode(), hashlib.sha256).digest()
    data["hash"] = hmac.new(secret, "\n".join(f"{k}={v}" for k, v in sorted(data.items())).encode(), hashlib.sha256).hexdigest()
    return urlencode(data)


@pytest.fixture
def client(tmp_path, monkeypatch):
    import database.db
    import webapp.main
    monkeypatch.setattr(database.db, "DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setattr(webapp.main, "UPLOAD_DIR", tmp_path / "uploads")
    rate_windows.clear()
    with TestClient(app) as instance:
        yield instance


def login(client, user_id=10002):
    result = client.post("/api/auth/telegram", json={"init_data": signed_data(user_id)})
    assert result.status_code == 200, result.text
    return {"Authorization": "Bearer " + result.json()["token"]}


@pytest.fixture
def admin(client):
    return login(client, 10001)


@pytest.fixture
def learner(client):
    return login(client, 10002)


@pytest.fixture
def application():
    return {"full_name": "Test <name>", "phone": "+998 90 000 00 00", "age": 18, "region": "Toshkent shahri", "course_id": 1, "time_preference": "Kechki", "kind": "trial"}


def apply(client, headers, payload, key=None):
    return client.post("/api/applications", headers={**headers, "Idempotency-Key": key or uuid.uuid4().hex}, json=payload)
