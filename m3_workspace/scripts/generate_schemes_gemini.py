"""
Generate real Indian government scheme data using Gemini API.
This replaces the broken scraper with AI-curated, accurate scheme records.
"""
import json
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")

SCHEME_BATCHES = [
    {
        "category": "Business & Entrepreneurship Loans",
        "schemes": [
            "PM MUDRA Yojana - Shishu (up to ₹50,000)",
            "PM MUDRA Yojana - Kishore (₹50,000 to ₹5 lakh)",
            "PM MUDRA Yojana - Tarun (₹5 lakh to ₹10 lakh)",
            "Prime Minister's Employment Generation Programme (PMEGP)",
            "Stand-Up India Scheme",
            "Startup India Seed Fund Scheme",
            "Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
            "PM Vishwakarma Yojana",
        ]
    },
    {
        "category": "Women Entrepreneurship & Empowerment",
        "schemes": [
            "Mahila Udyam Nidhi Scheme",
            "Annapurna Scheme for Women",
            "Stree Shakti Package for Women Entrepreneurs",
            "Mahila Samman Savings Certificate",
            "PM Matru Vandana Yojana",
            "Working Women Hostel Scheme",
        ]
    },
    {
        "category": "Scholarships & Education",
        "schemes": [
            "National Scholarship Portal - Post-Matric Scholarship for SC Students",
            "National Scholarship Portal - Post-Matric Scholarship for OBC Students",
            "Central Sector Scheme of Scholarships for College and University Students",
            "PM Research Fellowship (PMRF)",
            "AICTE Pragati Scholarship for Girls",
            "National Means-cum-Merit Scholarship (NMMSS)",
            "Ishan Uday Special Scholarship for North Eastern Region",
            "Begum Hazrat Mahal National Scholarship for Minority Girls",
        ]
    },
    {
        "category": "Agriculture & Farmer Welfare",
        "schemes": [
            "PM-KISAN Samman Nidhi (₹6,000/year)",
            "Pradhan Mantri Fasal Bima Yojana (Crop Insurance)",
            "Kisan Credit Card (KCC)",
            "PM Krishi Sinchayee Yojana (Irrigation)",
            "Soil Health Card Scheme",
            "National Mission on Sustainable Agriculture",
            "Agriculture Infrastructure Fund",
        ]
    },
    {
        "category": "Housing & Urban Development",
        "schemes": [
            "PM Awas Yojana - Urban (PMAY-U)",
            "PM Awas Yojana - Gramin (PMAY-G)",
            "Deendayal Antyodaya Yojana - National Urban Livelihoods Mission (DAY-NULM)",
            "PM SVANidhi (Street Vendor Loan)",
        ]
    },
    {
        "category": "Skill Development & Employment",
        "schemes": [
            "PM Kaushal Vikas Yojana (PMKVY)",
            "Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)",
            "National Apprenticeship Promotion Scheme (NAPS)",
            "PM Daksh Yojana for SC/OBC/Minorities",
        ]
    },
    {
        "category": "Healthcare & Social Security",
        "schemes": [
            "Ayushman Bharat - PM Jan Arogya Yojana (₹5 lakh health cover)",
            "PM Suraksha Bima Yojana (Accident Insurance ₹12/year)",
            "PM Jeevan Jyoti Bima Yojana (Life Insurance ₹436/year)",
            "Atal Pension Yojana",
            "National Family Benefit Scheme",
        ]
    },
    {
        "category": "MSME & Industry",
        "schemes": [
            "MSME Zero Defect Zero Effect (ZED) Certification",
            "SFURTI (Scheme of Fund for Regeneration of Traditional Industries)",
            "ASPIRE (Scheme for Promotion of Innovation in Rural Economy)",
            "Udyam Registration (MSME Registration)",
            "Technology Upgradation Fund Scheme (TUFS) for Textiles",
            "National SC-ST Hub Scheme",
        ]
    },
]

GENERATION_PROMPT = """You are a government scheme data expert for India. Generate accurate, real data for the following Indian government schemes.

For EACH scheme, output a JSON object with these EXACT fields:
{{
  "scheme_id": "lowercase-hyphenated-short-id",
  "title": "Official English name",
  "title_hi": "Hindi name in Devanagari script",
  "title_kn": "Kannada name in Kannada script",
  "description": "2-3 sentence accurate description of what the scheme provides",
  "eligibility_text": "Detailed eligibility criteria as written in official documents. Include age limits, income limits, caste requirements, gender requirements, etc.",
  "benefits_text": "What the beneficiary gets — loan amount, subsidy percentage, cash transfer amount, etc.",
  "funding_amount": <integer in INR — the maximum amount a single beneficiary can receive. Use null if not applicable>,
  "category": ["list", "of", "relevant", "categories"],
  "target_group": ["list", "of", "target", "demographics"],
  "ministry": "Full name of the ministry that runs this scheme",
  "state": "all" for central schemes, or specific state name,
  "min_age": <minimum age as integer or null>,
  "max_age": <maximum age as integer or null>,
  "max_income": <annual income ceiling in INR as integer or null>,
  "documents_required": ["list", "of", "required", "documents"],
  "application_url": "Official URL to apply",
  "deadline": "2026-03-31" or null if ongoing,
  "application_steps": ["Step 1: ...", "Step 2: ...", "Step 3: ..."]
}}

RULES:
- Use REAL, ACCURATE data from official Indian government sources
- funding_amount must be an integer (not string). For PM-KISAN it's 6000, for MUDRA Shishu it's 50000, etc.
- Include realistic eligibility criteria with actual numbers (income limits, age limits)
- category values should be from: entrepreneurship, business_loan, msme, women, scholarship, education, agriculture, farmer, housing, healthcare, skill_development, social_security, insurance, minority, sc_st, obc
- target_group values should be from: youth, women, farmer, student, sc_st, obc, minority, senior_citizen, small_business, startup, bpl, urban_poor, rural, disabled, all
- documents_required should use: aadhaar, pan, bank_passbook, income_certificate, caste_certificate, domicile_certificate, education_certificate, business_plan, land_documents, passport_photo, ration_card, voter_id, gst_certificate

Generate schemes for this batch:
Category: {category}
Schemes: {schemes}

Output ONLY a JSON array. No markdown, no explanation, no code blocks. Just the raw JSON array.
"""


