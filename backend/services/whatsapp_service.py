"""WhatsApp messaging through Meta's WhatsApp Cloud API (graph.facebook.com).

Two kinds of message:
- Free text: allowed only within 24 hours of the user last messaging our number.
- Templates: pre-approved by Meta; allowed any time (needed for business-initiated
  messages such as an OTP sent to someone who never messaged us).
"""
from __future__ import annotations

import logging
import re
from typing import Any

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)

GRAPH_URL = "https://graph.facebook.com"


class WhatsAppError(Exception):
    """A request rejected by the WhatsApp Cloud API."""

    def __init__(self, code: int | None, message: str) -> None:
        super().__init__(f"WhatsApp API error {code}: {message}")
        self.code = code
        self.message = message


def to_wa_id(phone: str) -> str:
    """Cloud API recipients are digits only with country code, e.g. '919876543210'."""
    return re.sub(r"\D", "", phone)


class WhatsAppService:
    def __init__(self) -> None:
        self.token = (settings.whatsapp_access_token or "").strip()
        self.phone_number_id = (settings.whatsapp_phone_number_id or "").strip()

    @property
    def configured(self) -> bool:
        return bool(self.token and self.phone_number_id)

    async def send_text(self, to: str, body: str) -> None:
        await self._post({"to": to_wa_id(to), "type": "text", "text": {"body": body}})

    async def send_template(
        self,
        to: str,
        name: str,
        body_params: list[str],
        *,
        language: str,
        copy_code: str | None = None,
    ) -> None:
        components: list[dict[str, Any]] = [
            {"type": "body", "parameters": [{"type": "text", "text": p} for p in body_params]}
        ]
        if copy_code is not None:
            # Authentication templates have a copy-code button that also takes the code.
            components.append(
                {
                    "type": "button",
                    "sub_type": "url",
                    "index": "0",
                    "parameters": [{"type": "text", "text": copy_code}],
                }
            )
        await self._post(
            {
                "to": to_wa_id(to),
                "type": "template",
                "template": {"name": name, "language": {"code": language}, "components": components},
            }
        )

    async def send_otp(self, to: str, otp: str) -> None:
        """Send a login code: via the OTP template if configured, else as free text."""
        template = (settings.whatsapp_otp_template or "").strip()
        if template:
            await self.send_template(
                to,
                template,
                [otp],
                language=settings.whatsapp_template_language,
                copy_code=otp if settings.whatsapp_otp_template_has_button else None,
            )
        else:
            await self.send_text(
                to, f"Yojana Saathi sign-in code: {otp}. Valid for 10 minutes. Do not share this code."
            )

    async def send_application_update(
        self, scheme_id: str, application_id: str, to_number: str | None
    ) -> bool:
        """Best effort: returns False instead of raising (the application is already saved)."""
        if not self.configured or not to_number:
            return False
        try:
            await self.send_text(
                to_number,
                f"Yojana Saathi update: application {application_id} for {scheme_id} was submitted.",
            )
            return True
        except Exception as exc:
            logger.warning("WhatsApp application update not sent: %s", exc)
            return False

    async def _post(self, message: dict[str, Any]) -> dict[str, Any]:
        url = f"{GRAPH_URL}/{settings.whatsapp_api_version}/{self.phone_number_id}/messages"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                json={"messaging_product": "whatsapp", "recipient_type": "individual", **message},
            )
        data: dict[str, Any] = {}
        try:
            data = response.json()
        except ValueError:
            pass
        if response.is_success:
            return data
        error = data.get("error", {}) if isinstance(data, dict) else {}
        details = (error.get("error_data") or {}).get("details")
        raise WhatsAppError(error.get("code"), details or error.get("message") or response.text[:200])
