from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from supabase import Client, create_client

from backend.config import settings


class SupabaseService:
    def __init__(self) -> None:
        self.client: Client | None = None
        if settings.supabase_url and settings.supabase_service_key:
            self.client = create_client(settings.supabase_url, settings.supabase_service_key)

    @property
    def is_configured(self) -> bool:
        return self.client is not None

    def healthcheck(self) -> bool:
        if not self.client:
            return False

        self.client.table("users").select("id", count="exact").limit(1).execute()
        return True

    def get_scheme(self, scheme_id: str) -> dict[str, Any] | None:
        if self.client:
            try:
                response = self.client.table("schemes").select("*").eq("id", scheme_id).limit(1).execute()
                if response.data:
                    return response.data[0]
            except Exception:
                pass

        return self._get_scheme_from_seed(scheme_id)

    def list_schemes(self, scheme_ids: list[str]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for scheme_id in scheme_ids:
            scheme = self.get_scheme(scheme_id)
            if scheme:
                results.append(scheme)
        return results

    def create_application(
        self,
        *,
        application_id: str,
        user_id: str,
        scheme_id: str,
        form_data: dict,
        eligibility_score: int | None = None,
        eligibility_reasoning: str | None = None,
    ) -> bool:
        if not self.client:
            return False

        normalized_user_id: str | None = None
        try:
            normalized_user_id = str(UUID(user_id))
        except ValueError:
            normalized_user_id = None

        timestamp = datetime.now(UTC).isoformat()
        payload = {
            "user_id": normalized_user_id,
            "scheme_id": scheme_id,
            "status": "applied",
            "eligibility_score": eligibility_score,
            "eligibility_reasoning": eligibility_reasoning,
            "form_data": {
                **form_data,
                "_public_application_id": application_id,
                "_submitted_user_id": user_id,
            },
            "applied_at": timestamp,
            "status_history": [
                {
                    "status": "applied",
                    "timestamp": timestamp,
                    "note": "Application submitted from Yojana Saathi demo flow.",
                }
            ],
        }

        try:
            self.client.table("applications").insert(payload).execute()
            return True
        except Exception:
            return False

    def seed_schemes(self, schemes: list[dict[str, Any]]) -> int:
        if not self.client:
            raise RuntimeError("Supabase is not configured.")

        rows = [self._map_scheme_for_supabase(scheme) for scheme in schemes]
        self.client.table("schemes").upsert(rows).execute()
        return len(rows)

    def _get_scheme_from_seed(self, scheme_id: str) -> dict[str, Any] | None:
        for path in self._seed_paths():
            if not path.exists():
                continue
            try:
                schemes = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            for scheme in schemes:
                if scheme.get("scheme_id") == scheme_id or scheme.get("id") == scheme_id:
                    return self._map_scheme_for_supabase(scheme)
        return None

    @staticmethod
    def _map_scheme_for_supabase(scheme: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": scheme.get("scheme_id") or scheme.get("id"),
            "title": scheme.get("title"),
            "title_hi": scheme.get("title_hi"),
            "title_kn": scheme.get("title_kn"),
            "description": scheme.get("description"),
            "eligibility_text": scheme.get("eligibility_text") or scheme.get("eligibility"),
            "benefits_text": scheme.get("benefits_text") or scheme.get("benefits"),
            "funding_amount": scheme.get("funding_amount"),
            "category": scheme.get("category", []),
            "target_group": scheme.get("target_group", []),
            "ministry": scheme.get("ministry"),
            "state": scheme.get("state", "all"),
            "min_age": scheme.get("min_age"),
            "max_age": scheme.get("max_age"),
            "max_income": scheme.get("max_income"),
            "documents_required": scheme.get("documents_required", []),
            "application_url": scheme.get("application_url") or scheme.get("apply_url"),
            "deadline": scheme.get("deadline"),
            "raw_data": scheme,
        }

    @staticmethod
    def _seed_paths() -> list[Path]:
        root = Path(__file__).resolve().parents[2]
        return [
            root / "backend" / "data" / "seed_schemes.json",
            root / "data" / "processed" / "seed_schemes.json",
            root / "m3_workspace" / "backend" / "data" / "seed_schemes.json",
            root / "m3_workspace" / "data" / "processed" / "seed_schemes.json",
        ]
