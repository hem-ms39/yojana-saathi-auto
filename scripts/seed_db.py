from __future__ import annotations

import json
from pathlib import Path

from backend.services.supabase_service import SupabaseService


def seed_schemes() -> int:
    root = Path(__file__).resolve().parents[1]
    candidates = [
        root / "backend" / "data" / "seed_schemes.json",
        root / "data" / "processed" / "seed_schemes.json",
        root / "m3_workspace" / "backend" / "data" / "seed_schemes.json",
        root / "m3_workspace" / "data" / "processed" / "seed_schemes.json",
    ]
    source = next((path for path in candidates if path.exists()), None)
    if source is None:
        print("No seed_schemes.json found. Skipping scheme seed.")
        return 0

    service = SupabaseService()
    if not service.client:
        raise RuntimeError("Supabase is not configured.")

    schemes = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(schemes, list):
        raise RuntimeError("seed_schemes.json must contain a list.")

    if not schemes:
        print("No schemes to seed.")
        return 0

    return service.seed_schemes(schemes)


if __name__ == "__main__":
    count = seed_schemes()
    print(f"Seeded {count} schemes.")
