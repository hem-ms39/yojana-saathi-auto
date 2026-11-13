from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from backend.agents.discovery import DiscoveryAgent
from backend.agents.eligibility import EligibilityAgent
from backend.agents.profile_extractor import ProfileExtractorAgent
from backend.config import settings
from backend.models.schemas import AgentStep, ChatResponse, Scheme, UserProfile
from backend.services.qdrant_service import QdrantService

StepCallback = Callable[[AgentStep], None]


class AgentOrchestrator:
    def __init__(self) -> None:
        self.qdrant_service = QdrantService()
        self.profile_agent = ProfileExtractorAgent()
        self.discovery_agent = DiscoveryAgent(self.qdrant_service)
        self.eligibility_agent = EligibilityAgent()

        self._seed_if_needed()

    def run_chat(self, message: str, language: str = "en", step_callback: StepCallback | None = None) -> ChatResponse:
        steps: list[AgentStep] = []

        def emit(step: AgentStep) -> None:
            steps.append(step)
            if step_callback:
                step_callback(step)

        emit(AgentStep(agent="profile", status="running", message="Extracting profile"))
        profile = self.profile_agent.run(message)
        emit(AgentStep(agent="profile", status="complete", message="Profile extracted", data=profile.model_dump()))

        emit(AgentStep(agent="discovery", status="running", message="Finding matching schemes"))
        search_query = self._build_search_query(profile, message)
        discovered = self.discovery_agent.run(search_query, limit=12)
        emit(AgentStep(agent="discovery", status="complete", message=f"Found {len(discovered)} schemes"))

        emit(AgentStep(agent="eligibility", status="running", message="Scoring eligibility"))
        results = self.eligibility_agent.run(profile, discovered)[:7]
        emit(AgentStep(agent="eligibility", status="complete", message=f"Top {len(results)} schemes ranked"))

        return ChatResponse(profile=profile, results=results, steps=steps, language=language)

    def _seed_if_needed(self) -> None:
        if not self.qdrant_service.using_memory:
            return
        data_path = Path(__file__).resolve().parents[1] / "data" / "seed_schemes.json"
        if not data_path.exists():
            return
        with data_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        self.qdrant_service.upsert_schemes([Scheme(**item) for item in raw])

    @staticmethod
    def _build_search_query(profile: UserProfile, original_message: str) -> str:
        """Build a language-normalized English search query from the extracted profile.

        The profile extractor already normalizes fields to English, so using
        these fields ensures consistent scheme discovery regardless of the
        input language (Hindi, Kannada, English).
        """
        parts: list[str] = []
        if profile.occupation:
            parts.append(profile.occupation)
        if profile.gender:
            parts.append(profile.gender)
        if profile.age is not None:
            parts.append(f"{profile.age} years old")
        if profile.state:
            parts.append(profile.state)
        if profile.district:
            parts.append(profile.district)
        if profile.business_intent:
            parts.append(f"{profile.business_intent} startup loan")
        if profile.caste_category:
            parts.append(profile.caste_category)
        if profile.education:
            parts.append(profile.education)
        if profile.income_annual is not None:
            parts.append(f"income {profile.income_annual}")
        if profile.disabilities:
            parts.append("disability")
        if profile.minority:
            parts.append("minority")

        # If profile extraction yielded very little, fall back to original text
        if len(parts) < 2:
            return original_message

        return " ".join(parts)

    @staticmethod
    def load_demo_response() -> dict:
        path = Path(__file__).resolve().parents[1] / "data" / "demo_response.json"
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def run(self, message: str, language: str = "en") -> ChatResponse | dict:
        if settings.demo_mode:
            cached = self.load_demo_response()
            if cached:
                return cached
        return self.run_chat(message=message, language=language)

