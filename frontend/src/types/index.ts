export interface AgentStep {
  agent: string;
  status: "running" | "complete" | "error";
  message: string;
  data?: Record<string, unknown> | null;
}

export interface UserProfile {
  age?: number | null;
  gender?: string | null;
  state?: string | null;
  district?: string | null;
  income_annual?: number | null;
  caste_category?: string | null;
  occupation?: string | null;
  education?: string | null;
  business_intent?: string | null;
  existing_business?: boolean | null;
  has_bank_account?: boolean | null;
  disabilities?: boolean | null;
  minority?: boolean | null;
}

export interface SchemeResult {
  scheme_id: string;
  title: string;
  funding_amount: number;
  eligibility: "yes" | "likely" | "no";
  confidence: number;
  reasoning: string;
  category: string[];
  deadline?: string | null;
}

export interface SchemeDetail {
  id: string;
  title: string;
  funding_amount: number;
  summary: string;
  eligibility_text?: string;
  benefits_text?: string;
  documents_required: string[];
  application_url?: string;
  deadline?: string;
  ministry?: string;
  language: string;
}

export interface ApplicationRequest {
  user_id: string;
  scheme_id: string;
  form_data: Record<string, unknown>;
  notify_phone?: string;
  user_profile?: UserProfile;
}

export interface ApplicationResponse {
  application_id: string;
  status: string;
  message: string;
  whatsapp_sent: boolean;
  persisted?: boolean;
  next_steps?: string | null;
}

export type Language = "en" | "hi" | "kn";

export type SSEEvent =
  | { event: "agent_step"; data: AgentStep }
  | { event: "scheme_result"; data: SchemeResult }
  | { event: "done"; data: { total_eligible: number; session_id: string } }
  | { event: "error"; data: { error: string } };
