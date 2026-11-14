import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from backend.models.schemas import ApplicationRequest, ApplicationResponse
from backend.services.m3_service import M3Service
from backend.services.portal_service import attempt_udyam_submit
from backend.services.supabase_service import SupabaseService
from backend.services.twilio_service import TwilioService

router = APIRouter(tags=["apply"])


class PortalAttemptRequest(BaseModel):
    full_name: str = "Demo User"
    aadhaar: str | None = None
    application_id: str | None = None
    headless: bool = False


@router.post("/apply", response_model=ApplicationResponse)
async def apply_for_scheme(request: ApplicationRequest) -> ApplicationResponse:
    application_id = f"YS-{uuid.uuid4().hex[:8].upper()}"
    supabase = SupabaseService()
    twilio = TwilioService()
    m3 = M3Service()

    form_data = request.form_data
    if request.user_profile:
        try:
            prefilled = await m3.prefill_form(request.scheme_id, request.user_profile)
            form_data = {
                **request.form_data,
                "_m3_prefill": prefilled,
            }
        except Exception:
            form_data = request.form_data

    persisted = supabase.create_application(
        application_id=application_id,
        user_id=request.user_id,
        scheme_id=request.scheme_id,
        form_data=form_data,
    )
    whatsapp_sent = await twilio.send_application_update(
        scheme_id=request.scheme_id,
        application_id=application_id,
        to_number=request.notify_phone,
    )
    return ApplicationResponse(
        application_id=application_id,
        status="applied",
        message="Application submitted successfully",
        whatsapp_sent=whatsapp_sent,
        persisted=persisted,
        next_steps="You will receive status updates via WhatsApp." if whatsapp_sent else None,
    )


@router.post("/apply/portal-attempt")
async def portal_attempt(request: PortalAttemptRequest) -> dict:
    """
    Drives the real Udyam Registration portal with a Verhoeff-invalid
    Aadhaar and captures the rejection. Returns screenshot URL + error text.
    """
    return await attempt_udyam_submit(
        applicant_name=request.full_name or "Demo User",
        fake_aadhaar=request.aadhaar,
        headless=request.headless,
    )
