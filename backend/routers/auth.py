"""
WhatsApp OTP authentication endpoints.
Fallback for when email OTP rate limit is exceeded.
"""
from __future__ import annotations

import random
import re
import string
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import settings

router = APIRouter(prefix="/v1/auth", tags=["auth"])

# In-memory OTP store: phone -> {otp, expires_at}
# For production, use Redis. Fine for hackathon demo.
_otp_store: dict[str, dict[str, Any]] = {}

OTP_TTL = 600  # 10 minutes


class SendOtpRequest(BaseModel):
    phone: str  # e.g. "+919876543210"


class VerifyOtpRequest(BaseModel):
    phone: str
    otp: str


def _normalize_phone(phone: str) -> str:
    """Ensure phone has +91 prefix."""
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("91") and len(digits) == 12:
        return f"+{digits}"
    if len(digits) == 10:
        return f"+91{digits}"
    return f"+{digits}"


def _generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


@router.post("/whatsapp-otp/send")
async def send_whatsapp_otp(req: SendOtpRequest) -> dict:
    phone = _normalize_phone(req.phone)

    # Rate limit: max 3 sends per phone per 10 min
    existing = _otp_store.get(phone)
    if existing and time.time() < existing.get("expires_at", 0):
        attempts = existing.get("send_count", 0)
        if attempts >= 3:
            raise HTTPException(429, "Too many OTP requests. Please wait 10 minutes.")

    otp = _generate_otp(6)
    send_count = (existing.get("send_count", 0) + 1) if existing else 1
    _otp_store[phone] = {
        "otp": otp,
        "expires_at": time.time() + OTP_TTL,
        "send_count": send_count,
    }

    # Send via Twilio WhatsApp
    if not (settings.twilio_account_sid and settings.twilio_auth_token and settings.twilio_whatsapp_from):
        raise HTTPException(503, "WhatsApp notifications not configured")

    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        wa_to = f"whatsapp:{phone}"
        client.messages.create(
            from_=settings.twilio_whatsapp_from,
            to=wa_to,
            body=(
                f"🇮🇳 *Yojana Saathi* — Your sign-in code is:\n\n"
                f"*{otp}*\n\n"
                f"Valid for 10 minutes. Do not share this code."
            ),
        )
    except Exception as exc:
        raise HTTPException(500, f"Failed to send WhatsApp OTP: {exc}") from exc

    return {"sent": True, "phone": phone}


@router.post("/whatsapp-otp/verify")
async def verify_whatsapp_otp(req: VerifyOtpRequest) -> dict:
    phone = _normalize_phone(req.phone)
    stored = _otp_store.get(phone)

    if not stored:
        raise HTTPException(400, "No OTP found for this number. Please request a new one.")
    if time.time() > stored["expires_at"]:
        del _otp_store[phone]
        raise HTTPException(400, "OTP has expired. Please request a new one.")
    if stored["otp"] != req.otp.strip():
        raise HTTPException(400, "Incorrect OTP. Please try again.")

    # OTP verified — clean up
    del _otp_store[phone]

    # Create or retrieve Supabase user and generate a session
    try:
        from supabase import create_client
        admin = create_client(settings.supabase_url, settings.supabase_service_key)

        # Use a stable fake email derived from the phone number
        digits = re.sub(r"\D", "", phone)
        fake_email = f"wa{digits}@yojanasaathi.app"

        # Create user if not exists (ignore error if already exists)
        try:
            admin.auth.admin.create_user({
                "email": fake_email,
                "email_confirm": True,
                "user_metadata": {
                    "phone": phone,
                    "auth_method": "whatsapp",
                },
            })
        except Exception:
            pass  # User already exists

        # Generate a magic-link token to get access + refresh tokens
        link_resp = admin.auth.admin.generate_link({
            "type": "magiclink",
            "email": fake_email,
        })

        props = link_resp.properties
        return {
            "verified": True,
            "phone": phone,
            "access_token": props.access_token,
            "refresh_token": props.refresh_token,
            "expires_in": props.expires_in,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Session creation failed: {exc}") from exc
