"""
Scheme-specific Q&A chatbot endpoint.
POST /v1/schemes/{scheme_id}/chat

Uses RAG: fetches the scheme data + similar schemes from the embedding index,
then streams a Groq answer to any user question about the scheme.
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

from backend.agents.orchestrator import AgentOrchestrator
from backend.models.schemas import Scheme
from backend.services.llm_service import LLMService

router = APIRouter(tags=["scheme-chat"])

# Singleton orchestrator shared with explain.py
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


class SchemeChatRequest(BaseModel):
    message: str
    language: str = "en"
    history: list[dict[str, str]] = []   # [{role: user|assistant, content: str}]
    user_profile: dict[str, Any] = {}


SCHEME_CHAT_SYSTEM = """
You are Yojana Saathi, an expert AI assistant for Indian government schemes.
Answer the user's question ONLY based on the scheme context provided below.
Be concise, friendly, and accurate. If the answer is not in the context, say so honestly.
Do not hallucinate scheme rules or amounts.
Format: plain prose, no markdown headers. Bullets are ok.
Keep your response under 120 words.
Respond in the language specified by the 'language' field: en=English, hi=Hindi, kn=Kannada.
"""

_SENTINEL = object()


def _find_scheme(orch: AgentOrchestrator, scheme_id: str) -> Scheme | None:
    for scheme, _ in orch.qdrant_service._memory_index:
        if scheme.scheme_id == scheme_id:
            return scheme
    results = orch.qdrant_service.search(scheme_id, limit=20)
    for s in results:
        if s.scheme_id == scheme_id:
            return s
    return None


def _load_raw_scheme(scheme_id: str) -> dict:
    """Load raw scheme dict from seed JSON — has all fields including documents."""
    import json as _json
    from pathlib import Path
    seed_path = Path(__file__).resolve().parents[1] / "data" / "seed_schemes.json"
    try:
        data = _json.loads(seed_path.read_text(encoding="utf-8"))
        schemes_list = data if isinstance(data, list) else data.get("schemes", [])
        for s in schemes_list:
            if s.get("scheme_id") == scheme_id:
                return s
    except Exception:
        pass
    return {}


def _build_context(scheme: Scheme, similar: list[Scheme]) -> str:
    # Load raw JSON for complete field coverage
    raw = _load_raw_scheme(scheme.scheme_id)

    docs = (
        raw.get("documents_required")
        or scheme.required_documents
        or scheme.documents_required
        or []
    )
    docs_str = ", ".join(docs) if docs else "Not specified in scheme data"

    steps = raw.get("application_steps") or []
    steps_str = ""
    if steps:
        steps_str = "\nApplication Steps:\n" + "\n".join(f"  {s}" for s in steps)

    eligibility_text = raw.get("eligibility_text") or ""
    benefits_text = raw.get("benefits_text") or scheme.description or ""

    parts = [
        f"Scheme: {scheme.title}",
        f"Ministry: {raw.get('ministry') or scheme.ministry or 'N/A'}",
        f"State: {raw.get('state') or scheme.state or 'All India'}",
        f"Funding: ₹{scheme.funding_amount:,}",
        f"Category: {', '.join(scheme.category)}",
        f"Target Groups: {', '.join(raw.get('target_group') or scheme.target_group)}",
        f"Age Limit: {raw.get('min_age') or scheme.min_age or 'Any'}–{raw.get('max_age') or scheme.max_age or 'Any'}",
        f"Max Income: {raw.get('max_income') or scheme.max_income or 'No limit'}",
        f"Deadline: {scheme.deadline or 'Open / Rolling'}",
        f"Apply URL: {raw.get('application_url') or scheme.application_url or 'N/A'}",
        f"\nEligibility: {eligibility_text or 'See scheme guidelines'}",
        f"\nBenefits: {benefits_text[:300]}",
        f"\nRequired Documents: {docs_str}",
        steps_str,
    ]
    if similar:
        parts.append("\nRelated schemes for reference:")
        for s in similar[:2]:
            parts.append(f"  - {s.title}: {s.description[:80]}…")
    return "\n".join(p for p in parts if p)


def _worker(
    scheme_id: str,
    request: SchemeChatRequest,
    q: queue.Queue[Any],
) -> None:
    try:
        orch = _get_orchestrator()
        scheme = _find_scheme(orch, scheme_id)
        if not scheme:
            q.put({"event": "error", "data": {"error": f"Scheme '{scheme_id}' not found"}})
            q.put(_SENTINEL)
            return

        # RAG: fetch similar schemes for richer context
        similar = orch.qdrant_service.search(request.message, limit=5)
        similar = [s for s in similar if s.scheme_id != scheme_id][:2]

        context = _build_context(scheme, similar)

        # Build messages
        system_prompt = f"{SCHEME_CHAT_SYSTEM}\n\nLanguage: {request.language}\n\nScheme Context:\n{context}"

        # Include previous turns for continuity
        messages = [{"role": "system", "content": system_prompt}]
        for turn in request.history[-6:]:  # last 3 exchanges
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": request.message})

        llm = LLMService()
        if not llm.enabled:
            q.put({"event": "token", "data": {"text": "LLM not configured. Please check GROQ_API_KEY."}})
            q.put({"event": "done", "data": {}})
            q.put(_SENTINEL)
            return

        stream = llm._client.chat.completions.create(
            model=llm._model,
            temperature=0.4,
            stream=True,
            messages=messages,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                q.put({"event": "token", "data": {"text": delta}})

        q.put({"event": "done", "data": {}})

    except Exception as exc:
        q.put({"event": "error", "data": {"error": str(exc)}})
    finally:
        q.put(_SENTINEL)


@router.post("/schemes/{scheme_id}/chat")
async def scheme_chat(scheme_id: str, request: SchemeChatRequest) -> StreamingResponse:
    q: queue.Queue[Any] = queue.Queue()
    thread = threading.Thread(target=_worker, args=(scheme_id, request, q), daemon=True)
    thread.start()

    loop = asyncio.get_event_loop()

    async def event_stream():
        while True:
            item = await loop.run_in_executor(None, q.get)
            if item is _SENTINEL:
                break
            yield f"event: {item['event']}\ndata: {json.dumps(item['data'], ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
