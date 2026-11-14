from __future__ import annotations

import asyncio
import json
import uuid
from queue import Empty, Queue
from threading import Thread

from fastapi import APIRouter
from sse_starlette import EventSourceResponse

from backend.agents.orchestrator import AgentOrchestrator
from backend.models.schemas import AgentStep, ChatRequest

router = APIRouter(tags=["chat"])

_SENTINEL = object()


@router.post("/chat")
async def chat(request: ChatRequest) -> EventSourceResponse:
    session_id = request.session_id or str(uuid.uuid4())
    q: Queue = Queue()

    def run_orchestrator() -> None:
        try:
            orchestrator = AgentOrchestrator()

            def callback(step: AgentStep) -> None:
                q.put(("agent_step", step.model_dump()))

            response = orchestrator.run_chat(
                message=request.message,
                language=request.language,
                step_callback=callback,
            )

            for result in response.results:
                q.put(("scheme_result", result.model_dump()))

            q.put(("done", {"total_eligible": len(response.results), "session_id": session_id}))
        except Exception as exc:
            q.put(("error", {"error": str(exc)}))
        finally:
            q.put(_SENTINEL)

    thread = Thread(target=run_orchestrator, daemon=True)
    thread.start()

    async def event_generator():
        loop = asyncio.get_event_loop()
        while True:
            try:
                item = await loop.run_in_executor(None, q.get, True, 60.0)
            except Empty:
                yield {"event": "error", "data": json.dumps({"error": "request timed out"})}
                break
            if item is _SENTINEL:
                break
            event, data = item
            yield {"event": event, "data": json.dumps(data)}

    return EventSourceResponse(event_generator())
