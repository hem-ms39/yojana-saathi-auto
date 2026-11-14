# Deployment Notes

## Render Backend

- Runtime: Docker or Python 3.12
- Start command: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 10000`
- Health endpoint: `/health`
- Required env vars: Supabase, Twilio, LLM, Qdrant, `FRONTEND_URL`, `BACKEND_URL`

## Vercel Frontend

- Root directory: `frontend`
- Required env var: `NEXT_PUBLIC_BACKEND_URL`

## Pre-Demo Smoke Test

1. `GET /health`
2. `POST /v1/chat`
3. `POST /v1/apply`
4. Verify one WhatsApp notification on the demo phone
