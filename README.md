# 🇮🇳 Yojana Saathi — AI-Powered Government Scheme Navigator

[![CI](https://github.com/hem-ms39/yojana-saathi-auto/actions/workflows/ci.yml/badge.svg)](https://github.com/hem-ms39/yojana-saathi-auto/actions/workflows/ci.yml)
[![CD](https://github.com/hem-ms39/yojana-saathi-auto/actions/workflows/cd.yml/badge.svg)](https://github.com/hem-ms39/yojana-saathi-auto/actions/workflows/cd.yml)

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
                     │ REST + SSE  (/v1/...)
                     ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend (port 8000)         │
│                                                  │
│  AgentOrchestrator                               │
│  ├── ProfileAgent     (Groq LLM extraction)      │
│  ├── DiscoveryAgent   (Qdrant + Gemini embeddings)│
│  ├── EligibilityAgent (deterministic scoring)    │
│  └── SummaryAgent     (Groq LLM summaries)       │
│                                                  │
│  Routers: chat, explain, scheme_chat, compare,   │
│           apply, forms, voice, auth, health      │
└──┬──────────┬──────────┬──────────┬─────────────┘
   │          │          │          │
   ▼          ▼          ▼          ▼
Supabase   Groq LLM   WhatsApp   OCR service (m3_workspace, port 8001)
(Postgres  (gpt-oss   (Meta Cloud Gemini Vision → Aadhaar/PAN fields
 + Auth)    -20b)      API)
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
| 🔐 **Auth** | Supabase Email OTP (primary) + WhatsApp OTP via Meta WhatsApp Cloud API |
| 🌐 **Multilingual** | English, Hindi (हिन्दी), Kannada (ಕನ್ನಡ) |
| 🎤 **Voice Input** | Speech-to-text query entry |
| 📊 **Application History** | Profile page showing submitted applications |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.12 |
| **LLM** | Groq API (`openai/gpt-oss-20b`, configurable via `GROQ_MODEL`) |
| **Embeddings** | Gemini `gemini-embedding-001` (3072-dim), hash-based fallback when no key |
| **Vector Search** | Qdrant Cloud, in-memory fallback when not configured |
| **Database / Auth** | Supabase (Postgres + Auth) |
| **Notifications / OTP** | Meta WhatsApp Cloud API |
| **OCR** | Gemini Vision (separate FastAPI service in `m3_workspace/`) |
| **Portal Automation** | Playwright |
| **DevOps** | GitHub Actions CI/CD, Docker, GHCR, Render, Vercel |

---

## Setup

The app has three services. Each one can run directly on your machine (sections 2–4) or all together in Docker (section 5).

| Service | Folder | Port | Needs |
|---|---|---|---|
| Backend API | `backend/` | 8000 | root `.env` |
| OCR service | `m3_workspace/` | 8001 | root `.env` (`GEMINI_API_KEY`) |
| Frontend | `frontend/` | 3000 | `frontend/.env.local` |

### Prerequisites

- **Python 3.12** (CI and Docker use 3.12; some pinned packages do not install on 3.14 yet)
- **Node.js 22** (Node 18+ works)
- **Git**
- **Docker Desktop** — only for section 5
- Accounts (all have free tiers):

| Service | Get | Required? |
|---|---|---|
| [Groq](https://console.groq.com/keys) | API key | **Yes** — all LLM features |
| [Google AI Studio](https://aistudio.google.com/apikey) | Gemini API key (starts with `AIza`) | **Yes** — embeddings + OCR |
| [Supabase](https://supabase.com) | Project URL, `anon` key, `service_role` key | **Yes** — login + applications |
| [Qdrant Cloud](https://cloud.qdrant.io) | Cluster URL + API key | Optional — in-memory search without it |
| [Meta for Developers](https://developers.facebook.com) | WhatsApp Cloud API access token + phone number ID | Optional — WhatsApp OTP + notifications |

> **No OpenAI key is needed.** `OPENAI_API_KEY` is a leftover from early plans and is not used by any code.

---

### 1. Clone and configure

```bash
git clone https://github.com/hem-ms39/yojana-saathi-auto.git
cd yojana-saathi-auto
cp .env.example .env              # Windows PowerShell: Copy-Item .env.example .env
```

Fill in the root `.env`. The backend, the OCR service and Docker Compose all read this one file.

```env
GROQ_API_KEY=gsk_...
GROQ_MODEL=openai/gpt-oss-20b         # change here if Groq retires the model
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=                       # leave blank — unused

QDRANT_URL=https://xxxx.cloud.qdrant.io
QDRANT_API_KEY=...

SUPABASE_URL=https://xxxx.supabase.co # project URL only — no /rest/v1 at the end
SUPABASE_ANON_KEY=eyJ...              # "anon" key
SUPABASE_SERVICE_KEY=eyJ...           # "service_role" key — backend only, never in the frontend

WHATSAPP_ACCESS_TOKEN=EAAG...        # Meta app → WhatsApp → API Setup (optional: phone login)
WHATSAPP_PHONE_NUMBER_ID=1234567890
WHATSAPP_OTP_TEMPLATE=yojana_otp      # approved Authentication template; blank = free text
WHATSAPP_TEMPLATE_LANGUAGE=en_US

DEMO_MODE=false
DEFAULT_LANGUAGE=en
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
M3_API_URL=http://localhost:8001
```

`.env` and `frontend/.env.local` are git-ignored. Never commit them — the CI secret scan fails the build if a key is committed.

#### Supabase (one-time)

1. **SQL Editor → New query** → paste all of [`backend/supabase/schema.sql`](backend/supabase/schema.sql) → **Run**. This creates the `users`, `schemes` and `applications` tables.
2. **Project Settings → API Keys → Legacy API keys** → copy the `anon` and `service_role` keys into `.env`. Use the legacy JWT keys: the pinned `supabase` Python client may reject the newer `sb_secret_...` keys.
3. **Authentication → URL Configuration**
   - Site URL: `http://localhost:3000`
   - Redirect URLs: `http://localhost:3000/auth/callback`, and later `https://<your-vercel-app>.vercel.app/auth/callback`
4. **Authentication → Emails → SMTP Settings** → enable custom SMTP. Supabase's built-in sender only sends a few emails per hour and does not allow editing templates. With Gmail:
   - Host `smtp.gmail.com`, port `465`, username = your full Gmail address
   - Password = a [Gmail app password](https://myaccount.google.com/apppasswords) (needs 2-Step Verification). Never use your normal Gmail password.
   - Then raise **Authentication → Rate Limits → emails per hour** (for example to 30).
5. **Authentication → Emails → Templates** → in both **Magic Link** and **Confirm signup**, click **Source** and add the code, because the app asks the user to type a 6-digit code:
   ```html
   <h2>Your Yojana Saathi sign-in code</h2>
   <p style="font-size:32px;font-weight:bold;letter-spacing:6px">{{ .Token }}</p>
   <p>Or <a href="{{ .ConfirmationURL }}">click here to sign in</a>.</p>
   ```
6. Leave **Authentication → Providers → Phone** off. Phone sign-in goes through WhatsApp (next section), not Supabase SMS.

#### WhatsApp login (Meta WhatsApp Cloud API, optional)

Phone sign-in sends the 6-digit code on WhatsApp straight through Meta's free Cloud API (no Twilio).

1. Go to [developers.facebook.com](https://developers.facebook.com) → **My Apps → Create app** → use case **"Connect with customers through WhatsApp"** (type *Business*) → finish the wizard. Meta creates a free **test phone number** for you.
2. In the app, open **WhatsApp → API Setup**:
   - Copy **Phone number ID** → `WHATSAPP_PHONE_NUMBER_ID` in `.env`.
   - Click **Generate access token** → `WHATSAPP_ACCESS_TOKEN`. This token **expires after 24 hours**. For anything longer, create a permanent token: **Meta Business Settings → Users → System users → Add** (Admin) → **Assign assets** (your app, full control, and your WhatsApp account) → **Generate token** with the `whatsapp_business_messaging` and `whatsapp_business_management` permissions.
   - Under **To**, click **Manage phone number list** and add every phone that should receive codes (each one confirms with a code Meta sends). The test number can message **up to 5** recipients.
3. Choose how the code is sent:
   - **Quick test (no template):** leave `WHATSAPP_OTP_TEMPLATE` blank. WhatsApp only delivers free text within **24 hours of the user messaging your test number**, so first send any message (for example "hi") from the phone to the test number, then use the app.
   - **Proper OTP template (recommended, works any time):** open **WhatsApp Manager → Message templates → Create template** → category **Authentication** → code delivery **Copy code** → name it, for example `yojana_otp`, language **English (US)** → submit. Authentication templates are usually approved within minutes. Then set `WHATSAPP_OTP_TEMPLATE=yojana_otp` (and `WHATSAPP_TEMPLATE_LANGUAGE=en_US`, matching the template's language).
4. Restart the backend (it reads `.env` only at startup). `/health` should show `"whatsapp":"configured"`.
5. In the app: **Sign in → 💬 WhatsApp OTP**, enter one of the registered numbers (10 digits, or `+91XXXXXXXXXX`), and enter the code from WhatsApp.

The same settings send a best-effort WhatsApp confirmation when an application is submitted with a notification phone number.

---

### 2. Backend (`backend/`, port 8000)

Run all commands from the **repo root**: the backend is imported as the `backend` package.

```powershell
# Windows (PowerShell)
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend/requirements-dev.txt     # app + test/lint tools
playwright install chromium                     # only needed for portal auto-submit
```

```bash
# macOS / Linux
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements-dev.txt
playwright install chromium
```

**Load the scheme data (one-time, and again whenever `seed_schemes.json` changes):**

```bash
# from the repo root, with the venv activated
python scripts/seed_db.py        # 48 schemes → Supabase "schemes" table
python scripts/seed_qdrant.py    # 48 schemes → Gemini embeddings → Qdrant "schemes" collection
```

**Start it** — from the **repo root** (`...\yojana-saathi-auto>`), not from inside `backend\`:

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

> `ModuleNotFoundError: No module named 'backend'` means you are in the wrong folder — `cd` back to the repo root.

**Check it:**
- http://localhost:8000/health should return `"status":"ok"`, with `"supabase":"ok"` and `"m3_api":"ok"` once the OCR service is running.
- http://localhost:8000/docs is the interactive API docs. Try `POST /v1/chat` with `{"message": "30 year old farmer from Karnataka, income 80000", "language": "en"}`.

**Tests and lint (same as CI):**

```bash
cd backend
ruff check .
pytest
cd ..          # back to the repo root before starting the server again
```

---

### 3. OCR service (`m3_workspace/`, port 8001)

Uses the same virtual environment and reads `GEMINI_API_KEY` from the root `.env`.

Use a **second terminal** (venv activated), starting from the repo root:

```bash
pip install -r m3_workspace/requirements.txt pytest
cd m3_workspace                 # this service must be started from inside m3_workspace
python -m uvicorn backend.api.main:app --reload --port 8001
```

- http://localhost:8001/docs is the API docs. `POST /ocr/extract` takes an image upload; a sample is in `m3_workspace/backend/data/sample_aadhaar.png`.
- The backend reaches this service through `M3_API_URL` (default `http://localhost:8001`).
- Tests: `cd m3_workspace && pytest`

Data scripts in `m3_workspace/scripts/` (`scrape_schemes.py`, `clean_schemes.py`, `generate_schemes_gemini.py`, `embed_schemes.py`) rebuild the scheme dataset. You only need them to change the scheme list; normal setup uses `scripts/seed_db.py` and `scripts/seed_qdrant.py` above.

---

### 4. Frontend (`frontend/`, port 3000)

```bash
cd frontend
npm ci
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000/v1      # must end in /v1
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...                  # the anon key — never the service_role key
```

Everything starting with `NEXT_PUBLIC_` is shipped to the browser, so only public values go here.

```bash
npm run dev
```

Open http://localhost:3000 and search for *"22 year old woman from Bangalore, want to start a tailoring business"*. Restart `npm run dev` after editing `.env.local`.

**Checks (same as CI):**

```bash
npx next lint
npx tsc --noEmit
npm run build
```

---

### 5. Docker (all three services)

Needs [Docker Desktop](https://www.docker.com/products/docker-desktop/) running (on Windows, with the WSL 2 backend). It uses the root `.env` from step 1. You still need the Supabase setup and the seeding from step 2 once.

```bash
docker compose up --build        # first build takes a few minutes
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000/docs |
| OCR | http://localhost:8001/docs |

- Stop: `Ctrl+C`, then `docker compose down`
- Rebuild one service after code changes: `docker compose up --build backend`
- Logs: `docker compose logs -f backend`
- The frontend image bakes `SUPABASE_URL` and `SUPABASE_ANON_KEY` from `.env` in at **build** time, so rebuild it (`docker compose build frontend`) after changing them.

---

### 6. GitHub and CI/CD

#### Day-to-day workflow (everyone)

```bash
git checkout main && git pull
git checkout -b <your-name>/<short-topic>       # e.g. priya/qdrant-service
# ...make changes, run the checks for the part you touched...
git add <files>
git commit -m "feat(agents): add eligibility scoring"   # Conventional Commits
git push -u origin <your-name>/<short-topic>
```

Then open a Pull Request into `main` on GitHub. It can be merged once **all CI checks are green** and **one teammate has approved**. See [CONTRIBUTING.md](CONTRIBUTING.md).

#### Pipeline

```
 feature branch ──push──▶  CI (every push + PR)                         main ──▶ CD (only if CI green)
                           ├─ Backend   : ruff lint → pytest + coverage           ├─ Build & push 3 images → GHCR
                           ├─ OCR svc   : pytest                                  │   (tag = commit SHA + latest)
                           ├─ Frontend  : next lint → tsc → next build            ├─ Deploy backend + OCR → Render
                           ├─ Security  : gitleaks secret scan                    ├─ Deploy frontend      → Vercel
                           └─ Docker    : build images → run → smoke test         ├─ Smoke test live /health
                                                                                  └─ Tag GitHub release v1.0.N
```

| Workflow | File | Trigger |
|---|---|---|
| CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | every push, every PR to `main` |
| CD | [`.github/workflows/cd.yml`](.github/workflows/cd.yml) | after CI succeeds on `main`, or manually from the Actions tab |

CI needs no secrets. CD skips each deploy step whose secret is missing, so images are always published to GHCR even before hosting is set up.

#### One-time repository setup (repo owner)

1. **Settings → Collaborators** → add teammates with *Write* access.
2. **Settings → Actions → General → Workflow permissions** → *Read and write permissions* (CD pushes images and creates releases).
3. **Settings → Environments** → create `production`.
4. **Settings → Branches → Add rule** for `main`:
   - Require a pull request, with 1 approval
   - Require status checks: `Backend · lint + tests`, `OCR service · tests`, `Frontend · lint + typecheck + build`, `Security · secret scan`, `Docker · build images + smoke test` (they appear after CI has run once)
5. After the first CD run, open **your profile → Packages** and make the three `yojana-saathi-*` packages public, or give Render a registry credential, so Render can pull them.

#### Deploy the backend and OCR service (Render)

1. [render.com](https://render.com) → **New → Web Service → Existing image**.
2. Image: `ghcr.io/hem-ms39/yojana-saathi-backend:latest`. The backend listens on port `10000` (the image default).
3. **Environment**: add every variable from your root `.env`, plus `FRONTEND_URL=https://<your-vercel-app>.vercel.app` and `M3_API_URL=https://<your-ocr-service>.onrender.com`. Real API keys belong here, not in GitHub.
4. Health check path: `/health`.
5. **Settings → Deploy Hook** → copy the URL → GitHub secret `RENDER_BACKEND_DEPLOY_HOOK`.
6. Repeat for `ghcr.io/hem-ms39/yojana-saathi-ocr:latest` (port `8001`, needs `GEMINI_API_KEY`) → secret `RENDER_OCR_DEPLOY_HOOK`.

#### Deploy the frontend (Vercel)

1. [vercel.com](https://vercel.com) → **Add New → Project** → import this repo → **Root Directory: `frontend`**.
2. Environment variables:
   - `NEXT_PUBLIC_BACKEND_URL=https://<your-backend>.onrender.com/v1`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. **Settings → Git → Deploy Hooks** → create one for `main` → GitHub secret `VERCEL_DEPLOY_HOOK`.
4. Add `https://<your-vercel-app>.vercel.app/auth/callback` to Supabase's Redirect URLs.

#### GitHub secrets and variables (Settings → Secrets and variables → Actions)

| Name | Type | Value |
|---|---|---|
| `RENDER_BACKEND_DEPLOY_HOOK` | secret | Render deploy hook for the backend |
| `RENDER_OCR_DEPLOY_HOOK` | secret | Render deploy hook for the OCR service |
| `VERCEL_DEPLOY_HOOK` | secret | Vercel deploy hook for the frontend |
| `SUPABASE_ANON_KEY` | secret | Baked into the frontend image at build time |
| `BACKEND_PUBLIC_URL` | variable | Live backend URL **without** `/v1`, e.g. `https://yojana-backend.onrender.com` (enables the post-deploy smoke test) |
| `FRONTEND_PUBLIC_URL` | variable | Live frontend URL |
| `SUPABASE_URL` | variable | Supabase project URL |

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `CERTIFICATE_VERIFY_FAILED` on Groq/Gemini calls, chat times out | Antivirus HTTPS scanning (for example Norton Web/Mail Shield) replaces certificates and Python doesn't trust it. Turn off the antivirus's encrypted-connection scanning for development, or make the venv trust the Windows certificate store. |
| `model ... does not exist` from Groq | Groq retired the model. Pick one from the [Groq models list](https://console.groq.com/docs/models) and set `GROQ_MODEL` in `.env`. |
| Gemini `API key not valid` | Create a new key at https://aistudio.google.com/apikey. It should start with `AIza`. |
| Supabase `PGRST125 Invalid path` | `SUPABASE_URL` ends in `/rest/v1/`. Use only `https://xxxx.supabase.co`. |
| Supabase `Could not find the table` / health shows `supabase: not_configured_or_unreachable` | Run `backend/supabase/schema.sql` in the SQL Editor. |
| Chat error `Collection 'schemes' doesn't exist` | Run `python scripts/seed_qdrant.py`. |
| `ModuleNotFoundError: No module named 'backend'` | Start the backend from the repo root, and the OCR service from inside `m3_workspace`. |
| Frontend loads but every search fails (404) | `NEXT_PUBLIC_BACKEND_URL` must end in `/v1`. |
| No OTP email / "rate limit reached" | Set up custom SMTP in Supabase (step 1), and check Spam and **Supabase → Logs → Auth**. |
| Email arrives but has no code | Add `{{ .Token }}` to the Magic Link and Confirm signup templates. |
| "WhatsApp sign-in is not configured" | Set `WHATSAPP_ACCESS_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID` in `.env` and restart the backend. |
| "not on the app's WhatsApp test recipient list" (code 131030) | Add the number under Meta app → **WhatsApp → API Setup → To → Manage phone number list** (max 5 on the test number). |
| "WhatsApp needs you to message us first" (code 131047) | No OTP template is set and the user hasn't messaged the test number in the last 24 hours. Send "hi" from the phone, or set `WHATSAPP_OTP_TEMPLATE`. |
| "server access token expired" (code 190) | The temporary token from API Setup lasts 24 hours. Generate a new one, or create a permanent System User token (see the WhatsApp login section). |
| "template not found" (code 132001) | `WHATSAPP_OTP_TEMPLATE` or `WHATSAPP_TEMPLATE_LANGUAGE` doesn't match an **approved** template in WhatsApp Manager. |
| Any other WhatsApp failure | The backend terminal logs `WhatsApp OTP send failed (code …)` with Meta's exact reason. |

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

## Project Structure

```
yojana-saathi-auto/
├── .github/workflows/     # ci.yml, cd.yml
├── backend/               # FastAPI API (port 8000)
│   ├── agents/            # Profile, Discovery, Eligibility, Summary, Orchestrator
│   ├── data/seed_schemes.json   # 48 government schemes
│   ├── models/            # Pydantic schemas
│   ├── routers/           # chat, explain, scheme_chat, compare, apply, forms, voice, auth, health
│   ├── services/          # llm (Groq), embedding (Gemini), qdrant, supabase, whatsapp (Meta), m3 (OCR client)
│   ├── supabase/schema.sql      # database tables — run once in Supabase
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt / requirements-dev.txt
│   └── main.py
├── m3_workspace/          # OCR + form-filling service (port 8001)
│   ├── backend/agents/    # ocr_agent (Gemini Vision), form_filler
│   ├── backend/api/main.py
│   ├── scripts/           # scrape / clean / generate / embed scheme data
│   ├── tests/
│   └── Dockerfile
├── frontend/              # Next.js app (port 3000)
│   └── src/
│       ├── app/           # page.tsx, results/, schemes/[id]/, compare/, profile/, auth/callback/
│       ├── components/    # scheme-card, scheme-chatbot, auth-modal, nav-bar, voice-button, ...
│       ├── contexts/auth-context.tsx
│       └── lib/           # api.ts (backend client + SSE), supabase.ts
├── scripts/               # seed_db.py, seed_qdrant.py
├── prototype/             # early UI prototype (not deployed)
├── docker-compose.yml
└── .env.example
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

| Member | Module | CI/CD responsibility |
|---|---|---|
| Member 1 | Backend core & AI agents (`backend/agents`, `models`, core routers, tests) | Backend lint/test job, backend Dockerfile |
| Member 2 | Services, data & integrations (`backend/services`, `scripts`, `data`) | Secret scan, Docker build + smoke test job |
| Member 3 | Frontend (`frontend/`) | Frontend lint/typecheck/build job, frontend Dockerfile |
| Member 4 | OCR service & DevOps (`m3_workspace/`, `.github/`) | OCR test job, docker-compose, CD workflow |

See [TEAM_PLAN.md](TEAM_PLAN.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
