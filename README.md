# 🇮🇳 Yojana Saathi — AI-Powered Government Scheme Navigator

> **Hackathon Project** — Helping Indian citizens discover, understand, and apply for government schemes they qualify for, using a multi-agent AI pipeline.

---

## What is Yojana Saathi?

Yojana Saathi (योजना साथी — *"Scheme Companion"*) is a conversational AI platform that:

1. **Understands** your profile from natural language (age, income, occupation, state, caste, etc.)
2. **Discovers** relevant government schemes using semantic search over an embedding index
3. **Explains** why you are or aren't eligible — with bullet-by-bullet comparisons
4. **Answers** your questions about any scheme via a RAG-powered chatbot
5. **Compares** multiple schemes side-by-side with LLM-generated insights
6. **Auto-fills** application forms using your Aadhaar/PAN via OCR
7. **Submits** applications to government portals via Playwright automation

### Supported Schemes
48 schemes across: MSME loans, scholarships, women entrepreneurship, SC/ST support, agriculture, housing, skill development, and more.

---

## Architecture

```
User Query (text / voice)
        │
        ▼
┌─────────────────────────────────────────────────┐
│              Next.js Frontend (port 3000)        │
│  Search → Results → Why? → Chatbot → Apply Form │
└────────────────────┬────────────────────────────┘
                     │ REST + SSE
                     ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend (port 8000)         │
│                                                  │
│  AgentOrchestrator                               │
│  ├── ProfileAgent    (Groq LLM extraction)       │
│  ├── DiscoveryAgent  (Qdrant embedding search)   │
│  ├── EligibilityAgent (deterministic scoring)    │
│  └── SummaryAgent   (Groq LLM summaries)         │
│                                                  │
│  Routers: chat, explain, scheme_chat, compare,   │
│           apply, forms, voice, auth, health      │
└──────┬──────────┬──────────┬────────────────────┘
       │          │          │
       ▼          ▼          ▼
  Supabase     Groq LLM   Twilio SMS
  (Postgres    (llama-3.1  (OTP auth)
  + Auth)      -8b-instant)
```

---

## Features

