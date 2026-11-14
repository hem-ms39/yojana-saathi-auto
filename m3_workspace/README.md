# M3 Workspace — Setup & Integration Guide

## What This Module Does

M3 is the **Data + Action Lead** for Yojana Saathi. It owns:
1. The **scheme knowledge base** (48 real Indian government schemes in Qdrant)
2. The **OCR pipeline** (Gemini Vision extracts data from Aadhaar/PAN/etc.)
3. The **form autofill API** (pre-fills scheme application forms from user data)

Every other module depends on this. Without M3, nothing works.

---

## Folder Structure

```
d:\DeepStation\m3_workspace\
├── .env                          ← API keys (DO NOT COMMIT)
├── .env.example                  ← Template for teammates
├── .gitignore
├── requirements.txt
│
├── scripts/
│   ├── generate_schemes_gemini.py ← Generates real scheme data via Gemini
│   ├── embed_schemes.py           ← Embeds schemes + uploads to Qdrant
│   ├── clean_schemes.py           ← Cleans raw scraped data
│   └── scrape_schemes.py          ← (Legacy) MyScheme.gov.in scraper
│
├── backend/
│   ├── agents/
│   │   ├── ocr_agent.py           ← Gemini Vision OCR for ID documents
│   │   └── form_filler.py         ← Form prefill logic (8 scheme templates)
│   ├── api/
│   │   └── main.py                ← FastAPI server (port 8001)
│   └── data/
│       ├── seed_schemes.json      ← ★ 48 real schemes (key deliverable)
│       └── demo_profiles.json     ← 5 demo user profiles
│
├── data/
│   ├── raw/                       ← Raw data (gitignored)
│   └── processed/
│       └── seed_schemes.json      ← Source of truth for embeddings
│
├── test_ocr_pipeline.py           ← OCR pipeline test suite
└── test_api.py                    ← API endpoint tests
```

---

## Prerequisites

- Python 3.10+
- Git
- Access to the shared `.env` values (get from team lead)

---

## Step 1 — Clone & Setup

```powershell
# Clone the repo
git clone <repo-url>
cd DeepStation

# Create virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\Activate.ps1

# Install M3 dependencies
pip install -r m3_workspace\requirements.txt
```

---

## Step 2 — Configure Environment

Copy `.env.example` to `.env` and fill in your keys:

```powershell
copy m3_workspace\.env.example m3_workspace\.env
```

Edit `m3_workspace\.env`:

```env
# LLM APIs
OPENAI_API_KEY=sk-...          # (optional, OpenAI quota may be exhausted)
GROQ_API_KEY=gsk_...           # For M1 agents
GEMINI_API_KEY=AIzaSy...       # Required — used for generation + embeddings + OCR

# Vector DB (Qdrant Cloud)
QDRANT_URL=https://297e5cd6-c9e9-4194-a125-8bb7deeb1402.sa-east-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=eyJhbGci...     # Get from team lead
```

> **Note:** The Qdrant instance is already seeded. You only need to re-run the pipeline if you want to add more schemes.

---

## Step 3 — Verify Data is Ready

The scheme data should already be in `backend/data/seed_schemes.json` (tracked in git).

To verify:

```powershell
cd d:\DeepStation\m3_workspace

# Check scheme count
python -c "import json; d=json.load(open('backend/data/seed_schemes.json')); print(len(d), 'schemes')"
# Expected output: 48 schemes

# Check Qdrant is live
python -c "
from dotenv import load_dotenv; import os; load_dotenv()
from qdrant_client import QdrantClient
c = QdrantClient(url=os.getenv('QDRANT_URL'), api_key=os.getenv('QDRANT_API_KEY'))
info = c.get_collection('schemes')
print('Qdrant OK — Points:', info.points_count)
"
# Expected output: Qdrant OK — Points: 48
```

---

## Step 4 — Start the API Server

```powershell
cd d:\DeepStation\m3_workspace

# Activate venv if not already active
.\d:\DeepStation\venv\Scripts\Activate.ps1

# Start the server
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8001 --reload
```

Server will be available at:
- **API Root:** http://localhost:8001
- **Swagger Docs:** http://localhost:8001/docs
- **Health check:** http://localhost:8001/health

---

## Step 5 — Run Tests

