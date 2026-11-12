import type {
  ApplicationRequest,
  ApplicationResponse,
  SchemeDetail,
  SSEEvent,
} from "../types";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/v1";

async function* parseSSE(response: Response): AsyncGenerator<SSEEvent> {
  const reader = response.body?.getReader();
  if (!reader) return;

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    let currentEvent = "";
    let currentData = "";

    for (const line of lines) {
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        currentData = line.slice(5).trim();
        if (currentEvent && currentData) {
          try {
            const parsed = JSON.parse(currentData);
            yield { event: currentEvent, data: parsed } as SSEEvent;
          } catch {
            // skip malformed event
          }
          currentEvent = "";
          currentData = "";
        }
      }
    }
  }
}

export async function* streamChat(
  message: string,
  language: string
): AsyncGenerator<SSEEvent> {
  const response = await fetch(`${BACKEND_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, language }),
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  yield* parseSSE(response);
}

export async function getScheme(
  schemeId: string,
  language: string = "en"
): Promise<SchemeDetail> {
  const response = await fetch(
    `${BACKEND_URL}/schemes/${encodeURIComponent(schemeId)}?language=${language}`
  );
  if (!response.ok) {
    throw new Error(`Scheme not found: ${schemeId}`);
  }
  return response.json();
}

export async function applyForScheme(
  data: ApplicationRequest
): Promise<ApplicationResponse> {
  const response = await fetch(`${BACKEND_URL}/apply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Apply failed: ${response.status}`);
  }
  return response.json();
}

export interface OcrResult {
  status: "success" | "error";
  document: { type: string; confidence: number; warnings: string[] };
  user_profile: {
    name?: string;
    dob?: string;
    gender?: string;
    aadhaar?: string;
    pan?: string;
    state?: string;
    district?: string;
    pincode?: string;
    address?: string;
    annual_income?: number;
    caste_category?: string;
    bank_account?: string;
    ifsc?: string;
    bank_name?: string;
  };
  summary: {
    auto_filled: number;
    total_fields: number;
    fill_percentage: number;
    missing_required: string[];
  };
}

export async function uploadDocument(
  file: File,
  schemeId: string,
  docType: string = "auto"
): Promise<OcrResult> {
  const body = new FormData();
  body.append("file", file);
  body.append("scheme_id", schemeId);
  body.append("doc_type", docType);

  const response = await fetch(`${BACKEND_URL}/upload-document`, {
    method: "POST",
    body,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Upload failed: ${response.status}`);
  }
  return response.json();
}

export interface PortalAttemptResult {
  portal: string;
  portal_url: string;
  attempted: boolean;
  rejected: boolean;
  fake_aadhaar_used?: string;
  error_message: string;
  screenshot_url: string | null;
  field_log: string[];
}

export async function attemptPortalSubmit(data: {
  full_name?: string;
  aadhaar?: string | null;
  application_id?: string;
  headless?: boolean;
}): Promise<PortalAttemptResult> {
  const response = await fetch(`${BACKEND_URL}/apply/portal-attempt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Portal attempt failed: ${response.status}`);
  }
  return response.json();
}

export function backendStaticUrl(path: string | null | undefined): string | null {
  if (!path) return null;
  // BACKEND_URL is e.g. http://localhost:8000/v1 — strip the /v1 to reach /static
  const root = BACKEND_URL.replace(/\/v1\/?$/, "");
  return `${root}${path}`;
}

export async function compareSchemes(
  schemeIds: string[],
  language: string = "en"
): Promise<{ comparison: Record<string, string>[] }> {
  const response = await fetch(`${BACKEND_URL}/schemes/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scheme_ids: schemeIds, language }),
  });
  if (!response.ok) {
    throw new Error(`Compare failed: ${response.status}`);
  }
  return response.json();
}

// WhatsApp OTP auth (fallback when email rate limit is hit)
const AUTH_BASE = BACKEND_URL.replace("/v1", "");

export async function sendWhatsappOtp(phone: string): Promise<{ sent: boolean }> {
  const res = await fetch(`${AUTH_BASE}/v1/auth/whatsapp-otp/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `Failed to send WhatsApp OTP`);
  }
  return res.json();
}

export async function verifyWhatsappOtp(
  phone: string,
  otp: string
): Promise<{ access_token: string; refresh_token: string; expires_in: number }> {
  const res = await fetch(`${AUTH_BASE}/v1/auth/whatsapp-otp/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, otp }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `OTP verification failed`);
  }
  return res.json();
}

// ── Why / Explain — RAG eligibility chatbot ───────────────────────────────────

export interface ExplainAlternative {
  scheme_id: string;
  title: string;
  funding_amount: number;
}

export interface ExplainMeta {
  verdict: "yes" | "likely" | "no";
  confidence: number;
  reasoning: string;
  alternatives: ExplainAlternative[];
}

export type ExplainEvent =
  | { event: "meta"; data: ExplainMeta }
  | { event: "token"; data: { text: string } }
  | { event: "done"; data: Record<string, never> }
  | { event: "error"; data: { error: string } };

export async function* streamExplanation(
  schemeId: string,
  userProfile: Record<string, unknown>,
  language: string,
  signal?: AbortSignal
): AsyncGenerator<ExplainEvent> {
  const response = await fetch(`${BACKEND_URL}/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scheme_id: schemeId, user_profile: userProfile, language }),
    signal,
  });
  if (!response.ok) throw new Error(`Explain request failed: ${response.status}`);
  for await (const ev of parseSSE(response)) {
    yield ev as unknown as ExplainEvent;
  }
}
