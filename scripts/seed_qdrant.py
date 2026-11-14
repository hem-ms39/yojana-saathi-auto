"""Seed schemes into Qdrant cloud from backend/data/seed_schemes.json"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.models.schemas import Scheme
from backend.services.qdrant_service import QdrantService


def main() -> None:
    data_path = Path(__file__).resolve().parents[1] / "backend" / "data" / "seed_schemes.json"
    if not data_path.exists():
        print(f"Not found: {data_path}")
        sys.exit(1)

    schemes = [Scheme(**item) for item in json.loads(data_path.read_text(encoding="utf-8"))]
    print(f"Loaded {len(schemes)} schemes from JSON")

    qs = QdrantService()
    if qs.using_memory:
        print("ERROR: No QDRANT_URL configured — running in memory mode, nothing to seed.")
        sys.exit(1)

    qs.ensure_collection()
    qs.upsert_schemes(schemes)
    print(f"✓ Seeded {len(schemes)} schemes into Qdrant collection '{__import__('backend.config', fromlist=['settings']).settings.collection_name}'")


if __name__ == "__main__":
    main()
