from __future__ import annotations

import json
import re
from collections.abc import Iterator
from typing import Any

from backend.config import settings

try:
    from groq import Groq
except Exception:
    Groq = None


class LLMService:
    def __init__(self) -> None:
        self._client = None
        if Groq and settings.groq_api_key:
            try:
                self._client = Groq(api_key=settings.groq_api_key)
            except TypeError:
                # Common with incompatible httpx versions; caller falls back gracefully.
                self._client = None
        self._model = "llama-3.1-8b-instant"

    @property
    def enabled(self) -> bool:
        return self._client is not None and not settings.demo_mode

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        if not self.enabled:
            return "LLM unavailable; using deterministic MVP fallback."

        completion = self._client.chat.completions.create(
            model=self._model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content or ""

    def generate_text_stream(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.4
    ) -> Iterator[str]:
        """Yield LLM response tokens one-by-one for SSE streaming."""
        if not self.enabled:
            yield "Eligibility explanation unavailable (LLM not configured)."
            return

        stream = self._client.chat.completions.create(
            model=self._model,
            temperature=temperature,
            stream=True,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        text = self.generate_text(system_prompt, user_prompt, temperature=0)
        if not self.enabled:
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Fallback for models that wrap JSON in markdown/code-fences.
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
        if fenced:
            try:
                return json.loads(fenced.group(1))
            except json.JSONDecodeError:
                pass

        # Last-resort: pick first JSON-looking object.
        object_match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if object_match:
            try:
                return json.loads(object_match.group(0))
            except json.JSONDecodeError:
                pass
        return {}

