"use client";

import { useEffect, useRef } from "react";
import type { AgentStep } from "../types";

const AGENT_ICON: Record<string, string> = {
  profile: "🧠",
  discovery: "🔍",
  eligibility: "✅",
  summary: "📋",
  notification: "📱",
  profile_extractor: "🧠",
};

const STATUS_COLOR: Record<string, string> = {
  running: "text-amber-400",
  complete: "text-emerald-400",
  error: "text-red-400",
};

const STATUS_LABEL: Record<string, string> = {
  running: "Running…",
  complete: "Done",
  error: "Error",
};

interface AgentPanelProps {
  steps: AgentStep[];
  isStreaming: boolean;
  totalEligible?: number;
  elapsedMs?: number;
}

export function AgentPanel({
  steps,
  isStreaming,
  totalEligible,
  elapsedMs,
}: AgentPanelProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [steps]);

  return (
    <div className="bg-slate-800 rounded-xl h-full min-h-[400px] flex flex-col overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-700 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span className="text-sm font-mono text-slate-300 font-medium">
          Agent Reasoning
        </span>
        {isStreaming && (
          <span className="ml-auto text-xs text-amber-400 font-mono">
            ● LIVE
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm">
        {steps.length === 0 && (
          <p className="text-slate-500 text-xs">Waiting for query…</p>
        )}

        {steps.map((step, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className="text-base shrink-0">
              {AGENT_ICON[step.agent] ?? "⚙️"}
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-slate-300 font-medium capitalize">
                  {step.agent.replace(/_/g, " ")}
                </span>
                <span
                  className={`text-xs ${STATUS_COLOR[step.status] ?? "text-slate-400"}`}
                >
                  — {STATUS_LABEL[step.status] ?? step.status}
                </span>
              </div>
              <p className="text-slate-400 text-xs mt-0.5 break-words">
                {step.message}
              </p>
              {step.data && step.status === "complete" && (
                <pre className="mt-1 text-xs text-slate-500 whitespace-pre-wrap break-all">
                  {JSON.stringify(step.data, null, 2).slice(0, 200)}
                </pre>
              )}
            </div>
          </div>
        ))}

        {!isStreaming && totalEligible !== undefined && (
          <div className="pt-2 border-t border-slate-700">
            <p className="text-emerald-400 text-xs">
              📊 {totalEligible} eligible schemes ranked
            </p>
            {elapsedMs !== undefined && (
              <p className="text-slate-500 text-xs">
                ⏱ Completed in {(elapsedMs / 1000).toFixed(1)}s
              </p>
            )}
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}
