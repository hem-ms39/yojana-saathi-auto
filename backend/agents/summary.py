from __future__ import annotations

from backend.agents.prompts import SUMMARY_SYSTEM
from backend.models.schemas import Scheme
from backend.services.llm_service import LLMService


class SummaryAgent:
    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm_service = llm_service or LLMService()

    def run(self, scheme: Scheme, language: str = "en") -> str:
        prompt = (
            f"Language: {language}\n"
            f"Scheme: {scheme.title}\n"
            f"Description: {scheme.description}\n"
            f"Eligibility rules: {scheme.eligibility_rules}\n"
            f"Required documents: {scheme.required_documents}\n"
        )
        result = self.llm_service.generate_text(SUMMARY_SYSTEM, prompt)
        if self.llm_service.enabled and result.strip():
            return result.strip()
        return (
            f"{scheme.title} offers support up to Rs {scheme.funding_amount}. "
            f"It targets {', '.join(scheme.category) or 'eligible applicants'}. "
            f"Prepare documents: {', '.join(scheme.required_documents) or 'basic ID and income proof'}."
        )

