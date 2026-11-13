from __future__ import annotations

from backend.models.schemas import Scheme
from backend.services.qdrant_service import QdrantService


class DiscoveryAgent:
    def __init__(self, qdrant_service: QdrantService | None = None) -> None:
        self.qdrant_service = qdrant_service or QdrantService()

    def run(self, query_text: str, limit: int = 12) -> list[Scheme]:
        return self.qdrant_service.search(query_text, limit=limit)

