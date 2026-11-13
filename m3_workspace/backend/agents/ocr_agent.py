"""
OCR Agent — Extracts structured data from Indian government ID documents
using Gemini 1.5 Flash Vision.

Supports:
- Aadhaar Card (Front + Back)
- PAN Card
- Ration Card
- Voter ID
- Driving License
- Passbook / Bank Statement
- Income Certificate
- Caste Certificate
"""
import base64
import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini 3 Flash Preview for document OCR.
model = genai.GenerativeModel("models/gemini-3-flash-preview")


# ─── Document Type Definitions ──────────────────────────────────────────────

DOCUMENT_TYPES = {
    "aadhaar": {
        "display_name": "Aadhaar Card",
        "extract_fields": [
            "name", "dob", "gender", "aadhaar_number",
            "address", "pincode", "district", "state"
        ],
    },
    "pan": {
        "display_name": "PAN Card",
        "extract_fields": [
            "name", "father_name", "dob", "pan_number"
        ],
    },
    "voter_id": {
        "display_name": "Voter ID Card",
        "extract_fields": [
            "name", "father_name", "dob", "gender",
            "voter_id_number", "address", "district", "state"
        ],
    },
    "driving_license": {
        "display_name": "Driving License",
        "extract_fields": [
            "name", "dob", "address", "dl_number",
            "pincode", "state", "gender"
        ],
    },
    "ration_card": {
        "display_name": "Ration Card",
        "extract_fields": [
            "name", "address", "district", "state",
            "ration_card_number", "category"
        ],
    },
    "income_certificate": {
        "display_name": "Income Certificate",
        "extract_fields": [
            "name", "annual_income", "district", "state",
            "certificate_number", "issued_date"
        ],
    },
    "caste_certificate": {
        "display_name": "Caste Certificate",
        "extract_fields": [
            "name", "caste", "caste_category", "district",
            "state", "certificate_number", "issued_date"
        ],
    },
    "passbook": {
        "display_name": "Bank Passbook",
        "extract_fields": [
            "name", "account_number", "bank_name",
            "branch", "ifsc", "address"
        ],
    },
    "auto": {
        "display_name": "Auto-Detect",
        "extract_fields": []  # Gemini will detect and extract all fields
    }
}


OCR_PROMPT = """You are an expert Indian government document OCR system. 
Carefully read the document image and extract ALL visible text fields.

Document type hint: {doc_type_hint}

Extract and return a JSON object with these fields (use null if a field is not visible or not applicable):

{{
  "document_type": "aadhaar|pan|voter_id|driving_license|ration_card|income_certificate|caste_certificate|passbook",
  "confidence": 0.0-1.0,
  "extracted_fields": {{
    "name": "Full name as printed",
    "name_hi": "Name in Hindi/regional script if present",
    "dob": "Date of birth in YYYY-MM-DD format",
    "age": integer or null,
    "gender": "M|F|Other",
    "aadhaar_number": "12-digit number (mask last 8 for privacy: XXXX-XXXX-1234)",
    "pan_number": "10 character PAN (e.g. ABCDE1234F)",
    "voter_id_number": "Voter ID number",
    "dl_number": "Driving license number",
    "ration_card_number": "Ration card number",
    "father_name": "Father's name",
    "mother_name": "Mother's name",
    "address": "Full address as printed",
    "pincode": "6-digit pincode",
    "district": "District name",
    "state": "State name",
    "bank_name": "Bank name",
    "account_number": "Bank account number",
    "ifsc": "IFSC code",
    "branch": "Bank branch name",
    "annual_income": integer in INR or null,
    "caste": "Caste name",
    "caste_category": "SC|ST|OBC|General|EWS",
    "certificate_number": "Certificate/document number",
    "issued_date": "Issue date in YYYY-MM-DD format",
    "issued_by": "Authority that issued the document"
  }},
  "raw_text": "All visible text from the document as a single string",
  "warnings": ["any issues like poor image quality, partial visibility, etc."]
}}

RULES:
- Extract ONLY what is clearly visible in the image
- For Aadhaar numbers, show only last 4 digits (privacy protection)
- Convert regional dates (DD/MM/YYYY) to YYYY-MM-DD format
- Normalize gender to M/F/Other
- Capitalize state and district names properly
- If this is not an Indian government document, set document_type to "unknown"
- Return ONLY valid JSON, no explanation, no markdown

"""


def image_to_base64(image_path: str) -> tuple[str, str]:
    """Convert image file to base64 string and detect MIME type."""
    path = Path(image_path)
    ext = path.suffix.lower()
    
    mime_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".heic": "image/heic",
        ".pdf": "application/pdf",
    }
    mime_type = mime_map.get(ext, "image/jpeg")
    
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    
    return data, mime_type


def extract_from_image(image_path: str, doc_type: str = "auto") -> dict:
    """
    Extract structured data from a document image using Gemini Vision.
    
    Args:
        image_path: Path to the document image (JPG/PNG/PDF)
        doc_type: Document type hint: "aadhaar", "pan", "auto", etc.
    
    Returns:
        dict with extracted fields, confidence score, and raw text
    """
    doc_type_hint = DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["auto"])["display_name"]
    prompt = OCR_PROMPT.format(doc_type_hint=doc_type_hint)
    
    try:
        image_data, mime_type = image_to_base64(image_path)
        
        response = model.generate_content([
            prompt,
            {"mime_type": mime_type, "data": image_data}
        ])
        
        text = response.text.strip()
        
        # Strip markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(text)
        result["source_file"] = Path(image_path).name
        result["status"] = "success"
        return result
        
    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "error": f"JSON parse error: {str(e)}",
            "raw_response": response.text if 'response' in locals() else None,
            "source_file": Path(image_path).name
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "source_file": Path(image_path).name
        }


