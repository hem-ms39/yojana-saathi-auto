from __future__ import annotations

import json
from datetime import date

from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.prompts import SCHEME_COMPARISON_SYSTEM
from backend.services.llm_service import LLMService
from backend.services.supabase_service import SupabaseService

router = APIRouter(tags=["compare"])


class CompareRequest(BaseModel):
    scheme_ids: list[str]
    language: str = "en"


@router.post("/schemes/compare")
async def compare_schemes(request: CompareRequest) -> dict[str, object]:
    service = SupabaseService()
    schemes = service.list_schemes(request.scheme_ids)
    llm = LLMService()

    normalized = [_normalize_scheme(scheme, request.language) for scheme in schemes]
    llm_reasoning = _generate_llm_reasoning(llm, normalized, request.language)
    reasoning_by_scheme = {
        item["scheme_id"]: item for item in llm_reasoning.get("scheme_reasoning", []) if item.get("scheme_id")
    }

    for item in normalized:
        llm_item = reasoning_by_scheme.get(item["id"], {})
        item["eligibility_difficulty"] = llm_item.get(
            "eligibility_difficulty",
            _heuristic_eligibility_difficulty(item),
        )
        item["why_it_stands_out"] = llm_item.get(
            "why_it_stands_out",
            _fallback_reasoning(item),
        )
        item["best_for"] = llm_item.get("best_for", _fallback_best_for(item))

    comparison_table = [
        _row("Funding", normalized, lambda s: s["funding"]),
        _row("Eligibility Difficulty", normalized, lambda s: s["eligibility_difficulty"]),
        _row("Documents Needed", normalized, lambda s: f'{s["documents_needed_count"]} documents'),
        _row("Timeline", normalized, lambda s: s["timeline"]),
        _row("Benefits", normalized, lambda s: s["benefits"]),
    ]

    return {
        "scheme_ids": request.scheme_ids,
        "language": request.language,
        "comparison": comparison_table,
        "schemes": normalized,
        "reasoning_summary": llm_reasoning.get(
            "reasoning_summary",
            _fallback_summary(normalized),
        ),
        "llm_used": llm.enabled,
    }


def _normalize_scheme(scheme: dict, language: str) -> dict[str, object]:
    title = scheme.get(f"title_{language}") or scheme.get("title") or scheme.get("id")
    documents = scheme.get("documents_required", []) or []
    benefits_text = scheme.get("benefits_text") or scheme.get("description") or "Benefit details not available."
    return {
        "id": scheme.get("id"),
        "title": title,
        "funding": _format_currency(scheme.get("funding_amount")),
        "funding_amount": scheme.get("funding_amount") or 0,
        "documents_needed_count": len(documents),
        "documents_needed": documents,
        "timeline": _format_timeline(scheme),
        "deadline": scheme.get("deadline"),
        "benefits": _shorten_text(benefits_text, 180),
        "benefits_text": benefits_text,
        "eligibility_text": scheme.get("eligibility_text") or "",
        "category": scheme.get("category", []) or [],
        "target_group": scheme.get("target_group", []) or [],
        "ministry": scheme.get("ministry"),
        "application_url": scheme.get("application_url"),
        "min_age": scheme.get("min_age"),
        "max_age": scheme.get("max_age"),
        "max_income": scheme.get("max_income"),
    }


def _generate_llm_reasoning(llm: LLMService, schemes: list[dict[str, object]], language: str) -> dict[str, object]:
    compact_payload = [
        {
            "scheme_id": scheme["id"],
            "title": scheme["title"],
            "funding_amount": scheme["funding_amount"],
            "eligibility_text": scheme["eligibility_text"],
            "documents_needed_count": scheme["documents_needed_count"],
            "timeline": scheme["timeline"],
            "benefits_text": scheme["benefits_text"],
            "category": scheme["category"],
            "target_group": scheme["target_group"],
            "min_age": scheme["min_age"],
            "max_age": scheme["max_age"],
            "max_income": scheme["max_income"],
        }
        for scheme in schemes
    ]
    prompt = (
        f"Language: {language}\n"
        "Compare these schemes for a side-by-side comparison engine.\n"
        f"{json.dumps(compact_payload, ensure_ascii=False, indent=2)}"
    )
    return llm.generate_json(SCHEME_COMPARISON_SYSTEM, prompt)


def _heuristic_eligibility_difficulty(scheme: dict[str, object]) -> str:
    score = 0
    if scheme.get("min_age") or scheme.get("max_age"):
        score += 1
    if scheme.get("max_income"):
        score += 1
    if scheme.get("target_group"):
        score += 1
    if int(scheme.get("documents_needed_count", 0)) >= 6:
        score += 1

    text = str(scheme.get("eligibility_text") or "").lower()
    for token in ["income", "caste", "women", "sc", "st", "obc", "graduate", "certificate"]:
        if token in text:
            score += 1

    if score <= 2:
        return "Easy"
    if score <= 4:
        return "Medium"
    return "Hard"


def _fallback_reasoning(scheme: dict[str, object]) -> str:
    return (
        f"{scheme['title']} offers {scheme['funding']} with "
        f"{scheme['documents_needed_count']} documents and timeline '{scheme['timeline']}'."
    )


def _fallback_best_for(scheme: dict[str, object]) -> str:
    target_group = scheme.get("target_group") or scheme.get("category") or ["general applicants"]
    if isinstance(target_group, list) and target_group:
        return str(target_group[0]).replace("_", " ")
    return "general applicants"


def _fallback_summary(schemes: list[dict[str, object]]) -> str:
    if not schemes:
        return "No schemes available for comparison."
    richest = max(schemes, key=lambda s: int(s.get("funding_amount", 0)))
    easiest = min(schemes, key=lambda s: {"Easy": 0, "Medium": 1, "Hard": 2}.get(str(s.get("eligibility_difficulty", "Medium")), 1))
    return (
        f"{richest['title']} offers the highest funding, while {easiest['title']} looks easiest to qualify for. "
        "Use the table to balance funding against document burden and timeline clarity."
    )


def _row(field: str, schemes: list[dict[str, object]], formatter) -> dict[str, object]:
    row: dict[str, object] = {"field": field}
    for scheme in schemes:
        row[str(scheme["id"])] = formatter(scheme)
    return row


def _format_currency(amount: object) -> str:
    if not amount:
        return "Not specified"
    try:
        value = int(amount)
    except (TypeError, ValueError):
        return str(amount)
    return f"Rs {value:,}"


def _format_timeline(scheme: dict) -> str:
    deadline = scheme.get("deadline")
    if not deadline:
        return "Rolling / not specified"
    try:
        deadline_date = date.fromisoformat(str(deadline))
        if deadline_date >= date.today():
            return f"Deadline: {deadline_date.isoformat()}"
        return f"Closed: {deadline_date.isoformat()}"
    except ValueError:
        return f"Deadline: {deadline}"


def _shorten_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."
