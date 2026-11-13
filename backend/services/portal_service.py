"""
Live attempt against the real Udyam Registration portal with fake Aadhaar.

Spawns a child Python process running portal_runner.py so Playwright has its
own isolated asyncio event loop. Avoids the NotImplementedError that occurs
when running Playwright inside uvicorn's worker threads on Windows.
"""
from __future__ import annotations

import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import Any

PORTAL_URL = "https://udyamregistration.gov.in/UdyamRegistration.aspx"
PORTAL_NAME = "udyamregistration.gov.in"
SCREENSHOT_DIR = Path(__file__).resolve().parents[1] / "static" / "screenshots"
RUNNER_SCRIPT = Path(__file__).resolve().parent / "portal_runner.py"

# Verhoeff-invalid Aadhaar — instantly rejected by client-side validation.
DEFAULT_FAKE_AADHAAR = "111111111111"


async def attempt_udyam_submit(
    applicant_name: str = "Demo User",
    fake_aadhaar: str | None = None,
    headless: bool = False,
) -> dict[str, Any]:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    attempt_id = uuid.uuid4().hex[:8]
    screenshot_filename = f"udyam_{attempt_id}.png"
    screenshot_path = SCREENSHOT_DIR / screenshot_filename

    aadhaar_value = (fake_aadhaar or DEFAULT_FAKE_AADHAAR).strip() or DEFAULT_FAKE_AADHAAR

    payload = {
        "applicant_name": applicant_name,
        "fake_aadhaar": aadhaar_value,
        "headless": headless,
        "screenshot_path": str(screenshot_path),
    }

    field_log: list[str] = []
    error_text = ""

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            str(RUNNER_SCRIPT),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=json.dumps(payload).encode("utf-8")),
                timeout=120,
            )
        except TimeoutError:
            proc.kill()
            await proc.wait()
            error_text = "Portal automation timed out after 120s"
            field_log.append(error_text)
            stdout, stderr = b"", b""

        if proc.returncode == 0 and stdout:
            try:
                result = json.loads(stdout.decode("utf-8"))
                field_log = result.get("field_log", [])
                error_text = result.get("error_text") or error_text
            except Exception as exc:
                error_text = f"Failed to parse runner output: {exc}"
                field_log.append(error_text)
        elif proc.returncode != 0 and not error_text:
            stderr_text = stderr.decode("utf-8", errors="replace").strip()[-400:]
            error_text = f"Runner exited with code {proc.returncode}: {stderr_text}"
            field_log.append(error_text)

    except NotImplementedError:
        # Fallback for asyncio policies that don't support subprocess on this thread.
        return _run_via_blocking_subprocess(payload, screenshot_filename, screenshot_path)
    except Exception as exc:
        error_text = f"Failed to launch runner: {type(exc).__name__}: {exc}"
        field_log.append(error_text)

    if not error_text:
        error_text = (
            "Portal did not surface a visible rejection — the screenshot "
            "shows the current page state."
        )

    return {
        "portal": PORTAL_NAME,
        "portal_url": PORTAL_URL,
        "attempted": True,
        "rejected": True,
        "fake_aadhaar_used": aadhaar_value,
        "error_message": error_text,
        "screenshot_url": (
            f"/static/screenshots/{screenshot_filename}"
            if screenshot_path.exists()
            else None
        ),
        "field_log": field_log,
    }


def _run_via_blocking_subprocess(
    payload: dict, screenshot_filename: str, screenshot_path: Path
) -> dict[str, Any]:
    """Fallback path using stdlib subprocess.run() in a thread."""
    import subprocess

    field_log: list[str] = []
    error_text = ""
    try:
        completed = subprocess.run(
            [sys.executable, str(RUNNER_SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if completed.returncode == 0 and completed.stdout:
            result = json.loads(completed.stdout)
            field_log = result.get("field_log", [])
            error_text = result.get("error_text", "")
        else:
            stderr_tail = (completed.stderr or "").strip()[-400:]
            error_text = f"Runner exited with code {completed.returncode}: {stderr_tail}"
            field_log.append(error_text)
    except Exception as exc:
        error_text = f"Fallback subprocess failed: {exc}"
        field_log.append(error_text)

    if not error_text:
        error_text = "Portal did not surface a visible rejection — see screenshot."

    return {
        "portal": PORTAL_NAME,
        "portal_url": PORTAL_URL,
        "attempted": True,
        "rejected": True,
        "fake_aadhaar_used": payload.get("fake_aadhaar"),
        "error_message": error_text,
        "screenshot_url": (
            f"/static/screenshots/{screenshot_filename}"
            if screenshot_path.exists()
            else None
        ),
        "field_log": field_log,
    }