def extract_from_bytes(image_bytes: bytes, mime_type: str = "image/jpeg", 
                       doc_type: str = "auto") -> dict:
    """
    Extract structured data from image bytes (for API usage).
    
    Args:
        image_bytes: Raw image bytes
        mime_type: MIME type of the image
        doc_type: Document type hint
    """
    doc_type_hint = DOCUMENT_TYPES.get(doc_type, DOCUMENT_TYPES["auto"])["display_name"]
    prompt = OCR_PROMPT.format(doc_type_hint=doc_type_hint)
    
    try:
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        
        response = model.generate_content([
            prompt,
            {"mime_type": mime_type, "data": image_data}
        ])
        
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(text)
        result["status"] = "success"
        return result
        
    except json.JSONDecodeError:
        return {
            "status": "error",
            "error": "Could not parse Gemini response as JSON",
            "raw_response": response.text if 'response' in locals() else None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def map_to_user_profile(ocr_result: dict) -> dict:
    """
    Convert OCR-extracted fields into a normalized user profile dict
    that matches the format expected by form_filler.py and M1 agents.
    """
    if ocr_result.get("status") != "success":
        return {}
    
    fields = ocr_result.get("extracted_fields", {})
    
    profile = {}
    
    # Basic identity
    if fields.get("name"):
        profile["name"] = fields["name"]
    if fields.get("dob"):
        profile["dob"] = fields["dob"]
        # Calculate age from DOB
        try:
            from datetime import date
            dob_parts = fields["dob"].split("-")
            birth_year = int(dob_parts[0])
            birth_month = int(dob_parts[1])
            birth_day = int(dob_parts[2])
            today = date.today()
            age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day))
            profile["age"] = age
        except:
            pass
    
    if fields.get("age") and "age" not in profile:
        profile["age"] = fields["age"]
    if fields.get("gender"):
        profile["gender"] = fields["gender"]
    
    # Location
    if fields.get("state"):
        profile["state"] = fields["state"]
    if fields.get("district"):
        profile["district"] = fields["district"]
    if fields.get("pincode"):
        profile["pincode"] = fields["pincode"]
    if fields.get("address"):
        profile["address"] = fields["address"]
    
    # Document IDs (for form prefill)
    if fields.get("aadhaar_number"):
        profile["aadhaar"] = fields["aadhaar_number"]
    if fields.get("pan_number"):
        profile["pan"] = fields["pan_number"]
    
    # Financial/Social
    if fields.get("annual_income"):
        profile["annual_income"] = fields["annual_income"]
    if fields.get("caste_category"):
        profile["caste_category"] = fields["caste_category"]
    if fields.get("caste"):
        profile["caste"] = fields["caste"]
    
    # Family
    if fields.get("father_name"):
        profile["father_name"] = fields["father_name"]
    
    # Bank details
    if fields.get("bank_name"):
        profile["bank_name"] = fields["bank_name"]
    if fields.get("account_number"):
        profile["bank_account"] = fields["account_number"]
    if fields.get("ifsc"):
        profile["ifsc"] = fields["ifsc"]
    
    # Document metadata
    profile["_doc_type"] = ocr_result.get("document_type", "unknown")
    profile["_ocr_confidence"] = ocr_result.get("confidence", 0.0)
    
    return profile


def run_ocr_pipeline(image_path: str, doc_type: str = "auto") -> dict:
    """
    Full pipeline: image → OCR → user profile.
    
    Returns:
        {
          "ocr_result": {...},        # Raw extraction
          "user_profile": {...},      # Normalized profile for form filling
          "autofill_ready": bool,     # Whether we have enough data to autofill
          "missing_fields": [...]     # What we couldn't extract
        }
    """
    print(f"[OCR] Processing: {image_path} (type={doc_type})")
    
    ocr_result = extract_from_image(image_path, doc_type)
    
    if ocr_result.get("status") != "success":
        return {
            "ocr_result": ocr_result,
            "user_profile": {},
            "autofill_ready": False,
            "missing_fields": ["all - OCR failed"]
        }
    
    user_profile = map_to_user_profile(ocr_result)
    
    # Determine autofill readiness
    critical_fields = ["name", "state"]
    present = [f for f in critical_fields if user_profile.get(f)]
    missing = [f for f in critical_fields if not user_profile.get(f)]
    
    return {
        "ocr_result": ocr_result,
        "user_profile": user_profile,
        "autofill_ready": len(missing) == 0,
        "present_fields": present,
        "missing_fields": missing,
        "document_type": ocr_result.get("document_type", "unknown"),
        "confidence": ocr_result.get("confidence", 0.0)
    }


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ocr_agent.py <image_path> [doc_type]")
        print("doc_type options: aadhaar, pan, voter_id, driving_license, auto")
        sys.exit(1)
    
    image_path = sys.argv[1]
    doc_type = sys.argv[2] if len(sys.argv) > 2 else "auto"
    
    result = run_ocr_pipeline(image_path, doc_type)
    
    print("\n=== OCR RESULT ===")
    print(f"Document Type : {result['document_type']}")
    print(f"Confidence    : {result['confidence']:.1%}")
    print(f"Autofill Ready: {result['autofill_ready']}")
    print(f"\n=== EXTRACTED USER PROFILE ===")
    for k, v in result["user_profile"].items():
        if not k.startswith("_"):
            print(f"  {k:20s}: {v}")
    
    if result["missing_fields"]:
        print(f"\nMissing: {result['missing_fields']}")
