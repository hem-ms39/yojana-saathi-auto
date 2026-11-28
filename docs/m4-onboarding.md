# M4 Onboarding

## Scope

M4 owns infrastructure, communications, and demo readiness:

- Supabase project and schema bootstrap
- WhatsApp integration (Meta WhatsApp Cloud API)
- FastAPI routers and SSE endpoint
- Deployment on Render and Vercel
- Environment variables and final smoke checks
- Demo script, pitch deck, and backup recording

## Immediate Success Criteria

- `GET /health` returns `200`
- `POST /v1/chat` streams SSE events
- `POST /v1/apply` can trigger a WhatsApp message
- `.env` and `frontend/.env.local` exist with valid secrets

## Local Start

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup_m4.ps1
.\venv\Scripts\python -m uvicorn backend.main:app --reload
```

In a second terminal:

```powershell
cd frontend
cmd /c npm run dev
```
