"""
Updated form_filler.py — Now supports OCR-extracted profile data.
Expanded templates for all demo paths.
"""
from typing import Optional

# ─── Form Templates ────────────────────────────────────────────────────────

FORM_TEMPLATES = {
    "pm-mudra-shishu": {
        "form_title": "MUDRA Loan Application - Shishu (Up to ₹50,000)",
        "ministry": "Ministry of Finance",
        "apply_url": "https://www.mudra.org.in/",
        "fields": [
            {"label": "Full Name",              "key": "name",            "type": "text",     "required": True},
            {"label": "Date of Birth",           "key": "dob",             "type": "date",     "required": True},
            {"label": "Age",                     "key": "age",             "type": "number",   "required": False},
            {"label": "Gender",                  "key": "gender",          "type": "select",   "required": True,
             "options": ["Male", "Female", "Other"]},
            {"label": "Aadhaar Number",          "key": "aadhaar",         "type": "text",     "required": True},
            {"label": "PAN Number",              "key": "pan",             "type": "text",     "required": False},
            {"label": "State",                   "key": "state",           "type": "text",     "required": True},
            {"label": "District",                "key": "district",        "type": "text",     "required": True},
            {"label": "Address",                 "key": "address",         "type": "textarea", "required": True},
            {"label": "Pincode",                 "key": "pincode",         "type": "text",     "required": True},
            {"label": "Business Type",           "key": "business_intent", "type": "text",     "required": True},
            {"label": "Loan Amount Requested (₹)","key": "loan_amount",   "type": "number",   "required": True,
             "default": 50000, "max": 50000},
            {"label": "Bank Name",               "key": "bank_name",       "type": "text",     "required": True},
            {"label": "Bank Account Number",     "key": "bank_account",    "type": "text",     "required": True},
            {"label": "IFSC Code",              "key": "ifsc",            "type": "text",     "required": True},
        ]
    },
    "pm-mudra-kishore": {
        "form_title": "MUDRA Loan Application - Kishore (₹50,000–₹5 Lakh)",
        "ministry": "Ministry of Finance",
        "apply_url": "https://www.mudra.org.in/",
        "fields": [
            {"label": "Full Name",              "key": "name",            "type": "text",     "required": True},
            {"label": "Date of Birth",           "key": "dob",             "type": "date",     "required": True},
            {"label": "Gender",                  "key": "gender",          "type": "select",   "required": True,
             "options": ["Male", "Female", "Other"]},
            {"label": "Aadhaar Number",          "key": "aadhaar",         "type": "text",     "required": True},
            {"label": "PAN Number",              "key": "pan",             "type": "text",     "required": True},
            {"label": "State",                   "key": "state",           "type": "text",     "required": True},
            {"label": "District",                "key": "district",        "type": "text",     "required": True},
            {"label": "Business Type",           "key": "business_intent", "type": "text",     "required": True},
            {"label": "Existing Business Age",   "key": "business_age",    "type": "text",     "required": False},
            {"label": "Annual Turnover (₹)",     "key": "annual_turnover", "type": "number",   "required": False},
            {"label": "Loan Amount Requested (₹)","key": "loan_amount",   "type": "number",   "required": True,
             "default": 200000, "max": 500000},
            {"label": "Bank Name",               "key": "bank_name",       "type": "text",     "required": True},
            {"label": "Bank Account Number",     "key": "bank_account",    "type": "text",     "required": True},
        ]
    },
    "pmegp": {
        "form_title": "Prime Minister's Employment Generation Programme (PMEGP)",
        "ministry": "Ministry of MSME",
        "apply_url": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp",
        "fields": [
            {"label": "Full Name",                "key": "name",            "type": "text",     "required": True},
            {"label": "Date of Birth",             "key": "dob",             "type": "date",     "required": True},
            {"label": "Age",                       "key": "age",             "type": "number",   "required": True},
            {"label": "Gender",                    "key": "gender",          "type": "select",   "required": True,
             "options": ["Male", "Female", "Transgender"]},
            {"label": "Category",                  "key": "caste_category",  "type": "select",   "required": True,
             "options": ["General", "SC", "ST", "OBC", "Minority", "Women", "Ex-Serviceman", "PH"]},
            {"label": "Education Qualification",   "key": "education",       "type": "select",   "required": True,
             "options": ["Below 8th", "8th Pass", "10th Pass", "12th Pass", "Graduate", "Post Graduate"]},
            {"label": "Aadhaar Number",            "key": "aadhaar",         "type": "text",     "required": True},
            {"label": "PAN Number",                "key": "pan",             "type": "text",     "required": False},
            {"label": "State",                     "key": "state",           "type": "text",     "required": True},
            {"label": "District",                  "key": "district",        "type": "text",     "required": True},
            {"label": "Project/Business Name",     "key": "business_intent", "type": "text",     "required": True},
            {"label": "Project Sector",            "key": "project_sector",  "type": "select",   "required": True,
             "options": ["Manufacturing", "Service", "Trading"]},
            {"label": "Estimated Project Cost (₹)","key": "project_cost",    "type": "number",   "required": True},
            {"label": "Bank Name",                 "key": "bank_name",       "type": "text",     "required": True},
        ]
    },
    "stand-up-india": {
        "form_title": "Stand-Up India Scheme Application",
        "ministry": "Ministry of Finance",
        "apply_url": "https://www.standupmitra.in/",
        "fields": [
            {"label": "Full Name",              "key": "name",            "type": "text",     "required": True},
            {"label": "Date of Birth",           "key": "dob",             "type": "date",     "required": True},
            {"label": "Gender",                  "key": "gender",          "type": "select",   "required": True,
             "options": ["Male", "Female", "Other"]},
            {"label": "Category",                "key": "caste_category",  "type": "select",   "required": True,
             "options": ["SC", "ST", "Women (Other)"]},
            {"label": "Aadhaar Number",          "key": "aadhaar",         "type": "text",     "required": True},
            {"label": "PAN Number",              "key": "pan",             "type": "text",     "required": True},
            {"label": "State",                   "key": "state",           "type": "text",     "required": True},
            {"label": "District",                "key": "district",        "type": "text",     "required": True},
            {"label": "Nature of Enterprise",    "key": "business_intent", "type": "text",     "required": True},
            {"label": "Project Cost (₹)",        "key": "project_cost",    "type": "number",   "required": True},
            {"label": "Bank Name",               "key": "bank_name",       "type": "text",     "required": True},
            {"label": "Bank Account Number",     "key": "bank_account",    "type": "text",     "required": True},
            {"label": "IFSC Code",              "key": "ifsc",            "type": "text",     "required": True},
        ]
    },
    "nsp-post-matric-sc": {
        "form_title": "Post-Matric Scholarship for SC Students",
        "ministry": "Ministry of Social Justice and Empowerment",
        "apply_url": "https://scholarships.gov.in/",
        "fields": [
            {"label": "Student Full Name",       "key": "name",            "type": "text",     "required": True},
            {"label": "Date of Birth",           "key": "dob",             "type": "date",     "required": True},
            {"label": "Gender",                  "key": "gender",          "type": "select",   "required": True,
             "options": ["Male", "Female", "Transgender"]},
            {"label": "Caste",                   "key": "caste",           "type": "text",     "required": True},
            {"label": "Aadhaar Number",          "key": "aadhaar",         "type": "text",     "required": True},
            {"label": "State",                   "key": "state",           "type": "text",     "required": True},
            {"label": "District",                "key": "district",        "type": "text",     "required": True},
            {"label": "Institute Name",          "key": "institute",       "type": "text",     "required": True},
            {"label": "Course Name",             "key": "course",          "type": "text",     "required": True},
            {"label": "Year of Study",           "key": "year_of_study",   "type": "select",   "required": True,
             "options": ["1st Year", "2nd Year", "3rd Year", "4th Year"]},
            {"label": "Parent/Guardian Name",    "key": "father_name",     "type": "text",     "required": True},
            {"label": "Annual Family Income (₹)","key": "annual_income",   "type": "number",   "required": True},
            {"label": "Bank Account Number",     "key": "bank_account",    "type": "text",     "required": True},
            {"label": "Bank Name",               "key": "bank_name",       "type": "text",     "required": True},
            {"label": "IFSC Code",              "key": "ifsc",            "type": "text",     "required": True},
        ]
    },
    "pm-fasal-bima": {
        "form_title": "Pradhan Mantri Fasal Bima Yojana (Crop Insurance)",
        "ministry": "Ministry of Agriculture",
        "apply_url": "https://pmfby.gov.in/",
        "fields": [
            {"label": "Farmer Name",             "key": "name",            "type": "text",     "required": True},
            {"label": "Date of Birth",           "key": "dob",             "type": "date",     "required": True},
            {"label": "Aadhaar Number",          "key": "aadhaar",         "type": "text",     "required": True},
            {"label": "State",                   "key": "state",           "type": "text",     "required": True},
            {"label": "District",                "key": "district",        "type": "text",     "required": True},
            {"label": "Village",                 "key": "village",         "type": "text",     "required": True},
            {"label": "Season",                  "key": "season",          "type": "select",   "required": True,
             "options": ["Kharif", "Rabi", "Annual"]},
            {"label": "Crop Name",               "key": "crop_name",       "type": "text",     "required": True},
            {"label": "Land Area (in Hectares)", "key": "land_area",       "type": "number",   "required": True},
            {"label": "Bank Account Number",     "key": "bank_account",    "type": "text",     "required": True},
            {"label": "Bank Name",               "key": "bank_name",       "type": "text",     "required": True},
        ]
    },
    "ayushman-bharat": {
        "form_title": "Ayushman Bharat PM-JAY Enrollment",
        "ministry": "Ministry of Health and Family Welfare",
        "apply_url": "https://beneficiary.nha.gov.in/",
        "fields": [
            {"label": "Full Name",              "key": "name",            "type": "text",     "required": True},
            {"label": "Date of Birth",           "key": "dob",             "type": "date",     "required": True},
            {"label": "Gender",                  "key": "gender",          "type": "select",   "required": True,
             "options": ["Male", "Female", "Other"]},
            {"label": "Aadhaar Number",          "key": "aadhaar",         "type": "text",     "required": True},
            {"label": "Ration Card Number",      "key": "ration_card_number","type": "text",   "required": False},
            {"label": "State",                   "key": "state",           "type": "text",     "required": True},
            {"label": "District",                "key": "district",        "type": "text",     "required": True},
        ]
    },
    "pmkvy": {
        "form_title": "PM Kaushal Vikas Yojana (Skill Training) Registration",
        "ministry": "Ministry of Skill Development",
        "apply_url": "https://www.pmkvyofficial.org/",
        "fields": [
            {"label": "Full Name",              "key": "name",            "type": "text",     "required": True},
            {"label": "Date of Birth",           "key": "dob",             "type": "date",     "required": True},
            {"label": "Gender",                  "key": "gender",          "type": "select",   "required": True,
             "options": ["Male", "Female", "Transgender"]},
            {"label": "Aadhaar Number",          "key": "aadhaar",         "type": "text",     "required": True},
            {"label": "State",                   "key": "state",           "type": "text",     "required": True},
            {"label": "District",                "key": "district",        "type": "text",     "required": True},
            {"label": "Education Qualification", "key": "education",       "type": "select",   "required": True,
             "options": ["Below 8th", "8th Pass", "10th Pass", "12th Pass", "Graduate"]},
            {"label": "Preferred Skill/Trade",   "key": "business_intent", "type": "text",     "required": True},
            {"label": "Mobile Number",           "key": "mobile",          "type": "text",     "required": True},
        ]
    }
}