def generate_batch(category: str, scheme_names: list[str]) -> list[dict]:
    """Generate a batch of scheme data using Gemini."""
    prompt = GENERATION_PROMPT.format(
        category=category,
        schemes="\n".join(f"- {s}" for s in scheme_names)
    )
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean up potential markdown code block wrapping
        if text.startswith("```"):
            text = text.split("\n", 1)[1]  # Remove first line
            if text.endswith("```"):
                text = text[:-3]
            elif "```" in text:
                text = text[:text.rfind("```")]
        
        schemes = json.loads(text)
        print(f"  ✅ Generated {len(schemes)} schemes for '{category}'")
        return schemes
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON parse error for '{category}': {e}")
        # Try to salvage partial JSON
        try:
            # Find the last complete object
            last_bracket = text.rfind("]")
            if last_bracket > 0:
                schemes = json.loads(text[:last_bracket + 1])
                print(f"  ⚠️  Salvaged {len(schemes)} schemes")
                return schemes
        except:
            pass
        print(f"  Raw response preview: {text[:200]}...")
        return []
    except Exception as e:
        print(f"  ❌ Gemini error for '{category}': {e}")
        return []


def validate_scheme(scheme: dict) -> dict:
    """Validate and fix a single scheme record."""
    # Ensure scheme_id
    if not scheme.get("scheme_id"):
        scheme["scheme_id"] = scheme.get("title", "unknown").lower().replace(" ", "-")[:50]
    
    # Ensure funding_amount is int or None
    fa = scheme.get("funding_amount")
    if isinstance(fa, str):
        fa = fa.replace("₹", "").replace(",", "").strip()
        try:
            scheme["funding_amount"] = int(float(fa))
        except:
            scheme["funding_amount"] = None
    elif isinstance(fa, float):
        scheme["funding_amount"] = int(fa)
    
    # Ensure lists are lists
    for field in ["category", "target_group", "documents_required", "application_steps"]:
        if not isinstance(scheme.get(field), list):
            scheme[field] = []
    
    # Ensure string fields
    for field in ["title", "description", "eligibility_text", "benefits_text",
                   "ministry", "state", "application_url"]:
        if not scheme.get(field):
            scheme[field] = ""
    
    # Ensure state is lowercase
    scheme["state"] = scheme.get("state", "all").lower()
    
    # Ensure age fields are int or None
    for field in ["min_age", "max_age", "max_income"]:
        val = scheme.get(field)
        if val is not None:
            try:
                scheme[field] = int(val)
            except:
                scheme[field] = None
    
    # Build full_text for embedding
    scheme["full_text"] = (
        f"{scheme['title']}. {scheme.get('title_hi', '')}. {scheme.get('title_kn', '')}. "
        f"{scheme['description']} "
        f"Eligibility: {scheme['eligibility_text']} "
        f"Benefits: {scheme['benefits_text']} "
        f"Target: {', '.join(scheme['target_group'])}. "
        f"Category: {', '.join(scheme['category'])}. "
        f"Ministry: {scheme['ministry']}. "
        f"Documents: {', '.join(scheme['documents_required'])}."
    )
    
    return scheme


def main():
    os.makedirs("../data/processed", exist_ok=True)
    
    all_schemes = []
    
    for batch in SCHEME_BATCHES:
        print(f"\n📦 Generating: {batch['category']} ({len(batch['schemes'])} schemes)")
        schemes = generate_batch(batch["category"], batch["schemes"])
        
        for s in schemes:
            validated = validate_scheme(s)
            all_schemes.append(validated)
        
        time.sleep(2)  # Rate limit courtesy
    
    # Deduplicate by scheme_id
    seen = set()
    unique = []
    for s in all_schemes:
        if s["scheme_id"] not in seen:
            seen.add(s["scheme_id"])
            unique.append(s)
    
    output_path = "../data/processed/seed_schemes.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
    
    # Also copy to backend/data for M1/M4 access
    backend_path = "../m3_workspace/backend/data/seed_schemes.json"
    os.makedirs(os.path.dirname(backend_path), exist_ok=True)
    with open(backend_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Total schemes generated: {len(unique)}")
    print(f"📁 Saved to: {output_path}")
    print(f"📁 Copied to: {backend_path}")
    
    # Print category distribution
    from collections import Counter
    cats = Counter()
    for s in unique:
        for c in s.get("category", []):
            cats[c] += 1
    print(f"\n📊 Category distribution:")
    for cat, count in cats.most_common():
        print(f"   {cat}: {count}")


if __name__ == "__main__":
    main()
