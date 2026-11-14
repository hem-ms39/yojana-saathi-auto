from fastapi import APIRouter, HTTPException

from backend.services.supabase_service import SupabaseService

router = APIRouter(tags=["schemes"])


@router.get("/schemes/{scheme_id}")
async def get_scheme(scheme_id: str, language: str = "en") -> dict[str, object]:
    service = SupabaseService()
    scheme = service.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme not found: {scheme_id}")

    localized_title = scheme.get(f"title_{language}")
    title = localized_title or scheme.get("title")

    return {
        "id": scheme.get("id"),
        "title": title,
        "funding_amount": scheme.get("funding_amount"),
        "summary": scheme.get("description"),
        "eligibility_text": scheme.get("eligibility_text"),
        "benefits_text": scheme.get("benefits_text"),
        "documents_required": scheme.get("documents_required", []),
        "application_url": scheme.get("application_url"),
        "deadline": scheme.get("deadline"),
        "ministry": scheme.get("ministry"),
        "language": language,
        "raw_data": scheme.get("raw_data"),
    }