| Feature | Description |
|---|---|
| 🔍 **Natural Language Search** | "22 yr old woman from Karnataka, want to start a tailoring business" |
| 🤖 **Multi-Agent Pipeline** | Profile extraction → Semantic search → Eligibility scoring → Ranking |
| ❓ **"Why?" Explainer** | Per-card streaming explanation with RAG alternative scheme suggestions |
| 💬 **Scheme Chatbot** | Q&A on any scheme detail page — documents, eligibility, how to apply |
| ⚖️ **Scheme Comparison** | Select 2–3 schemes → LLM-powered side-by-side comparison table |
| 📄 **OCR Auto-fill** | Upload Aadhaar/PAN → Gemini Vision extracts fields → pre-fills form |
| 🔐 **Auth** | Supabase Email OTP (primary) + SMS OTP via Twilio (fallback) |
| 🌐 **Multilingual** | English, Hindi (हिन्दी), Kannada (ಕನ್ನಡ) |
| 🎤 **Voice Input** | Speech-to-text query entry |
| 📊 **Application History** | Profile page showing submitted applications |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 14, React, TypeScript, Vanilla CSS |
| **Backend** | FastAPI, Python 3.10 |
| **LLM** | Groq API (`llama-3.1-8b-instant`) |
| **Embeddings** | In-memory SHA256-hash projection (drop-in for Gemini/OpenAI) |
| **Vector Search** | Qdrant (cloud) with in-memory fallback |
| **Database / Auth** | Supabase (Postgres + Auth) |
| **SMS / WhatsApp** | Twilio |
| **OCR** | Gemini 2.0 Flash Vision |
| **Portal Automation** | Playwright |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- A [Supabase](https://supabase.com) project (free tier works)
- A [Groq](https://console.groq.com) API key (free tier works)
- (Optional) Twilio account for SMS OTP
- (Optional) Qdrant cloud instance for persistent vector search

---

## Local Setup

### 1. Clone the repo

```bash
git clone https://github.com/goldkrs/Yojana_Sathi.git
cd Yojana_Sathi
```

### 2. Backend

```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install playwright==1.48.0
playwright install chromium
```

Create a `.env` file in the **repo root**:

```env
# LLM
GROQ_API_KEY=your_groq_api_key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key

# Twilio (optional — for SMS OTP fallback)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Qdrant (optional — uses in-memory index if not set)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_key

# App
DEMO_MODE=false
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

Start the backend:

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Backend runs at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### 3. Frontend

```powershell
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000/v1
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_public_key
```

Start the frontend:

```powershell
npm run dev
```

Frontend runs at: `http://localhost:3000`

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/v1/chat` | Main agent pipeline — SSE stream |
| `GET` | `/v1/schemes/{id}` | Scheme detail |
| `POST` | `/v1/schemes/compare` | LLM scheme comparison |
| `POST` | `/v1/schemes/{id}/chat` | Scheme Q&A chatbot — SSE stream |
| `POST` | `/v1/explain` | "Why?" eligibility explanation — SSE stream |
| `POST` | `/v1/apply` | Submit application |
| `POST` | `/v1/forms/prefill` | OCR auto-fill form |
| `POST` | `/v1/voice` | Voice transcription |
| `POST` | `/v1/auth/whatsapp-otp/send` | Send WhatsApp OTP |
| `POST` | `/v1/auth/whatsapp-otp/verify` | Verify WhatsApp OTP |

---

## Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. **Auth → Providers → Email** → Enable, set OTP expiry to 3600s
3. **Auth → Email Templates** → Update the OTP template to display `{{ .Token }}` prominently
4. (Optional) **Auth → Providers → Phone** → Enable with Twilio for SMS OTP
5. Run the schema migrations in `backend/supabase/` if present

---

## Project Structure

```
Yojana_Sathi/
├── backend/
│   ├── agents/           # Profile, Discovery, Eligibility, Orchestrator
│   ├── data/
│   │   └── seed_schemes.json   # 48 government schemes
│   ├── models/           # Pydantic schemas
│   ├── routers/          # FastAPI route handlers
│   │   ├── chat.py       # Main agent SSE pipeline
│   │   ├── explain.py    # Why? eligibility chatbot
│   │   ├── scheme_chat.py # Scheme Q&A chatbot
│   │   ├── compare.py    # Scheme comparison
│   │   ├── apply.py      # Application submission
│   │   ├── auth.py       # WhatsApp OTP auth
│   │   └── ...
│   ├── services/
│   │   ├── llm_service.py       # Groq client + streaming
│   │   ├── embedding_service.py # Text → vector
│   │   ├── qdrant_service.py    # Vector search
│   │   └── supabase_service.py  # DB operations
│   └── main.py           # FastAPI app + router registration
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx          # Home / search
│       │   ├── results/          # Scheme results with Why? + compare
│       │   ├── schemes/[id]/     # Scheme detail + chatbot + apply form
│       │   ├── compare/          # Side-by-side comparison page
│       │   └── profile/          # User application history
│       ├── components/
│       │   ├── scheme-card.tsx   # Card with Why? panel + compare checkbox
│       │   ├── scheme-chatbot.tsx # Q&A chat panel
│       │   ├── auth-modal.tsx    # Email/SMS OTP modal
│       │   └── nav-bar.tsx       # Auth-aware navigation
│       ├── contexts/
│       │   └── auth-context.tsx  # Supabase session provider
│       └── lib/
│           ├── api.ts            # Backend API client + SSE helpers
│           └── supabase.ts       # Supabase browser client
└── requirements.txt
```

---

## Demo Query Examples

```
"22 year old woman from Bangalore, want to start a tailoring business"
"SC student from rural Karnataka looking for engineering scholarships"
"Farmer from Maharashtra with 2 acres land, need crop insurance"
"Unemployed youth from Bihar, want to learn a skill and get a loan"
"Muslim woman entrepreneur from UP, existing garment business"
```

---

## Team

Built for the hackathon by **Team DeepStation / goldkrs**.
