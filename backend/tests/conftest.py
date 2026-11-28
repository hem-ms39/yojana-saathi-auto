"""Shared fixtures. Tests run fully offline: no API keys, no Supabase, no Qdrant."""
import os

import pytest
from fastapi.testclient import TestClient

# Force "not configured" for every external service before the app is imported.
# Set to "" rather than removed: real environment variables override the
# repo-root .env, so a developer's local keys are never used by tests.
for key in [
    "GROQ_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY",
    "SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY",
    "WHATSAPP_ACCESS_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "WHATSAPP_OTP_TEMPLATE",
]:
    os.environ[key] = ""
os.environ["M3_API_URL"] = "http://127.0.0.1:9"  # unreachable on purpose


@pytest.fixture(scope="session")
def client() -> TestClient:
    from backend.main import app

    return TestClient(app)
