"""
M3 Backend API — FastAPI server exposing OCR and form-fill endpoints.
M4 should point their backend at this service.

Run with:
  cd d:\DeepStation\m3_workspace
  uvicorn backend.api.main:app --host 0.0.0.0 --port 8001 --reload
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import json

from backend.agents.ocr_agent import (
    extract_from_bytes, map_to_user_profile, run_ocr_pipeline, DOCUMENT_TYPES
)
from backend.agents.form_filler import (
    generate_prefilled_form, list_available_forms, get_form_template
)

app = FastAPI(
    title="Yojana Saathi — M3 Data & OCR API",
    description="OCR document extraction and form autofill for Indian government schemes",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # M2 frontend needs this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Models ─────────────────────────────────────────────────────────────────

class ProfileFormRequest(BaseModel):
    scheme_id: str
    user_profile: dict


class OCRFormRequest(BaseModel):
    scheme_id: str
    doc_type: Optional[str] = "auto"


# ─── Health ──────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Yojana Saathi M3 API",
        "status": "online",
        "endpoints": [
            "GET  /health",
            "GET  /forms",
            "GET  /forms/{scheme_id}",
            "POST /forms/prefill",
            "POST /ocr/extract",
            "POST /ocr/extract-and-fill",
            "GET  /doc-types",
        ]
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "m3-ocr-api"}


# ─── Forms ───────────────────────────────────────────────────────────────────

@app.get("/forms", tags=["Forms"],
         summary="List all available form templates")
def list_forms():
    """Returns all scheme IDs that have pre-built form templates."""
    return {
        "available_forms": list_available_forms(),
        "total": len(list_available_forms())
    }


@app.get("/forms/{scheme_id}", tags=["Forms"],
         summary="Get raw form template for a scheme")
def get_form(scheme_id: str):
    """Returns the empty form template for a given scheme."""
    template = get_form_template(scheme_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"No form template for scheme: {scheme_id}. Available: {list_available_forms()}"
        )
    return template


@app.post("/forms/prefill", tags=["Forms"],
          summary="Pre-fill a form using a user profile dict")
def prefill_form(request: ProfileFormRequest):
    """
    Given a scheme_id and user profile dict (from voice agent or OCR),
    returns the form with all extractable fields pre-filled.
    
    This is the primary integration point for M1 agents and M4 frontend.
    """
    result = generate_prefilled_form(request.scheme_id, request.user_profile)
    return result


# ─── OCR ─────────────────────────────────────────────────────────────────────

@app.get("/doc-types", tags=["OCR"],
         summary="List supported document types")
def list_doc_types():
    """Returns all document types the OCR can handle."""
    return {
        "supported_types": {k: v["display_name"] for k, v in DOCUMENT_TYPES.items()},
        "recommended": "Use 'auto' for automatic detection"
    }


@app.post("/ocr/extract", tags=["OCR"],
          summary="Extract data from a document image")
async def ocr_extract(
    file: UploadFile = File(..., description="Document image (JPG/PNG/PDF)"),
    doc_type: str = Form(default="auto", description="Document type hint")
):
    """
    Upload an image of an Indian government document (Aadhaar, PAN, etc.)
    and extract structured data from it.
    
    Returns extracted fields, normalized user profile, and confidence score.
    """
    # Validate file type
    content_type = file.content_type or ""
    if not any(ct in content_type for ct in ["image/", "application/pdf"]):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {content_type}. Upload JPG, PNG, or PDF."
        )
    
    image_bytes = await file.read()
    
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum size: 10MB"
        )
    
    # Run OCR
    ocr_result = extract_from_bytes(image_bytes, content_type, doc_type)
    
    if ocr_result.get("status") == "error":
        raise HTTPException(
            status_code=422,
            detail=f"OCR extraction failed: {ocr_result.get('error')}"
        )
    
    # Map to user profile
    user_profile = map_to_user_profile(ocr_result)
    
    return {
        "status": "success",
        "filename": file.filename,
        "document_type": ocr_result.get("document_type"),
        "confidence": ocr_result.get("confidence"),
        "extracted_fields": ocr_result.get("extracted_fields", {}),
        "user_profile": user_profile,
        "warnings": ocr_result.get("warnings", [])
    }


@app.post("/ocr/extract-and-fill", tags=["OCR"],
          summary="One-shot: Upload document → get prefilled form")
async def ocr_extract_and_fill(
    file: UploadFile = File(..., description="Document image (JPG/PNG/PDF)"),
    scheme_id: str = Form(..., description="Target scheme ID"),
    doc_type: str = Form(default="auto", description="Document type hint")
):
    """
    The flagship endpoint — single API call that:
    1. Takes a document image (Aadhaar/PAN/etc.)
    2. Runs Gemini Vision OCR to extract all data
    3. Maps extracted data to a pre-filled scheme application form
    4. Returns the form with auto-filled fields highlighted
    
    This is the WOW DEMO ENDPOINT.
    """
    content_type = file.content_type or "image/jpeg"
    image_bytes = await file.read()
    
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Max 10MB.")
    
    # Step 1: OCR
    ocr_result = extract_from_bytes(image_bytes, content_type, doc_type)
    
    if ocr_result.get("status") == "error":
        raise HTTPException(
            status_code=422,
            detail=f"OCR failed: {ocr_result.get('error')}"
        )
    
    # Step 2: Map to user profile
    user_profile = map_to_user_profile(ocr_result)
    
    # Step 3: Generate prefilled form
    form = generate_prefilled_form(scheme_id, user_profile)
    
    # Step 4: Build response
    auto_filled = form["auto_filled_count"]
    total = form["total_fields"]
    
    return {
        "pipeline": "ocr_to_form",
        "status": "success",
        "filename": file.filename,
        "document": {
            "type": ocr_result.get("document_type"),
            "confidence": ocr_result.get("confidence"),
            "warnings": ocr_result.get("warnings", [])
        },
        "user_profile": user_profile,
        "form": form,
        "summary": {
            "auto_filled": auto_filled,
            "total_fields": total,
            "fill_percentage": form["fill_percentage"],
            "missing_required": [
                f["label"] for f in form["fields"]
                if f.get("required") and not f.get("value")
            ]
        }
    }
