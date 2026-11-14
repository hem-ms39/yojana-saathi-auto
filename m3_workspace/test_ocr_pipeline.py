"""
Test the OCR → Form autofill pipeline end-to-end.
Run from the m3_workspace directory.
"""
import sys
import os
import json

# Add workspace to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.ocr_agent import run_ocr_pipeline, DOCUMENT_TYPES
from backend.agents.form_filler import generate_prefilled_form, list_available_forms


def test_ocr_with_image(image_path: str, doc_type: str = "auto"):
    """Test OCR extraction on an image file."""
    print(f"\n{'='*60}")
    print(f"TEST: OCR Extraction")
    print(f"Image : {image_path}")
    print(f"Type  : {doc_type}")
    print(f"{'='*60}")
    
    result = run_ocr_pipeline(image_path, doc_type)
    
    print(f"\nDocument Type : {result.get('document_type', 'unknown')}")
    print(f"Confidence    : {result.get('confidence', 0):.1%}")
    print(f"Autofill Ready: {result.get('autofill_ready')}")
    
    profile = result.get("user_profile", {})
    print(f"\nExtracted Profile:")
    for k, v in profile.items():
        if not k.startswith("_") and v:
            print(f"  {k:20s}: {v}")
    
    return result


def test_form_prefill(scheme_id: str, user_profile: dict):
    """Test form generation with a given profile."""
    print(f"\n{'='*60}")
    print(f"TEST: Form Prefill — {scheme_id}")
    print(f"{'='*60}")
    
    form = generate_prefilled_form(scheme_id, user_profile)
    
    print(f"\nForm Title    : {form['form_title']}")
    print(f"Auto-Filled   : {form['auto_filled_count']}/{form['total_fields']} ({form['fill_percentage']}%)")
    print(f"\nFields:")
    for f in form["fields"]:
        status = "[AUTO]" if f.get("auto_filled") else "[EMPTY]" if f.get("required") else "[opt] "
        value = str(f.get("value", ""))[:40] or "(empty)"
        print(f"  {status} {f['label']:30s}: {value}")
    
    return form


def test_full_pipeline(image_path: str, scheme_id: str, doc_type: str = "auto"):
    """Test the complete OCR → Form pipeline."""
    print(f"\n{'='*60}")
    print(f"FULL PIPELINE TEST")
    print(f"Image  : {image_path}")
    print(f"Scheme : {scheme_id}")
    print(f"{'='*60}")
    
    # Step 1: OCR
    ocr_result = run_ocr_pipeline(image_path, doc_type)
    user_profile = ocr_result.get("user_profile", {})
    
    # Step 2: Form
    form = generate_prefilled_form(scheme_id, user_profile)
    
    print(f"\nSUMMARY:")
    print(f"  Document Type : {ocr_result.get('document_type', 'unknown')}")
    print(f"  OCR Confidence: {ocr_result.get('confidence', 0):.1%}")
    print(f"  Form Fill Rate: {form['fill_percentage']}%")
    print(f"  Auto-filled   : {form['auto_filled_count']}/{form['total_fields']} fields")
    
    missing_required = [
        f["label"] for f in form["fields"]
        if f.get("required") and not f.get("value")
    ]
    if missing_required:
        print(f"\n  Still needs: {', '.join(missing_required)}")
    else:
        print(f"\n  All required fields filled!")
    
    return {"ocr": ocr_result, "form": form}


def test_mock_profiles():
    """Test form filling with the demo profiles (no image needed)."""
    print(f"\n{'='*60}")
    print("TEST: Demo Profile → Form Fill (No OCR)")
    print(f"{'='*60}")
    
    # Load demo profiles
    demo_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "backend", "data", "demo_profiles.json"
    )
    
    with open(demo_path, encoding="utf-8") as f:
        profiles = json.load(f)
    
    demo_scheme_map = {
        "demo-priya": ("pm-mudra-shishu", {
            "name": "Priya Sharma", "age": 22, "gender": "F",
            "state": "Karnataka", "district": "Bangalore Urban",
            "business_intent": "Tailoring", "aadhaar": "XXXX-XXXX-7842"
        }),
        "demo-ramesh": ("pm-fasal-bima", {
            "name": "Ramesh Kumar", "age": 45, "gender": "M",
            "state": "Uttar Pradesh"
        }),
        "demo-ananya": ("nsp-post-matric-sc", {
            "name": "Ananya R", "age": 19, "gender": "F",
            "state": "Karnataka", "district": "Mysore",
            "caste_category": "OBC"
        }),
    }
    
    for demo_id, (scheme_id, profile) in demo_scheme_map.items():
        print(f"\n--- {demo_id} → {scheme_id} ---")
        form = generate_prefilled_form(scheme_id, profile)
        print(f"  Fill: {form['fill_percentage']}% ({form['auto_filled_count']}/{form['total_fields']} fields)")


if __name__ == "__main__":
    print("\nYojana Saathi — M3 OCR Pipeline Test Suite")
    print("=" * 60)
    
    print(f"\nAvailable form templates: {list_available_forms()}")
    
    # Run demo profile tests (always works, no image needed)
    test_mock_profiles()
    
    # Run OCR test if image provided
    if len(sys.argv) >= 2:
        image_path = sys.argv[1]
        scheme_id = sys.argv[2] if len(sys.argv) > 2 else "pm-mudra-shishu"
        doc_type = sys.argv[3] if len(sys.argv) > 3 else "auto"
        
        if os.path.exists(image_path):
            test_full_pipeline(image_path, scheme_id, doc_type)
        else:
            print(f"\nImage not found: {image_path}")
    else:
        print(f"\nTo test with a real document image:")
        print(f"  python test_ocr_pipeline.py <image_path> [scheme_id] [doc_type]")
        print(f"  Example: python test_ocr_pipeline.py aadhaar.jpg pm-mudra-shishu aadhaar")
