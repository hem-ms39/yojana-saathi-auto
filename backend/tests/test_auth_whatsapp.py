"""WhatsApp OTP auth (Meta WhatsApp Cloud API) — offline: no network, no Supabase."""
import time

import pytest

from backend.routers import auth
from backend.services import whatsapp_service
from backend.services.whatsapp_service import WhatsAppError, WhatsAppService, to_wa_id


@pytest.fixture
def sent(monkeypatch):
    """Configure WhatsApp and capture outgoing Cloud API payloads instead of sending."""
    payloads: list[dict] = []

    async def fake_post(self, message):
        payloads.append(message)
        return {"messages": [{"id": "wamid.TEST"}]}

    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_access_token", "EAAG_SECRET_TOKEN")
    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_phone_number_id", "1234567890")
    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_otp_template", None)
    monkeypatch.setattr(WhatsAppService, "_post", fake_post)
    return payloads


def test_normalize_phone_adds_india_prefix():
    assert auth._normalize_phone("9876543210") == "+919876543210"
    assert auth._normalize_phone("+91 98765 43210") == "+919876543210"
    assert auth._normalize_phone("919876543210") == "+919876543210"


def test_wa_id_is_digits_only():
    assert to_wa_id("+91 98765-43210") == "919876543210"


def test_generated_otp_is_six_digits():
    otp = auth._generate_otp()
    assert len(otp) == 6 and otp.isdigit()


def test_send_fails_cleanly_when_whatsapp_not_configured(client):
    r = client.post("/v1/auth/whatsapp-otp/send", json={"phone": "9876543210"})
    assert r.status_code == 503
    assert "not configured" in r.json()["detail"]
    assert "+919876543210" not in auth._otp_store


def test_send_uses_free_text_without_template(client, sent):
    r = client.post("/v1/auth/whatsapp-otp/send", json={"phone": "9000000001"})
    assert r.status_code == 200
    msg = sent[-1]
    assert msg["to"] == "919000000001" and msg["type"] == "text"
    assert auth._otp_store["+919000000001"]["otp"] in msg["text"]["body"]


def test_send_uses_authentication_template_when_configured(client, sent, monkeypatch):
    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_otp_template", "yojana_otp")
    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_otp_template_has_button", True)

    r = client.post("/v1/auth/whatsapp-otp/send", json={"phone": "9000000002"})
    assert r.status_code == 200
    otp = auth._otp_store["+919000000002"]["otp"]
    template = sent[-1]["template"]
    assert sent[-1]["type"] == "template" and template["name"] == "yojana_otp"
    body, button = template["components"]
    assert body == {"type": "body", "parameters": [{"type": "text", "text": otp}]}
    assert button["type"] == "button" and button["parameters"][0]["text"] == otp


def test_api_error_is_friendly_and_hides_token(client, sent, monkeypatch):
    async def failing_post(self, message):
        raise WhatsAppError(131030, "Recipient phone number not in allowed list (EAAG_SECRET_TOKEN)")

    monkeypatch.setattr(WhatsAppService, "_post", failing_post)
    r = client.post("/v1/auth/whatsapp-otp/send", json={"phone": "9000000003"})
    assert r.status_code == 502
    assert "test recipient list" in r.json()["detail"]
    assert "EAAG_SECRET_TOKEN" not in r.text
    assert "+919000000003" not in auth._otp_store  # failed send leaves no usable code


async def test_application_update_never_raises(monkeypatch):
    async def failing_post(self, message):
        raise WhatsAppError(131047, "Re-engagement message")

    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_access_token", "t")
    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_phone_number_id", "1")
    monkeypatch.setattr(WhatsAppService, "_post", failing_post)
    assert await WhatsAppService().send_application_update("pm-mudra", "YS-1", "+919000000004") is False


async def test_post_builds_request_and_parses_meta_errors(monkeypatch):
    import httpx

    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(400, json={"error": {
            "message": "(#131030) Recipient phone number not in allowed list", "code": 131030,
            "error_data": {"details": "Recipient phone number not in allowed list"}}})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(whatsapp_service.httpx, "AsyncClient",
                        lambda **kw: real_client(transport=httpx.MockTransport(handler), **kw))
    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_access_token", "tok")
    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_phone_number_id", "555")
    monkeypatch.setattr(whatsapp_service.settings, "whatsapp_api_version", "v26.0")

    with pytest.raises(WhatsAppError) as err:
        await WhatsAppService().send_text("+919000000008", "hi")
    assert err.value.code == 131030 and "allowed list" in err.value.message
    req = seen[0]
    assert str(req.url) == "https://graph.facebook.com/v26.0/555/messages"
    assert req.headers["Authorization"] == "Bearer tok"
    assert b'"messaging_product":"whatsapp"' in req.content.replace(b" ", b"")


def test_verify_without_send_is_rejected(client):
    r = client.post("/v1/auth/whatsapp-otp/verify", json={"phone": "9000000005", "otp": "123456"})
    assert r.status_code == 400
    assert "No OTP found" in r.json()["detail"]


def test_verify_wrong_code_is_rejected(client):
    auth._otp_store["+919000000006"] = {"otp": "111111", "expires_at": time.time() + 60}
    r = client.post("/v1/auth/whatsapp-otp/verify", json={"phone": "9000000006", "otp": "222222"})
    assert r.status_code == 400
    assert "Incorrect OTP" in r.json()["detail"]


def test_verify_expired_code_is_rejected(client):
    auth._otp_store["+919000000007"] = {"otp": "111111", "expires_at": time.time() - 1}
    r = client.post("/v1/auth/whatsapp-otp/verify", json={"phone": "9000000007", "otp": "111111"})
    assert r.status_code == 400
    assert "expired" in r.json()["detail"]
