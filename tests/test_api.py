import os

os.environ.setdefault("WHATSAPP_WEBHOOK_SECRET", "test-secret")

from fastapi.testclient import TestClient

from app.main import app


def test_webhook_verification_ok():
    client = TestClient(app)
    r = client.get("/webhook", params={
        "hub.mode": "subscribe", "hub.verify_token": "test-secret", "hub.challenge": "12345",
    })
    assert r.status_code == 200
    assert r.json() == 12345


def test_webhook_verification_rejects_bad_token():
    client = TestClient(app)
    r = client.get("/webhook", params={
        "hub.mode": "subscribe", "hub.verify_token": "wrong", "hub.challenge": "1",
    })
    assert r.status_code == 403


def test_post_message_roundtrip():
    client = TestClient(app)
    r = client.post("/webhook", json={
        "phone": "+551199", "name": "Ana", "message": "quanto custa o plano?",
    })
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "sales_interest"
    assert "demo" in body["reply"].lower()


def test_health_reports_handoffs():
    client = TestClient(app)
    client.post("/webhook", json={"phone": "+553377", "message": "falar com atendente"})
    r = client.get("/health")
    assert r.json()["handoffs_pending"] >= 1
