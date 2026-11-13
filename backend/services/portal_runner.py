"""
Standalone Playwright runner — invoked as a subprocess so it has its own
asyncio event loop, untouched by uvicorn or the parent process. Avoids the
Windows NotImplementedError on subprocess_exec.

Reads JSON from stdin: {applicant_name, fake_aadhaar, headless, screenshot_path}
Writes JSON to stdout: {error_text, field_log, screenshot_exists}
"""
from __future__ import annotations

import asyncio
import json
import sys
import traceback

PORTAL_URL = "https://udyamregistration.gov.in/UdyamRegistration.aspx"

_ERROR_KEYWORDS = (
    "invalid",
    "aadhaar",
    "incorrect",
    "error",
    "fail",
    "wrong",
    "not valid",
    "please enter",
    "verification",
)


async def run(applicant_name: str, fake_aadhaar: str, headless: bool, screenshot_path: str) -> dict:
    from playwright.async_api import async_playwright

    field_log: list[str] = []
    error_text = ""
    fatal_error: str | None = None

    try:
        async with async_playwright() as p:
            field_log.append("Launching Chromium…")
            browser = await p.chromium.launch(headless=headless)
            field_log.append("Chromium launched")
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                ignore_https_errors=True,
            )
            page = await context.new_page()

            try:
                await page.goto(PORTAL_URL, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(2000)
                field_log.append(f"Navigated to {PORTAL_URL}")
            except Exception as nav_exc:
                field_log.append(f"Navigation error: {type(nav_exc).__name__}: {nav_exc}")
                try:
                    await page.screenshot(path=screenshot_path, full_page=False)
                    field_log.append("Failure screenshot saved")
                except Exception:
                    pass
                fatal_error = f"Could not load portal: {type(nav_exc).__name__}: {nav_exc}"
                await browser.close()
                return _result(field_log, fatal_error, screenshot_path)

            aadhaar_input = await _find_first(
                page,
                [
                    'input[id*="dhar" i]',
                    'input[name*="dhar" i]',
                    'input[placeholder*="aadhaar" i]',
                ],
            )
            if aadhaar_input is None:
                fatal_error = "Could not locate Aadhaar input field on the portal."
                field_log.append(fatal_error)
            else:
                await aadhaar_input.fill(fake_aadhaar)
                field_log.append(f"Filled Aadhaar with fake value: {fake_aadhaar}")

                name_input = await _find_first(
                    page,
                    [
                        'input[id*="ownername" i]',
                        'input[id*="applicantname" i]',
                        'input[placeholder*="name" i]:not([placeholder*="aadhaar" i])',
                    ],
                )
                if name_input is not None:
                    await name_input.fill(applicant_name)
                    field_log.append(f"Filled Name: {applicant_name}")

                try:
                    await aadhaar_input.evaluate("el => el.blur()")
                except Exception:
                    pass
                await page.keyboard.press("Tab")
                await page.wait_for_timeout(1200)

                clicked = await _try_click(
                    page,
                    [
                        'input[value*="Validate" i][type="submit"]',
                        'input[value*="Validate" i]',
                        'input[id*="ValidateAadhaar" i]',
                        'button:has-text("Validate")',
                        'button:has-text("Generate OTP")',
                    ],
                )
                if clicked:
                    field_log.append("Clicked validate / generate-OTP button")
                    await page.wait_for_timeout(2500)

                error_text = await _extract_error(page)

            try:
                await page.screenshot(path=screenshot_path, full_page=False)
                field_log.append("Screenshot saved")
            except Exception as exc:
                field_log.append(f"Screenshot failed: {exc}")

            await browser.close()

    except Exception as exc:
        tb = traceback.format_exc()
        tb_last = tb.strip().splitlines()[-1] if tb else ""
        detail = str(exc) or tb_last or "(no message)"
        fatal_error = fatal_error or f"Automation failed [{type(exc).__name__}]: {detail}"
        field_log.append(f"Exception: {type(exc).__name__}: {detail}")

    final_error = error_text or fatal_error or ""
    return _result(field_log, final_error, screenshot_path)


def _result(field_log: list[str], error_text: str, screenshot_path: str) -> dict:
    import os
    return {
        "field_log": field_log,
        "error_text": error_text,
        "screenshot_exists": os.path.exists(screenshot_path),
    }


async def _find_first(page, selectors: list[str]):
    for sel in selectors:
        loc = page.locator(sel)
        try:
            count = await loc.count()
        except Exception:
            count = 0
        if count > 0:
            try:
                if await loc.first.is_visible():
                    return loc.first
            except Exception:
                continue
    return None


async def _try_click(page, selectors: list[str]) -> bool:
    for sel in selectors:
        loc = page.locator(sel)
        try:
            count = await loc.count()
        except Exception:
            count = 0
        if count > 0:
            try:
                await loc.first.click(timeout=3000)
                return True
            except Exception:
                continue
    return False


async def _extract_error(page) -> str:
    candidates: list[str] = []
    selectors = [
        '[id*="msg" i]',
        '[id*="error" i]',
        '[id*="lblmsg" i]',
        '[class*="error" i]',
        '[class*="alert" i]',
        '[class*="text-danger" i]',
        'span[style*="red" i]',
        'div[style*="red" i]',
    ]
    for sel in selectors:
        loc = page.locator(sel)
        try:
            count = await loc.count()
        except Exception:
            count = 0
        for i in range(min(count, 8)):
            try:
                text = (await loc.nth(i).text_content()) or ""
            except Exception:
                continue
            text = text.strip()
            if not text or len(text) > 400:
                continue
            lowered = text.lower()
            if any(kw in lowered for kw in _ERROR_KEYWORDS):
                candidates.append(text)
    if not candidates:
        return ""
    candidates = sorted(set(candidates), key=len, reverse=True)
    return candidates[0]


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    payload = json.loads(sys.stdin.read())
    result = asyncio.run(
        run(
            applicant_name=payload["applicant_name"],
            fake_aadhaar=payload["fake_aadhaar"],
            headless=payload["headless"],
            screenshot_path=payload["screenshot_path"],
        )
    )
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