```powershell
cd d:\DeepStation\m3_workspace

# Test form filling with demo profiles (no image needed)
python test_ocr_pipeline.py

# Test the live API
python test_api.py

# Test OCR on a real document image
python test_ocr_pipeline.py path\to\aadhaar.jpg pm-mudra-shishu aadhaar
```

---

## Re-running the Data Pipeline (if needed)

Only run this if you need to regenerate or add more schemes:

```powershell
cd d:\DeepStation\m3_workspace

# Step 1: Generate new scheme data via Gemini
python scripts\generate_schemes_gemini.py
# Output: data/processed/seed_schemes.json (48+ schemes)

# Step 2: Embed and upload to Qdrant
python scripts\embed_schemes.py
# Output: Qdrant collection 'schemes' populated

# Step 3: Copy to backend (for M4 Supabase seeding)
copy data\processed\seed_schemes.json backend\data\seed_schemes.json
```

---

## Integration Guide for Other Modules

---

### For M1 (AI Lead) — Agent Integration

M1's discovery/recommendation agents need to query Qdrant and call the form prefill API.

#### Qdrant Search

```python
import os
from dotenv import load_dotenv
import google.generativeai as genai
from qdrant_client import QdrantClient

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

def search_schemes(query: str, top_k: int = 5, filters: dict = None):
    """Search for schemes by semantic similarity."""
    # Embed the query
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=query,
        task_type="retrieval_query"  # IMPORTANT: use retrieval_query for search
    )
    vector = result["embedding"]

    # Build optional filter (e.g., by state or category)
    qdrant_filter = None
    if filters:
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        conditions = []
        if filters.get("state"):
            conditions.append(
                FieldCondition(key="state", match=MatchValue(value=filters["state"].lower()))
            )
        if conditions:
            qdrant_filter = Filter(must=conditions)

    # Search
    results = qdrant.query_points(
        collection_name="schemes",
        query=vector,
        limit=top_k,
        query_filter=qdrant_filter
    )

    return [
        {
            "scheme_id": r.payload["scheme_id"],
            "title": r.payload["title"],
            "score": r.score,
            "funding_amount": r.payload.get("funding_amount"),
            "eligibility": r.payload.get("eligibility_text"),
            "benefits": r.payload.get("benefits_text"),
            "apply_url": r.payload.get("application_url"),
            "documents": r.payload.get("documents_required", []),
        }
        for r in results.points
    ]

# Example usage:
schemes = search_schemes("young woman starting tailoring business in Karnataka")
# Returns top 5 matching schemes with scores, amounts, eligibility
```

#### Form Prefill (after agent extracts user profile)

```python
import requests

def get_prefilled_form(scheme_id: str, user_profile: dict):
    """Call M3 API to get a pre-filled application form."""
    resp = requests.post(
        "http://localhost:8001/forms/prefill",
        json={"scheme_id": scheme_id, "user_profile": user_profile}
    )
    return resp.json()

# Example:
form = get_prefilled_form("pm-mudra-shishu", {
    "name": "Priya Sharma",
    "age": 22,
    "gender": "F",
    "state": "Karnataka",
    "district": "Bangalore Urban",
    "business_intent": "tailoring"
})
# Returns: form with 60%+ fields auto-filled
```

---

### For M4 (Infra Lead) — Backend Integration

#### Supabase Seeding

```python
import json
# seed_schemes.json is already in backend/data/seed_schemes.json
# Use it to populate the 'schemes' table in Supabase

with open("m3_workspace/backend/data/seed_schemes.json") as f:
    schemes = json.load(f)

for scheme in schemes:
    supabase.table("schemes").upsert({
        "id": scheme["scheme_id"],
        "title": scheme["title"],
        "title_hi": scheme.get("title_hi"),
        "description": scheme["description"],
        "eligibility": scheme["eligibility_text"],
        "benefits": scheme["benefits_text"],
        "funding_amount": scheme.get("funding_amount"),
        "category": scheme["category"],
        "target_group": scheme["target_group"],
        "ministry": scheme["ministry"],
        "state": scheme["state"],
        "min_age": scheme.get("min_age"),
        "max_age": scheme.get("max_age"),
        "max_income": scheme.get("max_income"),
        "documents_required": scheme["documents_required"],
        "apply_url": scheme.get("application_url"),
    }).execute()
```

