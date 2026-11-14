"""
SSE endpoint: POST /v1/explain
Streams a plain-language eligibility explanation for one scheme + user profile.
Uses RAG: fetches semantically similar alternative schemes from the embedding index.
"""
from __future__ import annotations

import asyncio
import json
import queue
import threading
from typing import Any

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.agents.eligibility import EligibilityAgent
from backend.agents.orchestrator import AgentOrchestrator
from backend.agents.prompts import EXPLAIN_ELIGIBILITY_SYSTEM
from backend.models.schemas import Scheme, UserProfile
from backend.services.llm_service import LLMService

router = APIRouter(tags=["explain"])

# ── Singleton orchestrator (holds in-memory scheme index) ──────────────────────
_orchestrator: AgentOrchestrator | None = None
_orch_lock = threading.Lock()


def _get_orchestrator() -> AgentOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        with _orch_lock:
            if _orchestrator is None:
                _orchestrator = AgentOrchestrator()
                _orchestrator._seed_if_needed()
    return _orchestrator


# ── Request model ───────────────────────────────────────────────────────────────
class ExplainRequest(BaseModel):
    scheme_id: str
    user_profile: dict[str, Any] = {}
    language: str = "en"


# ── Helpers ─────────────────────────────────────────────────────────────────────

_PROFILE_FIELDS = {f for f in UserProfile.model_fields}


def _coerce_profile(raw: dict[str, Any]) -> UserProfile:
    clean = {k: v for k, v in raw.items() if k in _PROFILE_FIELDS}
    return UserProfile(**clean)


def _profile_query(profile: UserProfile) -> str:
    parts: list[str] = []
    if profile.occupation:
        parts.append(profile.occupation)
    if profile.business_intent:
        parts.append(f"{profile.business_intent} business")
    if profile.age is not None:
        parts.append(f"{profile.age} years old")
    if profile.state:
        parts.append(profile.state)
    if profile.gender:
        parts.append(profile.gender)
    if profile.income_annual is not None:
        parts.append(f"income {profile.income_annual}")
    if profile.caste_category:
        parts.append(profile.caste_category)
    return " ".join(parts) if parts else "government scheme India"


def _find_target_scheme(orch: AgentOrchestrator, scheme_id: str) -> Scheme | None:
    # 1. Walk in-memory index first (O(n), cheap)
    for scheme, _ in orch.qdrant_service._memory_index:
        if scheme.scheme_id == scheme_id:
            return scheme
    # 2. Fallback: text search on the scheme_id itself
    results = orch.qdrant_service.search(scheme_id, limit=20)
    for s in results:
        if s.scheme_id == scheme_id:
            return s
    return None


def _build_user_prompt(
    profile: UserProfile,
    scheme: Scheme,
    verdict: str,
    confidence: int,
    reasoning: str,
    alternatives: list[Scheme],
    language: str,
) -> str:
    alt_names = ", ".join(s.title for s in alternatives[:3]) if alternatives else "none found"
    return f"""
Language: {language}

User Profile:
{profile.model_dump_json(indent=2)}

Scheme: {scheme.title}
Eligibility Rules: {json.dumps(scheme.eligibility_rules or {}, indent=2)}
Target Groups: {scheme.target_group}
Category: {scheme.category}
Min Age: {scheme.min_age}, Max Age: {scheme.max_age}
Max Income: {scheme.max_income}
State: {scheme.state}

Pre-computed verdict: {verdict} (confidence: {confidence}%)
Reasoning hint: {reasoning}

Alternative schemes (for not-eligible case): {alt_names}

Now explain why.
""".strip()


# ── SSE worker ──────────────────────────────────────────────────────────────────

_SENTINEL = object()


def _worker(
    request: ExplainRequest,
    q: queue.Queue[Any],
) -> None:
    try:
        orch = _get_orchestrator()
        profile = _coerce_profile(request.user_profile)

        # Find the scheme
        scheme = _find_target_scheme(orch, request.scheme_id)
        if scheme is None:
            q.put({"event": "error", "data": {"error": f"Scheme {request.scheme_id!r} not found"}})
            q.put(_SENTINEL)
            return

        # Deterministic eligibility verdict
        results = EligibilityAgent().run(profile, [scheme])
        result = results[0] if results else None
        verdict = result.eligibility if result else "no"
        confidence = result.confidence if result else 0
        reasoning = result.reasoning if result else ""

        # RAG: fetch similar alternatives (only for non-eligible)
        alternatives: list[Scheme] = []
        if verdict != "yes":
            pq = _profile_query(profile)
            candidates = orch.qdrant_service.search(pq, limit=8)
            alternatives = [s for s in candidates if s.scheme_id != request.scheme_id][:3]

        # Emit meta event first
        q.put({
            "event": "meta",
            "data": {
                "verdict": verdict,
                "confidence": confidence,
                "reasoning": reasoning,
                "alternatives": [
                    {"scheme_id": s.scheme_id, "title": s.title, "funding_amount": s.funding_amount}
                    for s in alternatives
                ],
            },
        })

        # Stream LLM explanation
        llm = LLMService()
        user_prompt = _build_user_prompt(
            profile, scheme, verdict, confidence, reasoning, alternatives, request.language
        )
        for token in llm.generate_text_stream(EXPLAIN_ELIGIBILITY_SYSTEM, user_prompt):
            q.put({"event": "token", "data": {"text": token}})

        q.put({"event": "done", "data": {}})

    except Exception as exc:
        q.put({"event": "error", "data": {"error": str(exc)}})
    finally:
        q.put(_SENTINEL)


# ── SSE endpoint ─────────────────────────────────────────────────────────────────

@router.post("/explain")
async def explain_eligibility(request: ExplainRequest) -> StreamingResponse:
    q: queue.Queue[Any] = queue.Queue()
    thread = threading.Thread(target=_worker, args=(request, q), daemon=True)
    thread.start()

    loop = asyncio.get_event_loop()

    async def event_stream():
        while True:
            item = await loop.run_in_executor(None, q.get)
            if item is _SENTINEL:
                break
            event = item["event"]
            data = json.dumps(item["data"], ensure_ascii=False)
            yield f"event: {event}\ndata: {data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
