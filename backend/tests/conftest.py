"""Shared fixtures. Tests run fully offline: no API keys, no Supabase, no Qdrant."""
import os

import pytest
from fastapi.testclient import TestClient

# Force "not configured" for every external service before the app is imported.
for key in [
    "GROQ_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "QDRANT_URL", "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
]:
    os.environ.pop(key, None)
os.environ["M3_API_URL"] = "http://127.0.0.1:9"  # unreachable on purpose


@pytest.fixture(scope="session")
def client() -> TestClient:
    from backend.main import app

    return TestClient(app)
