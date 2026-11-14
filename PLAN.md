# PLAN.md — Yojana Saathi

**"Find every government rupee you're entitled to — automatically."**

**Hackathon:** Deepstation AI Hackathon  
**Track:** Community  
**Team Size:** 4  
**Timeline:** \~48 hours  
**Last Updated:** May 2026

---

## Table of Contents

1. [Project Vision](#1-project-vision)  
2. [Core Idea Overview](#2-core-idea-overview)  
3. [MVP Definition (CRITICAL)](#3-mvp-definition)  
4. [Core Features](#4-core-features)  
5. [User Flow](#5-user-flow)  
6. [Technical Architecture](#6-technical-architecture)  
7. [Recommended Tech Stack](#7-recommended-tech-stack)  
8. [AI Components](#8-ai-components)  
9. [Database Schema](#9-database-schema)  
10. [API Design](#10-api-design)  
11. [Folder Structure](#11-folder-structure)  
12. [Vibecoding Execution Strategy](#12-vibecoding-execution-strategy)  
13. [Team Division](#13-team-division)  
14. [Roadmap](#14-roadmap)  
15. [UI/UX Design Direction](#15-uiux-design-direction)  
16. [Demo Strategy](#16-demo-strategy)  
17. [Risk Management](#17-risk-management)  
18. [Future Scope](#18-future-scope)

---

## 1\. Project Vision

### Mission Statement

Yojana Saathi is an autonomous citizen advocate — an AI-powered multi-agent system that discovers government schemes you qualify for, explains them in your language, checks your eligibility, and helps you apply. It replaces weeks of manual research across dozens of portals with a single voice query in your mother tongue.

### Problem Statement

India operates **950+ central government schemes** and **5,000+ state-level schemes** collectively worth approximately ₹15 lakh crore annually. Despite this massive allocation, an estimated **₹45,000+ crore goes unclaimed every year** — not because citizens don't qualify, but because:

- **Fragmentation:** Schemes are scattered across MyScheme.gov.in, Startup India, MSME portals, state government websites, and hundreds of ministry pages. There is no single entry point.  
- **Legibility:** Eligibility criteria are written in dense bureaucratic English. A farmer in Karnataka or a street vendor in UP cannot parse "beneficiaries must belong to a household with annual income not exceeding ₹2,00,000 as per the SECC 2011 database."  
- **Friction:** Applying means navigating 5–10 separate portals, each with different logins, form formats, and document requirements.  
- **Language:** The majority of India speaks Hindi, Kannada, Tamil, Telugu, Bengali, or Marathi. Most scheme information exists only in English.  
- **Tracking:** After filing, there is no unified way to check status. Citizens call helpdesks, visit offices, or simply give up.

### Why This Matters Socially

- The people who most need government support (daily-wage workers, rural women, first-generation entrepreneurs, students from low-income families) are the least equipped to navigate bureaucratic systems.  
- ₹45,000 crore unclaimed annually means millions of families miss healthcare, education subsidies, skill training, and startup capital they are legally entitled to.  
- The information asymmetry is the bottleneck — not the funding.

### Why This Solution Stands Out

- It is **not a chatbot**. It is a multi-agent system that takes real-world action: filling forms, submitting applications, tracking status, and sending notifications.  
- It works in **Kannada, Hindi, and English** via voice — no literacy required.  
- It covers **4 of the 8 community verticals** listed in the hackathon PS: startup/non-profit funding, SMB grants, accessible education (scholarships), and job discovery (skill-development schemes).  
- The architecture (multi-agent with visible reasoning traces) directly targets the hackathon's advanced tier.

---

## 2\. Core Idea Overview

### Platform End-to-End

Yojana Saathi is a web-based platform (PWA) where a user can:

1. **Speak or type** their situation in any supported language ("I'm a 22-year-old woman wanting to start a tailoring business in a tier-2 city")  
2. **Receive a ranked list** of government schemes they qualify for, with match confidence, funding amount, and deadlines  
3. **Deep-dive** into any scheme — AI-generated summary, eligibility breakdown, required documents, application steps  
4. **Compare** schemes side-by-side  
5. **Auto-apply** for select schemes — the system fills forms, attaches documents, and submits  
6. **Track** application status with WhatsApp notifications

### Target Users

| Persona | Description | Primary Interface |
| :---- | :---- | :---- |
| **Rural citizen** | Farmer, daily-wage worker, semi-literate | Voice in regional language |
| **First-gen entrepreneur** | Starting a small business, seeking MUDRA/PMEGP loans | Voice or text, Hindi/English |
| **Student** | Seeking scholarships (NSP, state merit, minority) | Text, English/Hindi |
| **SMB owner** | Looking for MSME subsidies, Startup India benefits | Text, English |
| **NGO/CSR worker** | Helping communities discover entitlements at scale | Dashboard, English |

### How AI Improves Accessibility

- **Language barrier → solved by multilingual LLM \+ speech-to-text.** Users speak naturally; the AI extracts structured profile data.  
- **Legibility barrier → solved by RAG \+ summarization.** Dense government PDFs become 3-sentence plain-language summaries.  
- **Discovery barrier → solved by semantic search over vector DB.** Instead of keyword-matching on portal sites, the system understands intent ("I want money to start a business" → MUDRA, PMEGP, Startup India, SFURTI, ASPIRE...).  
- **Application barrier → solved by form-filling agent.** The AI pre-fills forms using extracted profile data and OCR'd documents.  
- **Tracking barrier → solved by notification agent.** WhatsApp updates replace phone calls to district offices.

---

## 3\. MVP Definition

**This is the most important section. Read it before writing a single line of code.**

### The Demo-Day Contract

The MVP must support this exact 90-second demo flow:

1. User speaks a query in Hindi/Kannada/English → voice captured, transcribed  
2. Side panel shows agent reasoning (profile extraction → scheme discovery → eligibility check)  
3. 5–7 scheme cards appear, ranked by match score and funding amount  
4. User clicks one scheme → detailed AI summary \+ eligibility breakdown  
5. User clicks "Auto-Apply" → form pre-filled with demo data  
6. WhatsApp notification arrives on a real phone

**If this flow works end-to-end, you win.** Everything else is stretch.

### MUST Implement (P0 — No Excuses)

| Feature | Why It's P0 | Implementation Notes |
| :---- | :---- | :---- |
| Voice input (mic button) | Wow-factor, accessibility story | Use browser Web Speech API. Dead simple. No backend needed for STT. |
| Text input fallback | For when voice fails in noisy demo hall | Standard input field. |
| Profile extraction from natural language | Core AI differentiator | Single LLM call with structured output (JSON mode). |
| Scheme vector DB with \~100–200 schemes | RAG backbone | Pre-scraped, pre-embedded. Done on Day 1 Morning. |
| Semantic scheme search | Discovery agent | Qdrant similarity search \+ metadata filter. |
| Eligibility matching with confidence | Core value prop | LLM reasoning over user profile × scheme criteria. |
| Scheme cards UI | Demo visual | shadcn cards with amount, match %, deadline, category. |
| Scheme detail page | Shows AI understands the scheme | LLM-generated summary, eligibility checklist, required docs. |
| Agent reasoning side panel | Judge wow-factor (CRITICAL) | Streaming log of agent steps. Like Cursor's reasoning trace. |
| Language toggle (EN / HI / KN) | Multilingual story | i18n for static UI \+ LLM responds in selected language. |
| WhatsApp notification | Action-layer proof | Twilio one-shot message. Pre-configure before demo. |

### CAN Mock/Fake If Needed (P1)

| Feature | How to Fake It |
| :---- | :---- |
| Form auto-fill | Show a pre-filled PDF/form screenshot. Don't need real Playwright submission. |
| Application tracking | Hardcode 2–3 status entries in DB. Show timeline UI. No real polling needed. |
| Document OCR | Use a pre-processed Aadhaar/PAN result. Show the extraction, skip live camera. |
| Scheme comparison | Side-by-side cards with static data. No dynamic comparison agent needed. |

### Should NOT Attempt Initially (P2 — Ignore Until P0 Is Done)

- Real form submission to government portals  
- DigiLocker integration  
- Voice agent calling helpdesks  
- User authentication / login flows (use a demo user)  
- Payment or fee processing  
- Real-time portal scraping (pre-scrape everything)  
- Push notifications (WhatsApp is enough)  
- Mobile app (PWA is sufficient)  
- Database migrations or complex schema (Supabase raw SQL is fine)

### The Priority Stack

P0: Voice → Profile → Search → Match → Cards → Detail → Side Panel → WhatsApp

P1: Form mockup → Tracking timeline → OCR demo → Comparison

P2: Everything else

**Rule: No one touches P1 until ALL of P0 is working end-to-end.**

---

## 4\. Core Features

### MVP Features (Ship These)

1. **Multilingual Voice Input**  
     
   - Browser-native Web Speech API for real-time speech-to-text  
   - Supports English, Hindi, Kannada  
   - Fallback: text input field with language detection

   

2. **Intelligent Profile Extraction**  
     
   - User speaks naturally → LLM extracts structured JSON profile  
   - Fields: age, gender, location (state/district), income range, caste category, occupation, education level, business intent, existing assets  
   - Ask clarifying questions for missing critical fields

   

3. **RAG-Powered Scheme Discovery**  
     
   - Vector DB (Qdrant) containing \~150–200 government schemes  
   - Each scheme embedded with: title, description, eligibility criteria, benefits, required documents, application URL, deadline, ministry, category tags  
   - Semantic search returns top 10–15 candidates

   

4. **Eligibility Matching Agent**  
     
   - Takes user profile \+ candidate schemes  
   - LLM reasons through each eligibility criterion  
   - Returns: eligible / likely eligible / not eligible \+ confidence score \+ reasoning  
   - Ranks by: eligibility confidence × funding amount

   

5. **Scheme Detail View**  
     
   - AI-generated plain-language summary (3–4 sentences)  
   - Eligibility checklist (✅/❌ per criterion with explanation)  
   - Required documents list  
   - Application steps  
   - Deadline and funding amount  
   - "Auto-Apply" CTA

   

6. **Agent Reasoning Side Panel**  
     
   - Real-time streaming log of what agents are doing  
   - Shows: "Extracting profile... Found: age=22, location=Bangalore..."  
   - Shows: "Searching 200 schemes... Found 12 candidates..."  
   - Shows: "Checking eligibility for PM-MUDRA... ✅ Eligible (92%)"  
   - Styled like a terminal/reasoning trace

   

7. **WhatsApp Notification**  
     
   - Twilio sends a confirmation message after "applying"  
   - Message includes: scheme name, application ID (mocked), next steps  
   - Arrives on a real phone during demo

   

8. **Language Toggle**  
     
   - UI strings in EN/HI/KN via i18n  
   - LLM system prompt switches response language  
   - Voice recognition language switches accordingly

### Advanced Features (Day 2 If Time Permits)

9. **Document Upload \+ OCR**  
     
   - Upload Aadhaar, PAN, income certificate  
   - Gemini Vision extracts: name, DOB, address, Aadhaar number, PAN number, income  
   - Auto-populates profile fields

   

10. **Form Auto-Fill Preview**  
      
    - For 2–3 selected schemes (MUDRA, NSP, Startup India)  
    - Show a rendered form with pre-filled values from user profile  
    - "Submit" button (mocked — shows success state)

    

11. **Application Tracking Timeline**  
      
    - Status: Applied → Under Review → Approved/Rejected  
    - Hardcoded demo data with realistic timestamps  
    - Visual timeline component

    

12. **Scheme Comparison**  
      
    - Select 2–3 schemes → side-by-side view  
    - Compare: amount, eligibility, documents needed, timeline, success rate

### Stretch Features (Only If Ahead of Schedule)

13. AI voice output (TTS) for reading scheme summaries aloud  
14. Saved schemes / bookmarks  
15. User history across sessions (Supabase auth \+ profile persistence)  
16. Heatmap of popular schemes by region  
17. PDF export of eligibility report  
18. Scheme deadline alerts  
19. Group application mode for SHGs

---

## 5\. User Flow

### Flow 1: First-Time User (Primary Demo Flow)

Landing Page

    │

    ├── Hero: "Find every government rupee you deserve"

    ├── Giant mic button (center)

    ├── Language toggle: EN | हिंदी | ಕನ್ನಡ

    ├── Text input below mic: "Or type your situation..."

    │

    ▼

User taps mic → speaks in Kannada:

"Naanu 25 varsha, Bengaluru-alli small restaurant shuru maadbeku"

    │

    ▼

Transcription appears in real-time (Web Speech API)

    │

    ▼

Side panel opens → Agent reasoning trace streams:

    ├── "🎤 Transcribed: Naanu 25 varsha..."

    ├── "🧠 Extracting profile..."

    ├── "👤 Profile: {age: 25, location: Bengaluru, intent: restaurant}"

    ├── "🔍 Searching 200 schemes..."

    ├── "📋 Found 14 candidates"

    ├── "✅ Checking eligibility..."

    ├── "📊 7 schemes eligible"

    │

    ▼

Main panel shows 7 scheme cards:

    ├── PM-MUDRA Shishu (₹50,000) — 95% match

    ├── PMEGP (₹25,00,000) — 88% match

    ├── Stand-Up India (₹1,00,00,000) — 72% match

    ├── ... more cards

    │

    ▼

User clicks "PM-MUDRA Shishu" →

    │

    ├── AI Summary (3 sentences, in Kannada)

    ├── Eligibility: ✅ Age ✅ Business type ✅ No existing bank loan

    ├── Required docs: Aadhaar, Business plan, Bank account

    ├── How to apply: 3 steps

    ├── \[Auto-Apply\] button

    │

    ▼

User clicks "Auto-Apply" →

    ├── Form preview with pre-filled data

    ├── "Submit Application" button

    │

    ▼

User clicks Submit →

    ├── Success animation

    ├── "Application \#YS-2026-4521 submitted"

    ├── "WhatsApp update sent to \+91-XXXXX"

    ├── Judge's phone buzzes ✅

    │

    ▼

Dashboard shows:

    └── Application timeline: Applied → Under Review → ...

### Flow 2: Low-Literacy User (Voice-Only)

User arrives → sees large mic icon with text in regional language

    │

    ├── Taps mic

    ├── Speaks naturally in Hindi: "Meri beti ke liye scholarship chahiye, 

    │   10th pass hai, ghar mein koi government job nahi hai"

    │

    ▼

AI extracts: {relationship: daughter, need: scholarship, 

              education: 10th, govt\_job\_in\_family: false}

    │

    ├── AI asks ONE follow-up (voice): "Aapki beti ki umar kitni hai 

    │   aur aap kis state mein rehte hain?"

    │   (How old is your daughter and which state do you live in?)

    │

    ▼

Scheme results displayed with:

    ├── Large scheme name in Hindi

    ├── Funding amount in big ₹ text

    ├── Green/red eligibility indicators (no text needed)

    ├── Speaker icon to hear scheme summary aloud (stretch)

### Flow 3: Scheme Application Guidance

User on scheme detail page → clicks "How to Apply"

    │

    ▼

Step-by-step guide:

    ├── Step 1: Gather documents (Aadhaar, bank passbook, ...)

    ├── Step 2: Visit \[portal link\] or nearest CSC center

    ├── Step 3: Fill application form

    ├── Step 4: Upload documents

    ├── Step 5: Note application reference number

    │

    ├── \[Upload Documents\] — OCR extracts data (stretch)

    ├── \[Auto-Fill Form\] — shows pre-filled preview

    └── \[Track Application\] — timeline view

---

## 6\. Technical Architecture

### High-Level Architecture

┌─────────────────────────────────────────────────────────┐

│                    CLIENT (Next.js PWA)                  │

│                                                         │

│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │

│  │ Voice UI │  │ Chat UI  │  │ Scheme   │  │ Agent  │  │

│  │ (WebSpeech│  │          │  │ Cards/   │  │ Side   │  │

│  │  API)    │  │          │  │ Detail   │  │ Panel  │  │

│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  │

│       └──────────────┴─────────────┴────────────┘       │

│                        │ HTTP/SSE                       │

└────────────────────────┼────────────────────────────────┘

                         │

                         ▼

┌─────────────────────────────────────────────────────────┐

│                  BACKEND (FastAPI)                       │

│                                                         │

│  ┌──────────────────────────────────────────────────┐   │

│  │              API Gateway Layer                    │   │

│  │  /chat  /recommend  /eligibility  /apply /voice  │   │

│  └─────────────────────┬────────────────────────────┘   │

│                        │                                │

│  ┌─────────────────────▼────────────────────────────┐   │

│  │           LangGraph Orchestrator                  │   │

│  │                                                   │   │

│  │  ┌─────────┐ ┌──────────┐ ┌───────────────────┐  │   │

│  │  │Profile  │ │Discovery │ │Eligibility        │  │   │

│  │  │Extractor│ │Agent     │ │Reasoner           │  │   │

│  │  └─────────┘ └──────────┘ └───────────────────┘  │   │

│  │  ┌─────────┐ ┌──────────┐ ┌───────────────────┐  │   │

│  │  │Summary  │ │Form-Fill │ │Notification       │  │   │

│  │  │Agent    │ │Agent     │ │Agent (Twilio)     │  │   │

│  │  └─────────┘ └──────────┘ └───────────────────┘  │   │

│  └──────────────────────────────────────────────────┘   │

│                        │                                │

└────────────────────────┼────────────────────────────────┘

                         │

          ┌──────────────┼──────────────┐

          │              │              │

          ▼              ▼              ▼

   ┌────────────┐ ┌────────────┐ ┌──────────┐

   │  Qdrant    │ │  Supabase  │ │  Twilio  │

   │ (schemes   │ │ (users,    │ │ WhatsApp │

   │  vectors)  │ │  apps,     │ │   API    │

   │            │ │  status)   │ │          │

   └────────────┘ └────────────┘ └──────────┘

### Data Flow (Primary Query)

1\. User speaks → Web Speech API transcribes in browser

2\. Transcript \+ language → POST /api/chat

3\. FastAPI receives → LangGraph orchestrator starts

4\. Step 1: Profile Extractor (LLM call with JSON mode)

   \- Input: raw transcript \+ language

   \- Output: {age, gender, location, income, occupation, intent, ...}

   \- Streams step to SSE for side panel

5\. Step 2: Discovery Agent

   \- Takes profile → constructs semantic query

   \- Queries Qdrant (top 15 by cosine similarity)

   \- Applies metadata filters (state, category)

   \- Streams step to SSE

6\. Step 3: Eligibility Reasoner

   \- For each candidate scheme (batched, max 10):

     \- LLM evaluates user profile against scheme criteria

     \- Returns: eligible/ineligible, confidence 0-100, reasoning

   \- Ranks by confidence × funding\_amount

   \- Streams results to SSE

7\. Step 4: Summary Agent

   \- For selected schemes, generates plain-language summary

   \- In user's selected language

8\. Results returned via SSE as they stream

9\. Frontend renders scheme cards progressively

### SSE (Server-Sent Events) for Real-Time Agent Panel

The agent reasoning side panel is the demo's most visually impressive feature. It works via SSE:

Client opens: EventSource('/api/chat/stream?session\_id=xxx')

Server sends events:

  event: agent\_step

  data: {"agent": "profile\_extractor", "status": "running", "message": "Extracting profile from transcript..."}

  event: agent\_step

  data: {"agent": "profile\_extractor", "status": "complete", "result": {"age": 22, "location": "Bangalore"}}

  event: agent\_step

  data: {"agent": "discovery", "status": "running", "message": "Searching 200 schemes..."}

  event: scheme\_found

  data: {"scheme\_id": "mudra-shishu", "name": "PM-MUDRA Shishu", "match": 95}

  event: agent\_step

  data: {"agent": "eligibility", "status": "complete", "eligible\_count": 7}

  event: results\_ready

  data: {"schemes": \[...\]}

---

## 7\. Recommended Tech Stack

### Frontend

| Technology | Why |
| :---- | :---- |
| **Next.js 15 (App Router)** | SSR for fast initial load, API routes as BFF if needed, great DX with Cursor/Claude Code. Vercel deploys in 30 seconds. |
| **Tailwind CSS** | Fastest styling for hackathons. AI agents generate valid Tailwind reliably. |
| **shadcn/ui** | Pre-built, accessible, beautiful components. Copy-paste, not npm install. Cards, buttons, dialogs, sheets — all ready. |
| **Framer Motion** | Scheme cards slide in, agent steps animate. 10 minutes of work → significant polish. |
| **Web Speech API** | Browser-native STT. Zero backend cost. Supports Hindi and Kannada recognition. No API key needed. |
| **next-intl** or **simple i18n object** | Lightweight language switching for EN/HI/KN static strings. |

### Backend

| Technology | Why |
| :---- | :---- |
| **FastAPI (Python 3.12)** | Best AI/ML ecosystem (LangChain, LangGraph, Qdrant client, Groq SDK all Python-native). Async by default. Auto-generates OpenAPI docs. |
| **SSE via `sse-starlette`** | Real-time agent reasoning stream. Simpler than WebSockets for unidirectional data. |
| **Pydantic v2** | Request/response validation. Structured output parsing from LLMs. |
| **`python-dotenv`** | Environment management. |

### AI / Agent Layer

| Technology | Why |
| :---- | :---- |
| **LangGraph** | State-machine-based agent orchestration. Explicit control flow (Profile → Discovery → Eligibility). Better than CrewAI for deterministic hackathon demos. Falls back gracefully. |
| **Groq API (llama-3.3-70b or gemma2-9b)** | Extremely fast inference (\~200 tok/s). Free tier is generous. Perfect for hackathon where speed \> quality. |
| **Google Gemini 2.5 Pro** | Fallback for complex reasoning (eligibility logic). Matches hackathon's suggested tooling. |
| **text-embedding-3-small (OpenAI)** or **Gemini text-embedding-004** | Scheme embeddings for vector search. |

### Data Layer

| Technology | Why |
| :---- | :---- |
| **Qdrant (self-hosted on Render or Qdrant Cloud free tier)** | Purpose-built vector DB. Payload filtering (filter by state, category, amount range). Free. Python client. |
| **Supabase** | Postgres \+ auth \+ storage \+ REST API in one click. Free tier is generous. Use for users, applications, status tracking. |

### External APIs

| Service | Purpose |
| :---- | :---- |
| **Twilio WhatsApp Sandbox** | Send real WhatsApp messages during demo. Free sandbox account works. |
| **Web Speech API** | Browser STT — no account needed. |
| **Groq API** | Fast LLM inference — free tier. |
| **Google Gemini API** | Reasoning \+ Vision OCR — free tier. |

### Deployment

| Service | What |
| :---- | :---- |
| **Vercel** | Next.js frontend. Auto-deploy from GitHub. Free. |
| **Render** | FastAPI backend \+ Qdrant (Docker). Free tier. |
| **Supabase Cloud** | Managed Postgres. Free tier. |

### Why NOT These Alternatives

- **LangChain without LangGraph:** Too much abstraction, unpredictable chains. LangGraph gives explicit state control.  
- **Pinecone:** Requires account setup, no self-hosting. Qdrant is faster to spin up.  
- **Firebase:** Supabase is more developer-friendly, has native Postgres, and better free tier.  
- **CrewAI:** Too autonomous for a demo — you want deterministic agent ordering, not agents deciding what to do.  
- **Streaming via WebSocket:** Overkill. SSE is simpler for server→client unidirectional updates.

---

## 8\. AI Components

### 8.1 LLM Orchestration (LangGraph)

The agent pipeline is a **directed graph**, not a chatbot loop:

\# Simplified LangGraph state machine

from langgraph.graph import StateGraph, END

class YojanaState(TypedDict):

    transcript: str

    language: str

    profile: dict

    candidate\_schemes: list\[dict\]

    eligible\_schemes: list\[dict\]

    selected\_scheme: dict | None

    agent\_logs: list\[dict\]

graph \= StateGraph(YojanaState)

graph.add\_node("extract\_profile", extract\_profile\_node)

graph.add\_node("discover\_schemes", discover\_schemes\_node)

graph.add\_node("check\_eligibility", check\_eligibility\_node)

graph.add\_node("generate\_summaries", generate\_summaries\_node)

graph.add\_edge("extract\_profile", "discover\_schemes")

graph.add\_edge("discover\_schemes", "check\_eligibility")

graph.add\_edge("check\_eligibility", "generate\_summaries")

graph.add\_edge("generate\_summaries", END)

graph.set\_entry\_point("extract\_profile")

app \= graph.compile()

**Why a directed graph, not autonomous agents:** In a hackathon demo, you need the pipeline to complete in 8–12 seconds. Autonomous agents that decide their own next step can loop, retry, or stall. A fixed graph guarantees consistent timing.

### 8.2 Profile Extraction Agent

**Type:** Single LLM call with structured output (JSON mode)

System: You are a profile extraction agent. Extract structured citizen data

from the user's natural language input. The user may speak in Hindi, 

Kannada, or English. Always output valid JSON.

Output schema:

{

  "age": int | null,

  "gender": "M" | "F" | "Other" | null,

  "state": str | null,

  "district": str | null,

  "income\_annual": int | null,

  "caste\_category": "General" | "OBC" | "SC" | "ST" | null,

  "occupation": str | null,

  "education": str | null,

  "business\_intent": str | null,

  "existing\_business": bool | null,

  "has\_bank\_account": bool | null,

  "disabilities": bool | null,

  "minority": bool | null

}

Rules:

\- Infer what you can (e.g., "Bengaluru" → state: "Karnataka")

\- Set null for anything not mentioned or inferable

\- Do NOT hallucinate values

**Where AI is genuinely useful:** Natural language to structured data in multiple languages. Traditional NER would fail on code-mixed Kannada-English.

### 8.3 RAG System (Scheme Discovery)

**Indexing Pipeline (pre-hackathon or Day 1 Morning):**

1\. Scrape \~150-200 schemes from MyScheme.gov.in

   \- Use Firecrawl or requests \+ BeautifulSoup

   \- Each scheme: title, description, eligibility, benefits, documents, 

     application\_url, ministry, category, state\_specific, deadline

2\. Chunk each scheme into sections:

   \- Full text (for embedding)

   \- Eligibility section (for filtering)

   \- Benefits section (for display)

3\. Embed with text-embedding-3-small (OpenAI) or Gemini embedding

   \- Dimension: 1536 (OpenAI) or 768 (Gemini)

   

4\. Upload to Qdrant with rich payload:

   {

     "vector": \[...\],

     "payload": {

       "scheme\_id": "pmegp",

       "title": "Prime Minister's Employment Generation Programme",

       "category": \["entrepreneurship", "manufacturing", "service"\],

       "target\_group": \["unemployed\_youth", "women", "sc\_st"\],

       "min\_age": 18,

       "max\_age": null,

       "max\_income": null,

       "states": \["all"\],

       "funding\_amount": 2500000,

       "ministry": "MSME",

       "deadline": "2026-03-31",

       "full\_text": "...",

       "eligibility\_text": "...",

       "benefits\_text": "...",

       "documents\_required": \["aadhaar", "pan", "bank\_passbook", ...\],

       "application\_url": "https://..."

     }

   }

**Retrieval Pipeline:**

async def discover\_schemes(profile: dict) \-\> list\[dict\]:

    \# Step 1: Build semantic query from profile

    query \= f"{profile.get('occupation', '')} {profile.get('business\_intent', '')} "

    query \+= f"age {profile.get('age', '')} {profile.get('state', '')} "

    query \+= f"income {profile.get('income\_annual', '')} {profile.get('gender', '')}"

    

    \# Step 2: Qdrant search with metadata filters

    filters \= \[\]

    if profile.get('state'):

        filters.append(

            FieldCondition(key="states", match=MatchAny(any=\["all", profile\['state'\]\]))

        )

    if profile.get('age'):

        filters.append(FieldCondition(key="min\_age", range=Range(lte=profile\['age'\])))

    

    results \= qdrant.search(

        collection\_name="schemes",

        query\_vector=embed(query),

        query\_filter=Filter(must=filters),

        limit=15

    )

    

    return \[hit.payload for hit in results\]

**Where AI is genuinely useful:** Semantic understanding of intent ("start a business" → entrepreneurship schemes) that keyword search cannot match. Metadata filtering handles hard constraints (age, state) with traditional logic — no need to waste LLM tokens on that.

### 8.4 Eligibility Reasoning Agent

**Type:** Batched LLM reasoning (process up to 5 schemes per call for speed)

System: You are an eligibility assessment agent. Given a citizen profile 

and a government scheme's eligibility criteria, determine if the citizen 

qualifies.

For each scheme, respond with:

{

  "scheme\_id": str,

  "eligible": "yes" | "likely" | "no",

  "confidence": 0-100,

  "reasoning": "Brief explanation of why eligible/ineligible",

  "missing\_info": \["field1", "field2"\]  // fields that would change assessment

}

Rules:

\- If a criterion cannot be verified due to missing profile data, 

  mark as "likely" with reduced confidence

\- Be conservative — marking someone eligible when they're not wastes 

  their time

\- Consider ALL criteria, not just the first match/mismatch

**Where traditional logic is better:** Simple threshold checks (age \>= 18, income \<= 200000\) should be pre-filtered in Qdrant payload filters, not sent to the LLM. Reserve LLM for nuanced eligibility reasoning ("must be a first-generation entrepreneur" — requires inference).

### 8.5 Multilingual Translation

**Strategy: Don't translate. Generate in-language.**

Rather than: English response → translate to Hindi (lossy, slow, doubles latency) Do: Set LLM system prompt to respond in the user's language directly.

language\_prompts \= {

    "en": "Respond in English.",

    "hi": "Respond in Hindi (Devanagari script). Use simple, everyday Hindi.",

    "kn": "Respond in Kannada (Kannada script). Use simple, everyday Kannada."

}

This is faster (one LLM call instead of two) and more natural.

### 8.6 Summary Agent

**Type:** Single LLM call per scheme (cacheable)

Generates a 3–4 sentence plain-language explanation of the scheme in the user's language. Cache results in Supabase keyed by scheme\_id \+ language.

### 8.7 Recommendation Ranking

**Hybrid ranking (AI \+ heuristic):**

def rank\_schemes(eligible\_schemes: list\[dict\]) \-\> list\[dict\]:

    for s in eligible\_schemes:

        \# Weighted score

        s\['final\_score'\] \= (

            s\['eligibility\_confidence'\] \* 0.5 \+          \# How sure are we they qualify

            min(s\['funding\_amount'\] / 1000000, 1.0) \* 30 \+ \# Higher funding \= better

            (10 if s\['deadline'\] and s\['deadline'\] \> today else 0\) \+  \# Active deadline bonus

            (5 if s\['state'\] \== user\_state else 0\)         \# State-specific bonus

        )

    return sorted(eligible\_schemes, key=lambda x: x\['final\_score'\], reverse=True)

**Where traditional logic is better:** Sorting and ranking are deterministic operations. Don't use an LLM for sorting — it's slower and less reliable.

---

## 9\. Database Schema

### Supabase (PostgreSQL)

\-- Users table (minimal for hackathon — no auth)

CREATE TABLE users (

    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),

    phone VARCHAR(15),

    name VARCHAR(255),

    profile JSONB DEFAULT '{}',

    \-- profile stores: {age, gender, state, district, income, caste, 

    \--                  occupation, education, business\_intent, ...}

    preferred\_language VARCHAR(2) DEFAULT 'en',

    created\_at TIMESTAMPTZ DEFAULT NOW()

);

\-- Schemes table (source of truth, synced from scraper)

CREATE TABLE schemes (

    id VARCHAR(100) PRIMARY KEY,  \-- e.g., "pm-mudra-shishu"

    title VARCHAR(500) NOT NULL,

    title\_hi VARCHAR(500),

    title\_kn VARCHAR(500),

    description TEXT,

    eligibility\_text TEXT,

    benefits\_text TEXT,

    funding\_amount BIGINT,  \-- in INR

    category VARCHAR(100)\[\],  \-- e.g., {"entrepreneurship", "women"}

    target\_group VARCHAR(100)\[\],

    ministry VARCHAR(255),

    state VARCHAR(100) DEFAULT 'all',  \-- 'all' for central schemes

    min\_age INT,

    max\_age INT,

    max\_income BIGINT,

    documents\_required VARCHAR(255)\[\],

    application\_url TEXT,

    deadline DATE,

    is\_active BOOLEAN DEFAULT TRUE,

    raw\_data JSONB,

    created\_at TIMESTAMPTZ DEFAULT NOW(),

    updated\_at TIMESTAMPTZ DEFAULT NOW()

);

\-- Applications (tracks what user applied for)

CREATE TABLE applications (

    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),

    user\_id UUID REFERENCES users(id),

    scheme\_id VARCHAR(100) REFERENCES schemes(id),

    status VARCHAR(50) DEFAULT 'draft',

    \-- status: draft | applied | under\_review | approved | rejected

    eligibility\_score INT,

    eligibility\_reasoning TEXT,

    form\_data JSONB DEFAULT '{}',

    applied\_at TIMESTAMPTZ,

    last\_checked TIMESTAMPTZ,

    status\_history JSONB DEFAULT '\[\]',

    \-- \[{status, timestamp, note}, ...\]

    created\_at TIMESTAMPTZ DEFAULT NOW()

);

\-- Conversations (for context continuity)

CREATE TABLE conversations (

    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),

    user\_id UUID REFERENCES users(id),

    transcript TEXT,

    extracted\_profile JSONB,

    schemes\_shown VARCHAR(100)\[\],

    language VARCHAR(2) DEFAULT 'en',

    agent\_logs JSONB DEFAULT '\[\]',

    created\_at TIMESTAMPTZ DEFAULT NOW()

);

\-- Scheme summaries cache (avoid re-generating)

CREATE TABLE scheme\_summaries (

    scheme\_id VARCHAR(100) REFERENCES schemes(id),

    language VARCHAR(2),

    summary TEXT,

    eligibility\_checklist JSONB,

    created\_at TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (scheme\_id, language)

);

\-- Indexes

CREATE INDEX idx\_schemes\_category ON schemes USING GIN (category);

CREATE INDEX idx\_schemes\_state ON schemes (state);

CREATE INDEX idx\_applications\_user ON applications (user\_id);

CREATE INDEX idx\_applications\_status ON applications (status);

### Qdrant Collection

from qdrant\_client.models import VectorParams, Distance

client.create\_collection(

    collection\_name="schemes",

    vectors\_config=VectorParams(

        size=1536,  \# text-embedding-3-small

        distance=Distance.COSINE

    )

)

\# Each point:

\# id: scheme\_id hash

\# vector: embedding of full scheme text

\# payload: all scheme fields for filtering \+ display

---

## 10\. API Design

### Base URL: `https://api.yojanasaathi.dev/v1`

### POST `/chat`

Primary endpoint. Runs the full agent pipeline.

**Request:**

{

  "message": "I am a 22 year old woman from Bangalore wanting to start a tailoring business",

  "language": "en",

  "session\_id": "uuid-optional",

  "stream": true

}

**Response (SSE stream):**

event: agent\_step

data: {"agent": "profile\_extractor", "status": "running", "message": "Extracting profile..."}

event: agent\_step

data: {"agent": "profile\_extractor", "status": "complete", "data": {"age": 22, "gender": "F", "state": "Karnataka", "business\_intent": "tailoring"}}

event: agent\_step

data: {"agent": "discovery", "status": "running", "message": "Searching 200 schemes..."}

event: agent\_step

data: {"agent": "discovery", "status": "complete", "data": {"candidates\_found": 14}}

event: agent\_step

data: {"agent": "eligibility", "status": "running", "message": "Checking eligibility for 14 schemes..."}

event: scheme\_result

data: {"scheme\_id": "pm-mudra-shishu", "title": "PM-MUDRA Shishu", "funding\_amount": 50000, "eligibility": "yes", "confidence": 95, "reasoning": "Meets all criteria: age, gender, business type"}

event: scheme\_result

data: {"scheme\_id": "pmegp", "title": "PMEGP", "funding\_amount": 2500000, "eligibility": "likely", "confidence": 78, "reasoning": "Meets age and business criteria. Income not confirmed."}

event: done

data: {"total\_eligible": 7, "session\_id": "abc-123"}

### GET `/schemes/{scheme_id}`

Get full scheme details with AI-generated summary.

**Request:** `GET /schemes/pm-mudra-shishu?language=hi`

**Response:**

{

  "id": "pm-mudra-shishu",

  "title": "प्रधानमंत्री मुद्रा योजना \- शिशु",

  "funding\_amount": 50000,

  "summary": "यह योजना छोटे व्यापारियों को ₹50,000 तक का ऋण प्रदान करती है...",

  "eligibility\_checklist": \[

    {"criterion": "Age 18+", "met": true, "note": "User is 22"},

    {"criterion": "Non-farm business", "met": true, "note": "Tailoring qualifies"},

    {"criterion": "No existing MUDRA loan", "met": null, "note": "Not confirmed"}

  \],

  "documents\_required": \["aadhaar", "pan", "business\_plan", "bank\_passbook"\],

  "application\_steps": \[

    "Visit nearest bank branch or MUDRA portal",

    "Fill MUDRA application form",

    "Attach required documents",

    "Submit and collect reference number"

  \],

  "application\_url": "https://www.mudra.org.in",

  "deadline": "2026-03-31",

  "ministry": "Ministry of Finance"

}

### POST `/schemes/compare`

Compare multiple schemes side by side.

**Request:**

{

  "scheme\_ids": \["pm-mudra-shishu", "pmegp", "standup-india"\],

  "language": "en"

}

**Response:**

{

  "comparison": \[

    {

      "field": "Funding Amount",

      "pm-mudra-shishu": "₹50,000",

      "pmegp": "₹25,00,000",

      "standup-india": "₹1,00,00,000"

    },

    {

      "field": "Eligibility Difficulty",

      "pm-mudra-shishu": "Easy",

      "pmegp": "Medium",

      "standup-india": "Hard"

    },

    {

      "field": "Documents Required",

      "pm-mudra-shishu": 4,

      "pmegp": 7,

      "standup-india": 10

    }

  \]

}

### POST `/apply`

Mock-submit an application and trigger WhatsApp notification.

**Request:**

{

  "user\_id": "uuid",

  "scheme\_id": "pm-mudra-shishu",

  "form\_data": {

    "name": "Priya Sharma",

    "age": 22,

    "aadhaar": "XXXX-XXXX-1234",

    "business\_type": "Tailoring"

  },

  "notify\_phone": "+919876543210"

}

**Response:**

{

  "application\_id": "YS-2026-4521",

  "status": "applied",

  "message": "Application submitted successfully",

  "whatsapp\_sent": true,

  "next\_steps": "You will receive status updates via WhatsApp"

}

### POST `/voice`

Process voice input directly (if Web Speech API unavailable).

**Request:** `multipart/form-data` with audio file

audio: \<wav/webm file\>

language: "hi"

**Response:**

{

  "transcript": "मैं 22 साल की हूं, बैंगलोर में...",

  "language\_detected": "hi",

  "redirect\_to": "/chat"

}

---

## 11\. Folder Structure

yojana-saathi/

├── README.md

├── PLAN.md                          \# This file

├── .env.example                     \# Environment variables template

│

├── frontend/                        \# Next.js 15 app

│   ├── package.json

│   ├── next.config.js

│   ├── tailwind.config.ts

│   ├── tsconfig.json

│   ├── public/

│   │   ├── icons/                   \# PWA icons

│   │   └── locales/

│   │       ├── en.json              \# English strings

│   │       ├── hi.json              \# Hindi strings

│   │       └── kn.json              \# Kannada strings

│   ├── src/

│   │   ├── app/

│   │   │   ├── layout.tsx           \# Root layout with providers

│   │   │   ├── page.tsx             \# Landing / search page

│   │   │   ├── schemes/

│   │   │   │   └── \[id\]/

│   │   │   │       └── page.tsx     \# Scheme detail page

│   │   │   ├── compare/

│   │   │   │   └── page.tsx         \# Scheme comparison

│   │   │   ├── track/

│   │   │   │   └── page.tsx         \# Application tracking

│   │   │   └── api/                 \# BFF routes (optional proxy)

│   │   │       └── proxy/

│   │   │           └── route.ts

│   │   ├── components/

│   │   │   ├── ui/                  \# shadcn/ui components

│   │   │   │   ├── button.tsx

│   │   │   │   ├── card.tsx

│   │   │   │   ├── badge.tsx

│   │   │   │   ├── dialog.tsx

│   │   │   │   ├── sheet.tsx

│   │   │   │   ├── progress.tsx

│   │   │   │   └── ...

│   │   │   ├── voice-button.tsx     \# Mic input component

│   │   │   ├── scheme-card.tsx      \# Scheme result card

│   │   │   ├── scheme-detail.tsx    \# Full scheme view

│   │   │   ├── agent-panel.tsx      \# Side panel reasoning trace

│   │   │   ├── search-input.tsx     \# Text query input

│   │   │   ├── language-toggle.tsx  \# EN/HI/KN switcher

│   │   │   ├── eligibility-badge.tsx

│   │   │   ├── timeline.tsx         \# Application status timeline

│   │   │   ├── comparison-table.tsx

│   │   │   └── hero-section.tsx

│   │   ├── hooks/

│   │   │   ├── use-voice.ts         \# Web Speech API hook

│   │   │   ├── use-chat-stream.ts   \# SSE consumer hook

│   │   │   └── use-language.ts      \# i18n hook

│   │   ├── lib/

│   │   │   ├── api.ts               \# Backend API client

│   │   │   ├── constants.ts

│   │   │   └── utils.ts

│   │   └── types/

│   │       └── index.ts             \# TypeScript interfaces

│   └── .env.local

│

├── backend/                         \# FastAPI application

│   ├── pyproject.toml               \# or requirements.txt

│   ├── Dockerfile

│   ├── main.py                      \# FastAPI app entry

│   ├── config.py                    \# Settings / env vars

│   ├── routers/

│   │   ├── chat.py                  \# /chat endpoint \+ SSE

│   │   ├── schemes.py               \# /schemes CRUD

│   │   ├── apply.py                 \# /apply \+ WhatsApp

│   │   ├── voice.py                 \# /voice processing

│   │   └── compare.py               \# /compare endpoint

│   ├── agents/

│   │   ├── orchestrator.py          \# LangGraph graph definition

│   │   ├── profile\_extractor.py     \# Profile extraction node

│   │   ├── discovery.py             \# Scheme discovery node

│   │   ├── eligibility.py           \# Eligibility reasoning node

│   │   ├── summary.py               \# Summary generation node

│   │   └── prompts.py               \# All LLM prompts (centralized)

│   ├── services/

│   │   ├── qdrant\_service.py        \# Vector DB operations

│   │   ├── supabase\_service.py      \# Database operations

│   │   ├── twilio\_service.py        \# WhatsApp messaging

│   │   ├── llm\_service.py           \# LLM client wrapper (Groq/Gemini)

│   │   └── embedding\_service.py     \# Embedding generation

│   ├── models/

│   │   ├── schemas.py               \# Pydantic models

│   │   └── db\_models.py             \# DB model definitions

│   └── data/

│       ├── seed\_schemes.json        \# Pre-scraped scheme data

│       └── demo\_profiles.json       \# Test user profiles

│

├── scripts/

│   ├── scrape\_schemes.py            \# MyScheme.gov.in scraper

│   ├── embed\_schemes.py             \# Generate \+ upload embeddings

│   ├── seed\_db.py                   \# Populate Supabase tables

│   └── test\_agents.py               \# Quick agent smoke test

│

├── data/

│   ├── raw/                         \# Raw scraped HTML/JSON

│   └── processed/                   \# Cleaned scheme JSON

│

└── docs/

    ├── architecture.png             \# Architecture diagram

    ├── demo-script.md               \# Word-for-word demo script

    └── pitch-deck.pdf               \# 5-slide pitch

---

## 12\. Vibecoding Execution Strategy

### Philosophy

**The goal is not to write code. The goal is to ship a working demo.** Every line of code that an AI agent can write in 30 seconds should not be written by a human in 30 minutes.

### What AI Coding Agents Should Generate

| What | Agent | Prompt Strategy |
| :---- | :---- | :---- |
| All shadcn/ui components | Cursor / Claude Code | "Generate a scheme card component using shadcn Card with props: title, amount, matchPercent, deadline, category. Use Tailwind. Include framer-motion fade-in." |
| API route handlers | Cursor / Claude Code | Paste the Pydantic model \+ endpoint spec from this doc. "Generate FastAPI endpoint matching this spec." |
| LangGraph node boilerplate | Claude Code | "Generate a LangGraph node function that takes YojanaState, calls Groq API with this prompt, and returns updated state." |
| Qdrant setup \+ search | Cursor | "Generate Qdrant collection creation and search functions using qdrant-client. Collection: schemes, vector size: 1536, cosine." |
| Twilio WhatsApp | Cursor | "Generate a function that sends a WhatsApp message via Twilio with scheme name and application ID." |
| SSE streaming | Claude Code | "Generate FastAPI SSE endpoint using sse-starlette that yields agent step events." |
| i18n JSON files | ChatGPT / Claude | "Translate these 30 UI strings from English to Hindi and Kannada. Output as JSON." |
| Supabase schema | Cursor | Paste the SQL from Section 9\. "Generate Supabase client functions for CRUD on these tables." |
| Demo data | Claude | "Generate 5 realistic Indian citizen profiles with varying demographics for testing a government scheme matcher." |

### What MUST Be Manually Coded / Reviewed

| What | Why |
| :---- | :---- |
| LangGraph graph topology | The agent flow order is your architecture decision. Don't let AI decide the graph shape. |
| LLM prompts (all in `prompts.py`) | Prompts are your IP. Write them yourself, test them, iterate. AI can draft v1 but you must tune. |
| SSE event naming \+ format | Frontend and backend must agree on event schema. Define it once in this doc, implement both sides to match. |
| Error handling in demo-critical paths | AI-generated code often has optimistic error handling. Add explicit try/except with fallback UI for the chat and voice flows. |
| Qdrant payload filtering logic | The filter conditions depend on your schema. AI will get the field names wrong if you don't specify them. |

### How to Avoid Agent Hallucinations

1. **Pin library versions.** AI agents will import from deprecated APIs. Use: `langgraph==0.2.x`, `qdrant-client==1.12.x`, `groq==0.11.x`. Put exact versions in `requirements.txt`.  
2. **Paste this doc as context.** When using Cursor or Claude Code, paste the relevant section of this PLAN.md as context. The more specific your input, the less the agent hallucinates.  
3. **One file at a time.** Don't ask "generate the entire backend." Ask "generate `backend/agents/profile_extractor.py` with this signature and this prompt."  
4. **Test immediately.** After every AI-generated file, run it. Don't batch-generate 10 files and debug them all at once.  
5. **Use Pydantic models as contracts.** Define all request/response schemas in `models/schemas.py` first. Then AI agents generate endpoint handlers that match the schema exactly.

### Breaking Work Into Isolated Modules

Each of these can be developed and tested independently:

Module 1: Scheme Data Pipeline

  Input: MyScheme.gov.in

  Output: seed\_schemes.json \+ Qdrant collection populated

  Test: "Query 'farmer loan karnataka' → returns PMFBY"

  Owner: M3

Module 2: Profile Extraction

  Input: "I'm a 22 year old..."

  Output: {age: 22, ...} JSON

  Test: 5 sample profiles in 3 languages

  Owner: M1

Module 3: Discovery \+ Eligibility Pipeline

  Input: profile JSON

  Output: ranked scheme list with scores

  Test: sample profile → expected schemes appear

  Owner: M1

Module 4: Frontend Shell

  Input: none

  Output: landing page, scheme cards, side panel, routing

  Test: renders with mock data

  Owner: M2

Module 5: SSE Integration

  Input: /chat request

  Output: streaming agent events → side panel renders

  Test: fire /chat → side panel animates → cards appear

  Owner: M1 \+ M2

Module 6: WhatsApp Notification

  Input: application submission

  Output: WhatsApp message on phone

  Test: POST /apply → phone buzzes

  Owner: M4

Module 7: Scheme Detail \+ Comparison

  Input: scheme\_id

  Output: rendered detail page

  Test: click card → detail loads

  Owner: M2

### Cursor-Specific Tips

- Use `.cursorrules` file in project root with: "This is a Next.js 15 \+ FastAPI \+ LangGraph project. Use shadcn/ui for UI. Use Tailwind. Use TypeScript for frontend, Python 3.12 for backend."  
- Keep `PLAN.md` open in a tab — Cursor reads open tabs as context.  
- Use Cursor's "Generate" (Cmd+K) inside files for inline code generation.  
- Use Cursor Chat for multi-file operations.

### Claude Code Tips

- Start sessions with: "Read PLAN.md first. We are building Yojana Saathi."  
- Use Claude Code for complex logic: agent graph, eligibility reasoning, SSE streaming.  
- Claude Code is better than Cursor for Python backend work.  
- Use it for writing and iterating on LLM prompts — it understands prompt engineering.

---

## 13\. Team Division (4 Members)

### Role Assignments

┌──────────────────────────────────────────────────────────────────┐

│                        M1 — AI Lead (Swastik)                   │

│                                                                  │

│  Owns: LangGraph orchestrator, all agent nodes, RAG pipeline,   │

│        prompt engineering, LLM service, embedding service        │

│                                                                  │

│  Files: backend/agents/\*, backend/services/llm\_service.py,      │

│         backend/services/qdrant\_service.py,                      │

│         backend/services/embedding\_service.py                    │

│                                                                  │

│  Skills needed: Python, LangGraph, prompt engineering, Qdrant    │

└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐

│                     M2 — Frontend Lead                           │

│                                                                  │

│  Owns: Next.js app, all components, voice hook, SSE consumer,   │

│        scheme pages, side panel, animations, i18n, responsive    │

│                                                                  │

│  Files: frontend/src/\*\*                                          │

│                                                                  │

│  Skills needed: React/Next.js, Tailwind, TypeScript, shadcn/ui  │

└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐

│                    M3 — Data \+ Action Lead                        │

│                                                                  │

│  Owns: Scheme scraping, data cleaning, Qdrant seeding,           │

│        form-fill agent logic, document OCR, demo data             │

│                                                                  │

│  Files: scripts/\*, data/\*, backend/agents/form\_filler.py (if     │

│         implemented), seed\_schemes.json                           │

│                                                                  │

│  Skills needed: Python, web scraping, data processing            │

└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐

│                M4 — Infra \+ Comms \+ Demo Lead                     │

│                                                                  │

│  Owns: Supabase setup, Twilio WhatsApp, FastAPI routers,         │

│        SSE endpoint, deployment (Vercel \+ Render), env vars,     │

│        demo script, pitch deck, video backup                     │

│                                                                  │

│  Files: backend/routers/\*, backend/main.py, backend/config.py,   │

│         backend/services/twilio\_service.py,                       │

│         backend/services/supabase\_service.py, docs/\*              │

│                                                                  │

│  Skills needed: DevOps, FastAPI, Twilio, presentation skills     │

└──────────────────────────────────────────────────────────────────┘

### Parallel Execution Strategy

Hour 0-2:   ALL members set up their environments simultaneously

            M1: Python env, LangGraph, Groq/Gemini API keys

            M2: Next.js scaffold, shadcn init, Tailwind config

            M3: Scraper environment, Firecrawl/BS4 setup

            M4: Supabase project, Twilio sandbox, Render account, 

                GitHub repo \+ CI

Hour 2-6:   Work in parallel — NO cross-dependencies yet

            M1: Build \+ test agents with mock data (hardcoded schemes)

            M2: Build UI shell with mock data (hardcoded JSON)

            M3: Scrape and clean schemes → produce seed\_schemes.json

            M4: Set up Supabase tables, write API route stubs,

                set up SSE endpoint skeleton

Hour 6:     SYNC POINT — Integration begins

            M3 delivers seed\_schemes.json → M1 loads into Qdrant

            M4 delivers API stubs → M2 connects frontend to real endpoints

            M1 delivers working agent pipeline → M4 wires into SSE

Hour 6-12:  Integration pairs

            M1 \+ M4: Agent pipeline → SSE → API endpoints

            M2 \+ M1: SSE consumer → side panel rendering

            M3: Starts form-fill mockup or OCR stretch goal

Hour 12+:   Full-stack integration, polish, demo prep

            All hands on demo-critical bug fixes

            M4 shifts to demo script, pitch deck, video backup

### Communication Protocol

- **Shared Slack/Discord channel** for all updates  
- **Every 2 hours:** 30-second standup message: "Done: X. Doing: Y. Blocked: Z."  
- **Mock data contract:** Agree on JSON shapes for schemes, profiles, and agent events in Hour 0\. Put them in `frontend/src/types/index.ts` and `backend/models/schemas.py`.  
- **API contract:** The API specs in Section 10 are the contract. Frontend and backend build against them independently. If either side needs to change the contract, post in channel first.

---

## 14\. Roadmap

### First 4 Hours — Foundation

**Priority:** Every member has their domain running independently with mock data.

| Member | Deliverable | Done When |
| :---- | :---- | :---- |
| M1 | Profile extraction agent works with 3 test inputs | Agent returns valid JSON for EN/HI/KN inputs |
| M2 | Landing page renders with mic button, scheme cards (mock data), side panel | UI looks good with hardcoded data |
| M3 | 100+ schemes scraped, cleaned, saved as JSON | `seed_schemes.json` exists with valid schema |
| M4 | Supabase tables created, FastAPI running with `/health`, SSE stub works | `curl /health` returns 200 |

### Day 1 (Hours 0–12) — Core Pipeline

**Priority:** The agent pipeline works end-to-end. Frontend consumes real data.

| Hour | M1 | M2 | M3 | M4 |
| :---- | :---- | :---- | :---- | :---- |
| 0–2 | Env setup, LangGraph scaffold | Next.js scaffold, shadcn init | Scraper setup | Supabase \+ Render \+ GitHub |
| 2–4 | Profile extraction agent | Voice button \+ search input | Scraping MyScheme.gov.in | Supabase schema \+ seed script |
| 4–6 | Discovery agent \+ Qdrant search | Scheme cards \+ side panel UI | Continue scraping \+ cleaning | FastAPI routers \+ SSE endpoint |
| 6–8 | Eligibility agent | Connect frontend to SSE stream | Embed schemes → Qdrant | Wire agents → SSE → API |
| 8–10 | Full pipeline test (input → cards) | Side panel rendering real agent events | Demo data: 5 test profiles | End-to-end test: API → frontend |
| 10–12 | Prompt tuning, edge cases | UI polish, animations | seed\_schemes.json final | Deploy v1 to Vercel \+ Render |

**Day 1 Exit Criteria:**

- [ ] Voice/text input → agent pipeline → scheme cards appear  
- [ ] Agent side panel shows real reasoning steps  
- [ ] At least 100 schemes in Qdrant  
- [ ] Deployed and accessible via URL

### Day 2 (Hours 12–24) — Action Layer \+ Polish

| Hour | M1 | M2 | M3 | M4 |
| :---- | :---- | :---- | :---- | :---- |
| 12–14 | Summary agent (scheme detail page) | Scheme detail page | Form auto-fill mockup | Twilio WhatsApp integration |
| 14–16 | Language-aware prompts (HI/KN) | Language toggle \+ i18n | OCR demo (stretch) | WhatsApp → /apply flow |
| 16–18 | Eligibility prompt tuning | Comparison page (stretch) | More schemes \+ cleaning | Application tracking UI data |
| 18–20 | Agent log improvements | Timeline component (stretch) | Demo data edge cases | Full deploy \+ env check |
| 20–22 | End-to-end testing | Responsive/mobile polish | Test all flows | Demo script draft |
| 22–24 | Bug fixes | Bug fixes | Bug fixes | Video backup recording |

**Day 2 Exit Criteria:**

- [ ] Scheme detail page with AI summary works  
- [ ] WhatsApp notification arrives on a real phone  
- [ ] Hindi and Kannada flows work  
- [ ] Application "submitted" state shows  
- [ ] Demo script finalized  
- [ ] Video backup recorded

### Final Polish Phase (Hours 24–28)

| Task | Owner | Time |
| :---- | :---- | :---- |
| 3 full dry-run demos | ALL | 1 hour |
| Fix demo-breaking bugs only | M1 \+ M2 | 1 hour |
| Pitch deck (5 slides) | M4 | 30 min |
| README with architecture diagram | M4 | 30 min |
| Prepare judge Q\&A answers | ALL | 30 min |
| Final deploy \+ smoke test | M4 | 30 min |

---

## 15\. UI/UX Design Direction

### Design Principles

1. **Not a chatbot.** This is a search \+ action dashboard. Chat is a means, not the interface.  
2. **Mobile-first.** Target users are on phones. Design at 375px width first.  
3. **Low-literacy friendly.** Large touch targets, visual indicators (✅/❌), minimal text, big numbers (₹50,000 in 32px+ type).  
4. **Voice-forward.** The mic button is the most prominent element on the landing page.

### Color Palette

Primary:        \#2563EB (Blue-600) — trust, government association

Secondary:      \#059669 (Emerald-600) — money, approval, eligibility

Accent:         \#F59E0B (Amber-500) — attention, CTA buttons

Background:     \#F8FAFC (Slate-50) — clean, modern

Surface:        \#FFFFFF — cards

Text Primary:   \#0F172A (Slate-900)

Text Secondary: \#64748B (Slate-500)

Success:        \#10B981 (Green-500)

Warning:        \#F59E0B (Amber-500)

Error:          \#EF4444 (Red-500)

Agent Panel BG: \#1E293B (Slate-800) — dark terminal-like feel

### Typography

Headings:   Inter or Plus Jakarta Sans — 700 weight

Body:       Inter — 400/500 weight

Agent Panel: JetBrains Mono or Fira Code — monospace

Hindi:      Noto Sans Devanagari (Google Fonts)

Kannada:    Noto Sans Kannada (Google Fonts)

### Landing Page Layout

┌─────────────────────────────────────────────┐

│  🇮🇳 Yojana Saathi        \[EN|हिं|ಕ\]       │  ← Header

├─────────────────────────────────────────────┤

│                                             │

│     Find every government rupee             │

│     you deserve                             │

│                                             │

│              ┌─────────┐                    │

│              │   🎤    │                    │  ← Giant mic button

│              │         │                    │     Pulsing animation

│              └─────────┘                    │

│         Tap to speak in your language        │

│                                             │

│  ┌─────────────────────────────────────┐    │

│  │ Or type: "I want to start a..."    │    │  ← Text fallback

│  └─────────────────────────────────────┘    │

│                                             │

│  Popular: 🏭 Business Loans  📚 Scholarships│  ← Quick-start chips

│           👩 Women Schemes  🌾 Farmer Aid   │

│                                             │

├─────────────────────────────────────────────┤

│  ₹45,000 Cr unclaimed  │  6,000+ schemes   │  ← Stats bar

│  200 schemes searchable │  3 languages       │

└─────────────────────────────────────────────┘

### Results Page Layout

┌──────────────────────────────────────────────────────────────┐

│  ← Back    Yojana Saathi                    \[EN|हिं|ಕ\]      │

├────────────────────────────────┬─────────────────────────────┤

│                                │  Agent Reasoning            │

│  Your Profile                  │  ─────────────              │

│  Age: 22 | Bangalore | F      │  🎤 Transcribed input       │

│  Intent: Tailoring business    │  🧠 Extracting profile...   │

│  \[Edit Profile\]                │  👤 Found: age=22, F, BLR   │

│                                │  🔍 Searching 200 schemes.. │

│  ─────────────────────         │  📋 14 candidates found     │

│                                │  ✅ Checking eligibility... │

│  7 Schemes Found               │  📊 7 eligible              │

│                                │  ⏱ Completed in 8.2s       │

│  ┌────────────────────────┐    │                             │

│  │ PM-MUDRA Shishu        │    │                             │

│  │ ₹50,000    95% match   │    │                             │

│  │ Deadline: Mar 2026     │    │                             │

│  │ \[View\] \[Auto-Apply\]    │    │                             │

│  └────────────────────────┘    │                             │

│                                │                             │

│  ┌────────────────────────┐    │                             │

│  │ PMEGP                  │    │                             │

│  │ ₹25,00,000  88% match  │    │                             │

│  │ Deadline: Mar 2026     │    │                             │

│  │ \[View\] \[Auto-Apply\]    │    │                             │

│  └────────────────────────┘    │                             │

│                                │                             │

│  ... more cards                │                             │

└────────────────────────────────┴─────────────────────────────┘

### Mobile Layout Adjustments

- Side panel becomes a bottom sheet (swipe up to see agent reasoning)  
- Scheme cards are full-width, stacked vertically  
- Mic button is 64px diameter, fixed bottom-center  
- Language toggle moves to hamburger menu  
- Touch targets minimum 48px

### Animations (Framer Motion)

\- Mic button: pulse animation when listening (scale 1.0 → 1.1, opacity 0.8 → 1.0)

\- Scheme cards: stagger fade-in from bottom (delay 0.1s each)

\- Agent steps: slide-in from right, one by one

\- Eligibility badges: pop-in with spring physics

\- Success state: confetti or checkmark animation

### Agent Side Panel Design

Dark background (\#1E293B)

Monospace font (JetBrains Mono)

Green text for success steps

Yellow for in-progress

Dim gray for upcoming

Each step:

  \[icon\] \[agent\_name\] ─── \[status\_text\]

  

  🎤 Transcription ─── "Naanu 22 varsha..."

  🧠 Profile Extraction ─── Extracting...  (spinner)

  👤 Profile ─── {age: 22, location: BLR, intent: tailoring}

  🔍 Discovery ─── Searching 200 schemes... (progress bar)

  📋 Candidates ─── 14 schemes found

  ✅ Eligibility ─── Checking... (7/14 complete)

  📊 Results ─── 7 eligible schemes ranked

  ⏱ Time ─── 8.2 seconds

---

## 16\. Demo Strategy

### The 90-Second Script (Word for Word)

**\[SLIDE 1 — Title: "Yojana Saathi"\]**

**Speaker:** *"India spends 15 lakh crore rupees on government schemes every year. And every year, 45,000 crore goes unclaimed. Not because people don't qualify — because they can't find the schemes that were built for them."*

**\[SLIDE 2 — Problem: MyScheme.gov.in screenshot\]**

**Speaker:** *"Here's MyScheme.gov.in. Try finding a scholarship for your domestic help's daughter."* **Pause 3 seconds.** *"That's what millions of Indians face. Dense English. Scattered portals. Dozens of forms."*

**\[SWITCH TO LIVE APP\]**

**Speaker:** *"We built Yojana Saathi — an autonomous citizen advocate."*

**\[TAP MIC — SPEAK IN HINDI/KANNADA\]**

**Speaker speaks into the app:** *"Main 22 saal ki hoon, Bangalore mein tailoring ka business shuru karna chahti hoon"*

**\[AGENT PANEL LIGHTS UP — STEPS STREAM IN\]**

**Speaker:** *"Watch the right panel. Five AI agents are working right now. Profile extraction — it understands Hindi naturally. Discovery — searching 200 schemes semantically. Eligibility — reasoning through each scheme's criteria."*

**\[SCHEME CARDS APPEAR\]**

**Speaker:** *"Seven schemes found. PM-MUDRA at 95% match — ₹50,000 loan. PMEGP — ₹25 lakh. Let me click MUDRA."*

**\[CLICK SCHEME — DETAIL PAGE\]**

**Speaker:** *"AI-generated summary in Hindi. Eligibility checklist — green means she qualifies. One click to auto-apply."*

**\[CLICK AUTO-APPLY\]**

**Speaker:** *"Application submitted. And..."* **Point to judge's phone.** *"Check your WhatsApp."*

**\[JUDGE'S PHONE BUZZES WITH WHATSAPP MESSAGE\]**

**Speaker:** *"Real notification. Real action. Not a chatbot."*

**\[SLIDE 3 — Architecture: 5 agents diagram\]**

**Speaker:** *"Five specialized agents — profile, discovery, eligibility, summary, notification — orchestrated by LangGraph. Multi-agent, action-oriented. Built in 48 hours."*

**\[SLIDE 4 — Impact\]**

**Speaker:** *"We didn't build a search engine. We built an autonomous citizen advocate. Imagine this in every panchayat, every CSC center, every NGO. That's Yojana Saathi."*

### What Judges Care About (and What to Emphasize)

| Judge Concern | How We Address It |
| :---- | :---- |
| "Is this just a chatbot?" | No. Show the action layer: forms filled, WhatsApp sent. Emphasize "action, not answers." |
| "Does the AI actually do something?" | Agent panel shows real reasoning. WhatsApp is tangible proof. |
| "Is this technically impressive?" | Multi-agent architecture with 5 agents, RAG, SSE streaming, voice. |
| "Is this feasible / real?" | Demo uses real scheme data from MyScheme.gov.in. Real WhatsApp message. |
| "Does this solve a real problem?" | ₹45,000 crore unclaimed. 1.4B citizens. Cite Haqdarshak as comparable. |
| "Can this scale?" | RAG scales to 6,000+ schemes. Multi-language. PWA works offline (stretch). |

### Fallback Demo Plan (If APIs Fail)

1. **Pre-record a 2-minute video** of the full demo flow on Day 2 evening. Screen-record with Loom.  
2. **Hardcode one golden path** — a specific input that always returns the same 7 schemes from a local JSON file, bypassing the LLM entirely. Wire a `DEMO_MODE=true` env var.  
3. **Pre-send the WhatsApp message** 30 seconds before the demo. Have someone text you when they see it, then "reveal" it.  
4. **Have screenshots** of every screen as slides if everything crashes.

**DEMO\_MODE implementation:**

\# backend/config.py

DEMO\_MODE \= os.getenv("DEMO\_MODE", "false").lower() \== "true"

\# backend/agents/orchestrator.py

if DEMO\_MODE:

    return load\_demo\_response()  \# Pre-computed JSON

---

## 17\. Risk Management

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
| :---- | :---- | :---- | :---- |
| Groq/Gemini API rate limit during demo | Medium | Critical | Pre-cache responses for demo profile. DEMO\_MODE fallback. Have backup API key. |
| Web Speech API fails in noisy demo hall | High | High | Text input always available. Pre-type the demo query as backup. |
| Qdrant on Render is slow (cold start) | Medium | Medium | Send a warmup query 5 min before demo. Or use Qdrant Cloud free tier. |
| LLM returns wrong eligibility | Medium | Medium | Pre-validate the demo schemes manually. Hardcode overrides for the 3 demo schemes if needed. |
| Twilio WhatsApp sandbox doesn't send | Medium | High | Test 1 hour before demo. Have backup phone with pre-received message. |
| Vercel/Render deployment fails | Low | Critical | Deploy early (Day 1). Keep a working commit tagged. Local fallback with ngrok. |
| SSE doesn't work in demo browser | Low | Medium | Polling fallback. Or just show the side panel with animated static data. |

### Scope Risks

| Risk | Mitigation |
| :---- | :---- |
| Team tries to build everything | **Enforce P0/P1/P2 discipline.** Nothing P1 until ALL P0 works. Print the priority stack and tape it to the wall. |
| Scheme scraping takes too long | Cap at 100 schemes. Quality \> quantity. Manually curate 20 high-profile schemes as fallback. |
| Form auto-fill is too complex | Mock it. Show a pre-filled form screenshot. Don't build real Playwright automation. |
| Multi-language prompts need tuning | Default to English. Add Hindi as primary demo language. Kannada is stretch. |

### API Risks

| API | Risk | Fallback |
| :---- | :---- | :---- |
| Groq | Rate limit (30 req/min on free) | Switch to Gemini. Or use local Ollama with llama3.2 (if machine supports it). |
| Gemini | Quota exhaustion | Switch to Groq. |
| Twilio | Sandbox expiry | Re-register. Or use a pre-sent message screenshot. |
| Web Speech API | Browser compatibility | Use Chrome only for demo. Test beforehand. |
| Qdrant Cloud | Free tier limits | Self-host on Render (Docker). |

---

## 18\. Future Scope

### Short-Term (Post-Hackathon, 1–3 Months)

- Expand scheme database to 1,000+ schemes (all central \+ Karnataka state)  
- Add real form submission for 10 high-impact schemes (MUDRA, PMEGP, NSP, etc.)  
- DigiLocker integration for automatic document fetch  
- Progressive Web App with offline scheme browsing  
- User authentication with phone OTP

### Medium-Term (3–12 Months)

- Partner with 5–10 CSC (Common Service Center) centers for pilot  
- Add 5+ regional languages (Tamil, Telugu, Bengali, Marathi, Gujarati)  
- Build scheme success-rate analytics from anonymized user data  
- AI voice agent for phone-based access (no smartphone needed)  
- Integration with state e-governance portals  
- WhatsApp bot interface (no web app needed)

### Startup Path

- **Revenue model:** Freemium (free discovery, paid auto-apply \+ tracking), B2G licensing to state governments, B2B to CSR departments  
- **Comparable:** Haqdarshak (₹100Cr+ raised, but no AI agents), SahajSeva, MyScheme (government's own, limited UX)  
- **Differentiator:** Multi-agent autonomous workflow vs. static directory  
- **TAM:** 1.4B citizens × \~200 applicable schemes per demographic cluster \= massive  
- **First market:** Karnataka (home state advantage, Kannada support built-in)

### Open Source Path

- Release the scheme dataset as public good  
- Open-source the RAG \+ eligibility pipeline  
- Let NGOs, state govts, and civic-tech orgs deploy their own instances  
- Build a community around scheme data quality

### Research Path

- Paper: "Agentic Systems for Civic Infrastructure: Multi-Agent Scheme Discovery and Application"  
- Venue: AAAI, NeurIPS workshop on AI for Social Good, ACM DEV  
- Focus: multilingual profile extraction accuracy, eligibility reasoning correctness, RAG retrieval quality on government documents

### Government Partnership Path

- Pitch to Ministry of Electronics and IT (MeitY) under Digital India  
- Integrate with UMANG app ecosystem  
- Partner with National Informatics Centre (NIC)  
- State-level deployment through IT departments

---

## Appendix A: Environment Variables

\# .env.example

\# LLM APIs

GROQ\_API\_KEY=gsk\_xxxxxxxxxxxx

GEMINI\_API\_KEY=AIzaSyxxxxxxxxxx

OPENAI\_API\_KEY=sk-xxxxxxxxxxxx        \# for embeddings only

\# Vector DB

QDRANT\_URL=https://xxx.qdrant.io      \# or http://localhost:6333

QDRANT\_API\_KEY=xxxxxxxxxxxx           \# if using Qdrant Cloud

\# Database

SUPABASE\_URL=https://xxx.supabase.co

SUPABASE\_ANON\_KEY=eyJxxxxxxxx

SUPABASE\_SERVICE\_KEY=eyJxxxxxxxx      \# for backend use only

\# Notifications

TWILIO\_ACCOUNT\_SID=ACxxxxxxxx

TWILIO\_AUTH\_TOKEN=xxxxxxxx

TWILIO\_WHATSAPP\_FROM=whatsapp:+14155238886  \# sandbox number

DEMO\_PHONE\_NUMBER=+919876543210

\# App Config

DEMO\_MODE=false

DEFAULT\_LANGUAGE=en

BACKEND\_URL=https://api.yojanasaathi.dev

FRONTEND\_URL=https://yojanasaathi.vercel.app

## Appendix B: Key Pydantic Models

\# backend/models/schemas.py

from pydantic import BaseModel

from typing import Optional

class ChatRequest(BaseModel):

    message: str

    language: str \= "en"

    session\_id: Optional\[str\] \= None

    stream: bool \= True

class UserProfile(BaseModel):

    age: Optional\[int\] \= None

    gender: Optional\[str\] \= None

    state: Optional\[str\] \= None

    district: Optional\[str\] \= None

    income\_annual: Optional\[int\] \= None

    caste\_category: Optional\[str\] \= None

    occupation: Optional\[str\] \= None

    education: Optional\[str\] \= None

    business\_intent: Optional\[str\] \= None

    existing\_business: Optional\[bool\] \= None

    has\_bank\_account: Optional\[bool\] \= None

    disabilities: Optional\[bool\] \= None

    minority: Optional\[bool\] \= None

class SchemeResult(BaseModel):

    scheme\_id: str

    title: str

    funding\_amount: int

    eligibility: str  \# "yes" | "likely" | "no"

    confidence: int  \# 0-100

    reasoning: str

    category: list\[str\]

    deadline: Optional\[str\] \= None

class AgentStep(BaseModel):

    agent: str

    status: str  \# "running" | "complete" | "error"

    message: str

    data: Optional\[dict\] \= None

class ApplicationRequest(BaseModel):

    user\_id: str

    scheme\_id: str

    form\_data: dict

    notify\_phone: Optional\[str\] \= None

class ApplicationResponse(BaseModel):

    application\_id: str

    status: str

    message: str

    whatsapp\_sent: bool

## Appendix C: Sample LLM Prompts

### Profile Extraction Prompt

You are a government scheme eligibility profile extractor for Indian citizens.

Given a user's natural language description of themselves (which may be in English, 

Hindi, or Kannada), extract a structured profile.

RULES:

1\. Infer location details (e.g., "Bengaluru" → state: "Karnataka", district: "Bangalore Urban")

2\. Infer gender from name or language cues if stated

3\. Map education to standard levels: "10th pass", "12th pass", "Graduate", "Post-Graduate", "PhD", "Below 10th"

4\. Set null for anything not mentioned — NEVER guess

5\. Convert any income mentioned to annual (monthly × 12\)

6\. "SC/ST/OBC" → caste\_category. "General" if not mentioned \= null (don't assume)

OUTPUT: Valid JSON matching the UserProfile schema. No additional text.

### Eligibility Assessment Prompt

You are a government scheme eligibility assessor. You will receive:

1\. A citizen's profile (JSON)

2\. A scheme's eligibility criteria (text)

Assess whether the citizen qualifies for this scheme.

RESPOND with JSON:

{

  "eligible": "yes" | "likely" | "no",

  "confidence": 0-100,

  "reasoning": "Brief 1-2 sentence explanation",

  "criteria\_met": \["criterion1", "criterion2"\],

  "criteria\_not\_met": \["criterion3"\],

  "criteria\_unknown": \["criterion4"\],

  "missing\_info": \["field that would help assess"\]

}

RULES:

\- "yes" (80-100 confidence): All stated criteria are met

\- "likely" (50-79 confidence): Most criteria met, some unverifiable due to missing data

\- "no" (0-49 confidence): One or more hard criteria are clearly not met

\- Be CONSERVATIVE: if unsure, say "likely" not "yes"

\- Check ALL criteria, don't stop at the first match/mismatch

### Scheme Summary Prompt

You are a plain-language government scheme explainer for Indian citizens.

Given a scheme's official description, generate a clear, simple summary that 

a person with basic education can understand.

RESPOND in {language}.

FORMAT:

\- 3-4 sentences maximum

\- Use simple words (avoid: "beneficiary", "disbursement", "pursuant to")

\- Lead with what the person GETS (money amount, benefit)

\- Then who qualifies (1 sentence)

\- Then how to apply (1 sentence)

\- Include the deadline if applicable

EXAMPLE (English):

"This scheme gives loans up to ₹50,000 to people who want to start a small 

business. Anyone above 18 who doesn't have a business loan already can apply. 

Visit your nearest bank with your Aadhaar and a simple business plan. 

The scheme is available until March 2026."

---

*This document is the single source of truth for the Yojana Saathi hackathon build. When in doubt, refer here. When using AI coding agents, paste the relevant section as context. Good luck.*  
