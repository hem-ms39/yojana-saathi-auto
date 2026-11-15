from backend.agents.ocr_agent import map_to_user_profile


def test_failed_ocr_maps_to_empty_profile():
    assert map_to_user_profile({"status": "error"}) == {}


def test_successful_ocr_maps_fields_and_computes_age():
    profile = map_to_user_profile(
        {
            "status": "success",
            "document_type": "aadhaar",
            "confidence": 0.9,
            "extracted_fields": {"name": "Ravi", "dob": "2000-01-01", "aadhaar_number": "XXXX"},
        }
    )
    assert profile["name"] == "Ravi"
    assert profile["age"] >= 25
    assert profile["aadhaar"] == "XXXX"
    assert profile["_doc_type"] == "aadhaar"