# ─── Core Form Functions ────────────────────────────────────────────────────

def generate_prefilled_form(scheme_id: str, user_profile: dict) -> dict:
    """
    Generate a pre-filled form for a scheme using user profile data.
    Works with both manually entered profiles and OCR-extracted profiles.
    
    Args:
        scheme_id: The scheme identifier (e.g. "pm-mudra-shishu")
        user_profile: Dict of user data (from OCR, voice agent, or manual input)
    
    Returns:
        Form dict with fields pre-filled wherever possible
    """
    template = FORM_TEMPLATES.get(scheme_id)
    if not template:
        # Return a generic empty form if template not found
        return {
            "form_title": f"Application Form",
            "scheme_id": scheme_id,
            "fields": [],
            "auto_filled_count": 0,
            "total_fields": 0,
            "error": f"No form template found for scheme: {scheme_id}",
            "available_schemes": list(FORM_TEMPLATES.keys())
        }
    
    filled_fields = []
    for field in template["fields"]:
        key = field["key"]
        
        # Try direct key match first
        value = user_profile.get(key, "")
        
        # Try gender normalization
        if key == "gender" and value:
            gender_map = {"M": "Male", "F": "Female", "male": "Male", "female": "Female"}
            value = gender_map.get(value, value)
        
        # Use field default if no user value
        if not value and field.get("default"):
            value = field["default"]
        
        filled_fields.append({
            **field,
            "value": value,
            "auto_filled": bool(value and value != field.get("default", ""))
        })
    
    auto_filled = sum(1 for f in filled_fields if f.get("auto_filled"))
    total = len(filled_fields)
    
    return {
        "form_title": template["form_title"],
        "scheme_id": scheme_id,
        "ministry": template.get("ministry", ""),
        "apply_url": template.get("apply_url", ""),
        "fields": filled_fields,
        "auto_filled_count": auto_filled,
        "total_fields": total,
        "fill_percentage": round((auto_filled / total) * 100) if total > 0 else 0,
        "ocr_source": user_profile.get("_doc_type"),
        "ocr_confidence": user_profile.get("_ocr_confidence"),
    }


