from __future__ import annotations

import hashlib
import logging
import math

from backend.config import settings

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class EmbeddingService:
    """Embedding service using Gemini text-embedding-001.

    Falls back to deterministic hash-based embeddings when Gemini is
    unavailable (missing API key or import error).
    """

    GEMINI_MODEL = "models/gemini-embedding-001"
    GEMINI_DIM = 3072

    def __init__(self, size: int | None = None) -> None:
        self._use_gemini = False

        if genai and settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self._use_gemini = True
                self.size = size or self.GEMINI_DIM
                logger.info("EmbeddingService: using Gemini embeddings (%d-dim)", self.size)
            except Exception as exc:
                logger.warning("Gemini embedding init failed (%s), using hash fallback", exc)
                self.size = size or settings.embedding_size
        else:
            self.size = size or settings.embedding_size
            logger.info("EmbeddingService: using hash-based fallback (%d-dim)", self.size)

    def embed_text(self, text: str, task_type: str = "retrieval_document") -> list[float]:
        """Embed text for storage (documents/schemes)."""
        if not text.strip():
            return [0.0] * self.size

        if self._use_gemini:
            return self._gemini_embed(text, task_type)
        return self._hash_embed(text)

    def embed_query(self, text: str) -> list[float]:
        """Embed text for search queries (uses retrieval_query task type)."""
        return self.embed_text(text, task_type="retrieval_query")

    # ── Gemini backend ──────────────────────────────────────────────

    def _gemini_embed(self, text: str, task_type: str) -> list[float]:
        try:
            result = genai.embed_content(
                model=self.GEMINI_MODEL,
                content=text,
                task_type=task_type,
            )
            return result["embedding"]
        except Exception as exc:
            logger.warning("Gemini embed call failed (%s), falling back to hash", exc)
            return self._hash_embed(text)

    # ── Hash-based fallback ─────────────────────────────────────────

    def _hash_embed(self, text: str) -> list[float]:
        vec = [0.0] * self.size
        words = text.lower().split()
        for word in words:
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            for i in range(self.size):
                vec[i] += digest[i % len(digest)] / 255.0

        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]
