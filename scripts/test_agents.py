from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.agents.orchestrator import AgentOrchestrator


def run_smoke_tests() -> None:
    orchestrator = AgentOrchestrator()
    demo_profiles_path = Path(__file__).resolve().parents[1] / "backend" / "data" / "demo_profiles.json"
    profiles = json.loads(demo_profiles_path.read_text(encoding="utf-8"))

    for item in profiles:
        print(f"\n=== {item['name']} ({item['language']}) ===")
        response = orchestrator.run_chat(item["query"], item["language"])
        print("Profile:", response.profile.model_dump())
        for i, scheme in enumerate(response.results[:3], start=1):
            print(f"{i}. {scheme.title} | {scheme.eligibility} | {scheme.confidence}%")


if __name__ == "__main__":
    run_smoke_tests()

