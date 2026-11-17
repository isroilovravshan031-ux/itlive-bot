import json
import time
from urllib.parse import parse_qsl, urlencode
import pytest
from conftest import login, signed_data


@pytest.mark.parametrize("path", ["/api/bootstrap", "/api/my/applications", "/api/staff/statistics", "/api/staff/leads", "/api/admin/sales", "/api/admin/export.xlsx", "/api/admin/feedback", "/api/admin/broadcasts"])
def test_no_auth_cannot_read_data(client, path):
    assert client.get(path).status_code == 401


def test_signature_tampering_duplicates_age_and_identity(client):
    valid = signed_data()
    pairs = dict(parse_qsl(valid))
    pairs["user"] = json.dumps({"id": 10001, "first_name": "Attacker"})
    for raw in [urlencode(pairs), valid + "&user=x", signed_data(timestamp=int(time.time()) - 4000), signed_data(timestamp=int(time.time()) + 120), signed_data(user=json.dumps({"id": True, "first_name": "Bad"}))]:
        assert client.post("/api/auth/telegram", json={"init_data": raw}).status_code == 401
    result = client.post("/api/auth/telegram", json={"init_data": valid})
    assert result.status_code == 200
    assert result.json()["user"]["role"] == "user"


def test_frontend_cannot_claim_admin_role(client):
    response = client.post("/api/auth/telegram", json={"init_data": signed_data(), "role": "admin"})
    assert response.status_code == 422


def test_staff_roles_are_rechecked_on_every_request(client, admin, learner):
    assert client.get("/api/staff/leads", headers=learner).status_code == 403
    data = {"telegram_id": 10002, "full_name": "Sales Test", "phone": ""}
    assert client.post("/api/admin/sales", headers=admin, json=data).status_code == 201
    assert client.get("/api/staff/leads", headers=learner).status_code == 200
    assert client.get("/api/bootstrap", headers=learner).json()["user"]["role"] == "sales"
    assert client.get("/api/admin/export.xlsx", headers=learner).status_code == 403
    assert client.delete("/api/admin/sales/10002", headers=admin).status_code == 200
    assert client.get("/api/staff/leads", headers=learner).status_code == 403
    assert client.get("/api/bootstrap", headers=learner).json()["user"]["role"] == "user"


def test_logout_revokes_token(client, learner):
    assert client.post("/api/auth/logout", headers=learner).status_code == 200
    assert client.get("/api/bootstrap", headers=learner).status_code == 401


def test_production_has_no_demo_auth_endpoint(client):
    assert client.post("/api/auth/demo", json={"role": "admin"}).status_code == 404
    assert client.get("/docs").status_code == 404
