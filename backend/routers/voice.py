
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.services.m3_service import M3Service

router = APIRouter(tags=["voice"])


@router.post("/voice")
async def process_voice(audio: UploadFile = File(...), language: str = Form("en")) -> dict[str, str]:
    return {
        "filename": audio.filename or "upload",
        "language_detected": language,
        "redirect_to": "/chat",
    }


@router.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    scheme_id: str = Form(...),
    doc_type: str = Form("auto"),
) -> dict:
    service = M3Service()
    content = await file.read()

    try:
        return await service.ocr_extract_and_fill(
            filename=file.filename or "upload",
            content=content,
            content_type=file.content_type or "image/jpeg",
            scheme_id=scheme_id,
            doc_type=doc_type,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"M3 OCR service unavailable: {exc}") from exc
