import { create } from "zustand";
import type { Agent, AgentId, AgentLogEvent, AgentStatus, Language } from "./types";
import { initialAgents } from "./mock";

interface State {
  language: Language;
  setLanguage: (l: Language) => void;
  agents: Agent[];
  logs: AgentLogEvent[];
  setAgentStatus: (id: AgentId, status: AgentStatus, lastAction?: string) => void;
  pushLog: (log: Omit<AgentLogEvent, "id" | "timestamp">) => void;
  reset: () => void;
}

export const useApp = create<State>((set) => ({
  language: "en",
  setLanguage: (language) => set({ language }),
  agents: initialAgents.map((a) => ({ ...a })),
  logs: [],
  setAgentStatus: (id, status, lastAction) =>
    set((s) => ({
      agents: s.agents.map((a) =>
        a.id === id ? { ...a, status, lastAction: lastAction ?? a.lastAction, startedAt: status === "working" ? Date.now() : a.startedAt } : a
      ),
    })),
  pushLog: (log) =>
    set((s) => ({
      logs: [
        ...s.logs,
        { ...log, id: Math.random().toString(36).slice(2), timestamp: Date.now() },
      ].slice(-60),
    })),
  reset: () => set({ agents: initialAgents.map((a) => ({ ...a })), logs: [] }),
}));
