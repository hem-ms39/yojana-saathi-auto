from fastapi import APIRouter, HTTPException

from backend.models.schemas import ProfileFormRequest
from backend.services.m3_service import M3Service

router = APIRouter(tags=["forms"])


@router.get("/forms")
async def list_forms() -> dict:
    service = M3Service()
    try:
        return await service.list_forms()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"M3 forms service unavailable: {exc}") from exc


@router.get("/forms/{scheme_id}")
async def get_form(scheme_id: str) -> dict:
    service = M3Service()
    try:
        return await service.get_form(scheme_id)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"M3 form lookup failed: {exc}") from exc


@router.post("/forms/prefill")
async def prefill_form(request: ProfileFormRequest) -> dict:
    service = M3Service()
    try:
        return await service.prefill_form(request.scheme_id, request.user_profile)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"M3 prefill failed: {exc}") from exc
