export type AgentId = "profile" | "discovery" | "eligibility" | "form" | "notification";
export type AgentStatus = "idle" | "working" | "done" | "error";

export interface Agent {
  id: AgentId;
  name: string;
  description: string;
  status: AgentStatus;
  lastAction?: string;
  startedAt?: number;
}

export interface AgentLogEvent {
  id: string;
  agentId: AgentId;
  message: string;
  level: "info" | "success" | "warn";
  timestamp: number;
}

export interface Scheme {
  id: string;
  name: string;
  ministry: string;
  category: string;
  fundingAmount: string;
  matchPercent: number;
  confidence: number;
  deadline: string;
  tags: string[];
  description: string;
  state?: string;
}

export type Language = "en" | "hi" | "kn";