#### Wire `/apply` Route to M3 Form Filler

```python
# In your FastAPI/Express backend:
import requests

@app.post("/apply/{scheme_id}")
def apply_for_scheme(scheme_id: str, user_profile: dict):
    # Get pre-filled form from M3
    m3_resp = requests.post(
        "http://localhost:8001/forms/prefill",
        json={"scheme_id": scheme_id, "user_profile": user_profile}
    )
    return m3_resp.json()
```

#### Wire Document Upload to M3 OCR

```python
@app.post("/upload-document")
async def upload_document(file: UploadFile, scheme_id: str, doc_type: str = "auto"):
    # Forward to M3 OCR API
    files = {"file": (file.filename, await file.read(), file.content_type)}
    data  = {"scheme_id": scheme_id, "doc_type": doc_type}
    m3_resp = requests.post(
        "http://localhost:8001/ocr/extract-and-fill",
        files=files, data=data
    )
    # Returns pre-filled form from OCR data
    return m3_resp.json()
```

---

### For M2 (Frontend) — API Reference

The M3 API is REST + JSON. M2 can call it directly from the frontend or via M4's proxy.

#### Available Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | Health check |
| `GET` | `/forms` | List all 8 form templates |
| `GET` | `/forms/{scheme_id}` | Get empty form for a scheme |
| `POST` | `/forms/prefill` | Get form pre-filled with user data |
| `POST` | `/ocr/extract` | Extract data from uploaded document |
| `POST` | `/ocr/extract-and-fill` | Upload doc → get pre-filled form (WOW endpoint) |
| `GET` | `/doc-types` | List supported document types |
| `GET` | `/docs` | Swagger interactive UI |

#### Sample Call from JavaScript

```javascript
// Get pre-filled form for user
const response = await fetch('http://localhost:8001/forms/prefill', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    scheme_id: 'pm-mudra-shishu',
    user_profile: {
      name: 'Priya Sharma',
      age: 22,
      gender: 'F',
      state: 'Karnataka',
      district: 'Bangalore Urban'
    }
  })
});
const form = await response.json();
// form.fields[] → render as form inputs
// form.fill_percentage → show "60% auto-filled" badge

// Upload Aadhaar → auto-fill form
const formData = new FormData();
formData.append('file', aadhaarImageFile);
formData.append('scheme_id', 'pm-mudra-shishu');
formData.append('doc_type', 'aadhaar');

const ocrResp = await fetch('http://localhost:8001/ocr/extract-and-fill', {
  method: 'POST',
  body: formData
});
const result = await ocrResp.json();
// result.form.fields[] → pre-filled from Aadhaar data
```

---

## API Key Rotation

If any API key expires during the hackathon:

| Key | Where to Get |
|-----|-------------|
| `GEMINI_API_KEY` | console.cloud.google.com → APIs → Gemini API |
| `QDRANT_API_KEY` | cloud.qdrant.io → Your cluster → API Keys |
| `GROQ_API_KEY` | console.groq.com → API Keys |

After updating `.env`, restart the uvicorn server — it hot-reloads automatically.

---

## Quick Reference Commands

```powershell
# Activate venv
d:\DeepStation\venv\Scripts\Activate.ps1

# Start M3 API server
cd d:\DeepStation\m3_workspace
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8001 --reload

# Regenerate + re-embed all schemes
python scripts\generate_schemes_gemini.py
python scripts\embed_schemes.py

# Run tests
python test_ocr_pipeline.py
python test_api.py

# Check Qdrant
python -c "from qdrant_client import QdrantClient; import os; from dotenv import load_dotenv; load_dotenv(); c=QdrantClient(url=os.getenv('QDRANT_URL'),api_key=os.getenv('QDRANT_API_KEY')); print(c.get_collection('schemes').points_count, 'points in Qdrant')"
```

---

## Contact / Handoffs

| Module | Owner | What They Need From M3 |
|--------|-------|------------------------|
| **M1 (AI Lead)** | — | `seed_schemes.json`, Qdrant live, search verified |
| **M4 (Infra)** | — | `seed_schemes.json` for Supabase, `form_filler.py`, API on port 8001 |
| **M2 (Frontend)** | — | API endpoint list above, Swagger at `/docs` |
