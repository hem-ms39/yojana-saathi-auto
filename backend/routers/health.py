from fastapi import APIRouter

from backend.services.m3_service import M3Service
from backend.services.supabase_service import SupabaseService
from backend.services.twilio_service import TwilioService

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict[str, object]:
    supabase = SupabaseService()
    twilio = TwilioService()
    m3 = M3Service()

    db_ok = False
    if supabase.is_configured:
        try:
            db_ok = supabase.healthcheck()
        except Exception:
            db_ok = False

    m3_ok = await m3.healthcheck()

    return {
        "status": "ok",
        "services": {
            "supabase": "ok" if db_ok else "not_configured_or_unreachable",
            "twilio": "configured" if twilio.client else "not_configured",
            "m3_api": "ok" if m3_ok else "unreachable",
        },
    }
