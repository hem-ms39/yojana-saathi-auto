from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routers import (
    apply,
    auth,
    chat,
    compare,
    explain,
    forms,
    health,
    scheme_chat,
    schemes,
    voice,
)

app = FastAPI(title="Yojana Saathi API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_static_dir = Path(__file__).resolve().parent / "static"
(_static_dir / "screenshots").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

app.include_router(health.router)
app.include_router(chat.router, prefix="/v1")
app.include_router(schemes.router, prefix="/v1")
app.include_router(compare.router, prefix="/v1")
app.include_router(forms.router, prefix="/v1")
app.include_router(apply.router, prefix="/v1")
app.include_router(voice.router, prefix="/v1")
app.include_router(explain.router, prefix="/v1")
app.include_router(scheme_chat.router, prefix="/v1")
app.include_router(auth.router)