def get_form_template(scheme_id: str) -> Optional[dict]:
    """Return the raw form template for a given scheme_id."""
    return FORM_TEMPLATES.get(scheme_id)


def list_available_forms() -> list[str]:
    """Return all scheme IDs that have form templates."""
    return list(FORM_TEMPLATES.keys())


# ─── OCR → Form Full Pipeline ───────────────────────────────────────────────

def ocr_to_form(image_path: str, scheme_id: str, doc_type: str = "auto") -> dict:
    """
    Full one-shot pipeline: document image → OCR → prefilled form.
    
    Args:
        image_path: Path to the document image
        scheme_id: Target scheme to fill the form for
        doc_type: Document type hint ("aadhaar", "pan", "auto", etc.)
    
    Returns:
        Combined result with OCR data + prefilled form
    """
    # Import here to avoid circular imports
    from backend.agents.ocr_agent import run_ocr_pipeline
    
    ocr_result = run_ocr_pipeline(image_path, doc_type)
    user_profile = ocr_result.get("user_profile", {})
    form = generate_prefilled_form(scheme_id, user_profile)
    
    return {
        "pipeline": "ocr_to_form",
        "document_type": ocr_result.get("document_type"),
        "ocr_confidence": ocr_result.get("confidence"),
        "autofill_ready": ocr_result.get("autofill_ready"),
        "user_profile": user_profile,
        "form": form,
        "fill_summary": {
            "total_fields": form["total_fields"],
            "auto_filled": form["auto_filled_count"],
            "fill_percentage": form["fill_percentage"],
            "missing_fields": [
                f["label"] for f in form["fields"]
                if f["required"] and not f.get("value")
            ]
        }
    }
