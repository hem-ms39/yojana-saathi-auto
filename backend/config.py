from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Always the repo-root .env, whatever the current working directory is.
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    groq_api_key: str | None = None
    groq_model: str = "openai/gpt-oss-20b"
    gemini_api_key: str | None = None
    openai_api_key: str | None = None

    qdrant_url: str | None = None
    qdrant_api_key: str | None = None

    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_key: str | None = None

    # Meta WhatsApp Cloud API (developers.facebook.com → your app → WhatsApp → API Setup)
    whatsapp_access_token: str | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_api_version: str = "v26.0"
    # Approved template for the login code (code = body variable {{1}}). Without it the
    # code is sent as free text, which WhatsApp only allows within 24 hours of the user
    # last messaging our number.
    whatsapp_otp_template: str | None = None
    whatsapp_otp_template_has_button: bool = True  # Authentication templates have a copy-code button
    whatsapp_template_language: str = "en_US"
    demo_phone_number: str | None = None

    app_name: str = "Yojana Saathi Backend"
    demo_mode: bool = False
    default_language: str = "en"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    m3_api_url: str = "http://localhost:8001"

    collection_name: str = "schemes"
    embedding_size: int = 1536
    search_limit: int = 12

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
