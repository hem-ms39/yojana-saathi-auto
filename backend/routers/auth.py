"""
WhatsApp OTP authentication endpoints (Meta WhatsApp Cloud API).
Alternative to Supabase email OTP.
"""
from __future__ import annotations

import logging
import re
import secrets
import string
import time
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import settings
from backend.services.whatsapp_service import WhatsAppError, WhatsAppService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/auth", tags=["auth"])

# User-facing messages for common WhatsApp Cloud API error codes
# (https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes).
_SEND_DEFAULT_ERROR = "Could not send the WhatsApp code right now. Please try again or use email."
_SEND_ERRORS: dict[int, str] = {
    # Test numbers can only message recipients added under WhatsApp → API Setup.
    131030: "This number isn't on the app's WhatsApp test recipient list yet. "
            "Please use email, or ask the team to add your number.",
    # Free text outside the 24-hour window and no OTP template configured.
    131047: "WhatsApp needs you to message us first. Send any message to our WhatsApp "
            "number from this phone, then tap Send OTP again.",
    131026: "Couldn't deliver to this number. Check that it uses WhatsApp.",
    132001: "WhatsApp OTP isn't set up correctly on the server (template not found). "
            "Please use email for now.",
    190: "WhatsApp OTP isn't available right now (server access token expired). "
         "Please use email for now.",
}

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
    return "".join(secrets.choice(string.digits) for _ in range(length))


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

    whatsapp = WhatsAppService()
    if not whatsapp.configured:
        _otp_store.pop(phone, None)
        raise HTTPException(503, "WhatsApp sign-in is not configured on this server.")

    try:
        await whatsapp.send_otp(phone, otp)
    except WhatsAppError as exc:
        # Full details go to the server log only.
        logger.warning("WhatsApp OTP send failed (code %s): %s", exc.code, exc.message)
        _otp_store.pop(phone, None)
        raise HTTPException(502, _SEND_ERRORS.get(exc.code, _SEND_DEFAULT_ERROR)) from exc
    except Exception as exc:
        logger.exception("WhatsApp OTP send failed")
        _otp_store.pop(phone, None)
        raise HTTPException(502, _SEND_DEFAULT_ERROR) from exc

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

        # generate_link does not return a session. It returns a one-time hashed
        # token; the browser exchanges it for a session with
        # supabase.auth.verifyOtp({ token_hash, type: "magiclink" }).
        return {
            "verified": True,
            "phone": phone,
            "token_hash": link_resp.properties.hashed_token,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Session creation failed: {exc}") from exc
