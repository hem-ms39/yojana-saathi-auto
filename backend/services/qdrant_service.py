from __future__ import annotations

from typing import Any

from backend.config import settings
from backend.models.schemas import Scheme
from backend.services.embedding_service import EmbeddingService

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, PointStruct, VectorParams
except Exception:
    QdrantClient = None
    Distance = PointStruct = VectorParams = None


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=False))


def _to_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if cleaned.isdigit():
            return int(cleaned)
    return default


class QdrantService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self._memory_index: list[tuple[Scheme, list[float]]] = []
        self._client = None
        if QdrantClient and settings.qdrant_url:
            try:
                client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
                # Force a connectivity test — QdrantClient uses lazy connections
                client.get_collections()
                self._client = client
                self._sync_embedding_size_from_remote()
            except Exception as exc:
                import logging
                logging.getLogger(__name__).warning(
                    "Qdrant Cloud unreachable (%s). Falling back to in-memory search.", exc
                )
                self._client = None

    @property
    def using_memory(self) -> bool:
        return self._client is None

    def ensure_collection(self) -> None:
        if not self._client:
            return
        existing = [c.name for c in self._client.get_collections().collections]
        if settings.collection_name not in existing:
            self._client.create_collection(
                collection_name=settings.collection_name,
                vectors_config=VectorParams(size=settings.embedding_size, distance=Distance.COSINE),
            )

    def _sync_embedding_size_from_remote(self) -> None:
        if not self._client:
            return
        try:
            existing = [c.name for c in self._client.get_collections().collections]
            if settings.collection_name not in existing:
                return
            collection = self._client.get_collection(settings.collection_name)
            vectors = collection.config.params.vectors
            remote_size = None
            if hasattr(vectors, "size"):  # single unnamed vector config
                remote_size = vectors.size
            elif isinstance(vectors, dict):  # named vectors
                first_vector = next(iter(vectors.values()), None)
                remote_size = getattr(first_vector, "size", None)

            if isinstance(remote_size, int) and remote_size > 0:
                self.embedding_service = EmbeddingService(size=remote_size)
        except Exception:
            # If remote introspection fails, keep configured local size.
            return

    def upsert_schemes(self, schemes: list[Scheme]) -> None:
        if self.using_memory:
            self._memory_index = []
            for s in schemes:
                text = f"{s.title} {s.description} {' '.join(s.category)}"
                self._memory_index.append((s, self.embedding_service.embed_text(text)))
            return

        self.ensure_collection()
        points: list[Any] = []
        for i, scheme in enumerate(schemes):
            text = f"{scheme.title} {scheme.description} {' '.join(scheme.category)}"
            points.append(
                PointStruct(
                    id=i + 1,
                    vector=self.embedding_service.embed_text(text),
                    payload=scheme.model_dump(),
                )
            )
        self._client.upsert(collection_name=settings.collection_name, points=points)

    def search(self, query: str, limit: int | None = None) -> list[Scheme]:
        limit = limit or settings.search_limit
        query_vector = self.embedding_service.embed_query(query)

        if self.using_memory:
            scored = [
                (scheme, _cosine(query_vector, vec))
                for scheme, vec in self._memory_index
            ]
            scored.sort(key=lambda item: item[1], reverse=True)
            return [s for s, _ in scored[:limit]]

        results = self._client.search(
            collection_name=settings.collection_name,
            query_vector=query_vector,
            limit=limit,
        )
        schemes: list[Scheme] = []
        for r in results:
            payload = r.payload or {}
            normalized = {
                "scheme_id": payload.get("scheme_id") or f"scheme-{r.id}",
                "title": payload.get("title") or "Unnamed scheme",
                "description": payload.get("description") or "",
                "category": payload.get("category") or [],
                "eligibility_rules": payload.get("eligibility_rules") or {},
                "funding_amount": _to_int(payload.get("funding_amount"), default=0),
                "deadline": payload.get("deadline"),
                "required_documents": payload.get("required_documents") or [],
                "application_url": payload.get("application_url"),
            }
            schemes.append(Scheme(**normalized))
        return schemes

