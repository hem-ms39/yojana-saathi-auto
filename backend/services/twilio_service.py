from __future__ import annotations

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from backend.config import settings


class TwilioService:
    def __init__(self) -> None:
        self.client: Client | None = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    async def send_application_update(
        self,
        scheme_id: str,
        application_id: str,
        to_number: str | None,
    ) -> bool:
        if not self.client or not settings.twilio_whatsapp_from or not to_number:
            return False

        try:
            self.client.messages.create(
                from_=settings.twilio_whatsapp_from,
                to=f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number,
                body=(
                    f"Yojana Saathi update: application {application_id} for {scheme_id} was submitted."
                ),
            )
            return True
        except TwilioRestException:
            return False
