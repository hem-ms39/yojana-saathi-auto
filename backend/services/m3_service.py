from __future__ import annotations

import importlib.util
from functools import lru_cache
from pathlib import Path
from typing import Any

import httpx

from backend.config import settings


class M3Service:
    def __init__(self) -> None:
        self.base_url = settings.m3_api_url.rstrip("/")

    async def healthcheck(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                data = response.json()
                return data.get("status") == "ok"
        except Exception:
            return self._has_local_workspace()

    async def prefill_form(self, scheme_id: str, user_profile: dict[str, Any]) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/forms/prefill",
                    json={"scheme_id": scheme_id, "user_profile": user_profile},
                )
                response.raise_for_status()
                return response.json()
        except Exception:
            form_filler = self._load_module(
                "m3_form_filler",
                self._workspace_root() / "backend" / "agents" / "form_filler.py",
            )
            return form_filler.generate_prefilled_form(scheme_id, user_profile)

    async def list_forms(self) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{self.base_url}/forms")
                response.raise_for_status()
                return response.json()
        except Exception:
            form_filler = self._load_module(
                "m3_form_filler",
                self._workspace_root() / "backend" / "agents" / "form_filler.py",
            )
            available_forms = form_filler.list_available_forms()
            return {"available_forms": available_forms, "total": len(available_forms)}

    async def get_form(self, scheme_id: str) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(f"{self.base_url}/forms/{scheme_id}")
                response.raise_for_status()
                return response.json()
        except Exception:
            form_filler = self._load_module(
                "m3_form_filler",
                self._workspace_root() / "backend" / "agents" / "form_filler.py",
            )
            template = form_filler.get_form_template(scheme_id)
            if not template:
                raise RuntimeError(f"No form template for scheme: {scheme_id}")
            return template

    async def ocr_extract_and_fill(
        self,
        *,
        filename: str,
        content: bytes,
        content_type: str,
        scheme_id: str,
        doc_type: str,
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/ocr/extract-and-fill",
                    files={"file": (filename, content, content_type)},
                    data={"scheme_id": scheme_id, "doc_type": doc_type},
                )
                response.raise_for_status()
                return response.json()
        except Exception:
            ocr_agent = self._load_module(
                "m3_ocr_agent",
                self._workspace_root() / "backend" / "agents" / "ocr_agent.py",
            )
            form_filler = self._load_module(
                "m3_form_filler",
                self._workspace_root() / "backend" / "agents" / "form_filler.py",
            )

            ocr_result = ocr_agent.extract_from_bytes(content, content_type, doc_type)
            if ocr_result.get("status") == "error":
                raise RuntimeError(ocr_result.get("error", "M3 OCR failed"))

            user_profile = ocr_agent.map_to_user_profile(ocr_result)
            form = form_filler.generate_prefilled_form(scheme_id, user_profile)
            return {
                "pipeline": "ocr_to_form",
                "status": "success",
                "filename": filename,
                "document": {
                    "type": ocr_result.get("document_type"),
                    "confidence": ocr_result.get("confidence"),
                    "warnings": ocr_result.get("warnings", []),
                },
                "user_profile": user_profile,
                "form": form,
                "summary": {
                    "auto_filled": form.get("auto_filled_count", 0),
                    "total_fields": form.get("total_fields", 0),
                    "fill_percentage": form.get("fill_percentage", 0),
                    "missing_required": [
                        f["label"]
                        for f in form.get("fields", [])
                        if f.get("required") and not f.get("value")
                    ],
                },
            }

    @staticmethod
    def _workspace_root() -> Path:
        return Path(__file__).resolve().parents[2] / "m3_workspace"

    @classmethod
    def _has_local_workspace(cls) -> bool:
        return (cls._workspace_root() / "backend" / "agents" / "form_filler.py").exists()

    @staticmethod
    @lru_cache(maxsize=4)
    def _load_module(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load M3 module: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
