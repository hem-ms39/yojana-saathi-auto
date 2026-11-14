import { useApp } from "@/lib/store";
import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

const AGENT_LABEL: Record<string, string> = {
  profile: "PROFILE", discovery: "DISCOVERY", eligibility: "ELIGIBILITY", form: "FORM", notification: "NOTIFY",
};

function formatTime(ts: number) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

export function LogStream() {
  const logs = useApp((s) => s.logs);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    ref.current?.scrollTo({ top: ref.current.scrollHeight, behavior: "smooth" });
  }, [logs.length]);

  return (
    <div className="glass gradient-border flex h-72 flex-col rounded-2xl">
      <div className="flex items-center justify-between border-b border-white/5 px-4 py-2.5">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="absolute inset-0 animate-ping rounded-full bg-emerald opacity-60" style={{ background: "oklch(0.78 0.18 165)" }} />
            <span className="relative h-2 w-2 rounded-full bg-emerald" style={{ background: "oklch(0.78 0.18 165)" }} />
          </span>
          <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Live agent stream</p>
        </div>
        <p className="text-[10px] text-muted-foreground">{logs.length} events</p>
      </div>
      <div ref={ref} className="scrollbar-thin flex-1 overflow-y-auto px-4 py-3 font-mono text-[12px] leading-relaxed">
        <AnimatePresence initial={false}>
          {logs.map((log) => (
            <motion.div
              key={log.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25 }}
              className="flex items-start gap-2 py-0.5"
            >
              <span className="shrink-0 text-muted-foreground/60">{formatTime(log.timestamp)}</span>
              <span className="shrink-0 rounded px-1.5 text-[10px] font-semibold tracking-wider text-emerald" style={{ color: "oklch(0.85 0.16 165)" }}>
                {AGENT_LABEL[log.agentId]}
              </span>
              <span
                className={cn(
                  "min-w-0 flex-1",
                  log.level === "warn" && "text-amber-300",
                )}
                style={log.level === "success" ? { color: "oklch(0.88 0.14 165)" } : undefined}
              >
                {log.message}
              </span>
            </motion.div>
          ))}
        </AnimatePresence>
        {logs.length === 0 && (
          <p className="text-muted-foreground/60">Waiting for agents to start…</p>
        )}
      </div>
    </div>
  );
}
