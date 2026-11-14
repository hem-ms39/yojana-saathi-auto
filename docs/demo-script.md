# Demo Script

## 90-Second Flow

1. Open landing page and introduce the problem: scheme discovery is fragmented and inaccessible.
2. Trigger voice or text input with the golden demo profile.
3. Point to the agent panel while `/v1/chat` streams profile and discovery steps.
4. Open one scheme card and explain the eligibility summary.
5. Trigger `Auto-Apply`.
6. Show the application success state and the WhatsApp notification on the demo phone.

## Fallbacks

- If speech recognition fails, use the prepared text query.
- If live reasoning is unstable, switch to `DEMO_MODE=true`.
- If WhatsApp fails, use the pre-received backup message on the demo phone.
