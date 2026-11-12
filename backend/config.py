from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
    openai_api_key: str | None = None

    qdrant_url: str | None = None
    qdrant_api_key: str | None = None

    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_key: str | None = None

    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_whatsapp_from: str | None = None
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
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
