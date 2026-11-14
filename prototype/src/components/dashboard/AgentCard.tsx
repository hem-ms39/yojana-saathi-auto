import type { Agent } from "@/lib/types";
import { GlassCard } from "@/components/fx/GlassCard";
import { motion } from "framer-motion";
import { CheckCircle2, AlertCircle, Loader2, User, Search, ShieldCheck, FileText, Bell } from "lucide-react";
import { cn } from "@/lib/utils";

const ICONS = {
  profile: User, discovery: Search, eligibility: ShieldCheck, form: FileText, notification: Bell,
} as const;

export function AgentCard({ agent }: { agent: Agent }) {
  const Icon = ICONS[agent.id];
  const isWorking = agent.status === "working";
  const isDone = agent.status === "done";
  const isError = agent.status === "error";

  return (
    <GlassCard className="p-4" hover>
      <div className="flex items-start gap-3">
        <div className="bg-gradient-primary/10 relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/10">
          <Icon className="h-5 w-5 text-foreground" />
          {isWorking && (
            <motion.span
              className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-emerald"
              style={{ background: "oklch(0.78 0.18 165)" }}
              animate={{ scale: [1, 1.4, 1], opacity: [1, 0.4, 1] }}
              transition={{ duration: 1.4, repeat: Infinity }}
            />
          )}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <p className="truncate text-sm font-medium">{agent.name}</p>
            <span
              className={cn(
                "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] uppercase tracking-wider",
                isWorking && "bg-emerald/15 text-emerald",
                isDone && "bg-emerald/20 text-emerald",
                isError && "bg-destructive/20 text-destructive",
                agent.status === "idle" && "bg-white/5 text-muted-foreground"
              )}
              style={
                isWorking ? { color: "oklch(0.85 0.16 165)", background: "oklch(0.78 0.18 165 / 15%)" } :
                isDone ? { color: "oklch(0.85 0.16 165)", background: "oklch(0.78 0.18 165 / 20%)" } :
                undefined
              }
            >
              {isWorking && <Loader2 className="h-3 w-3 animate-spin" />}
              {isDone && <CheckCircle2 className="h-3 w-3" />}
              {isError && <AlertCircle className="h-3 w-3" />}
              {agent.status}
            </span>
          </div>
          <p className="mt-0.5 truncate text-xs text-muted-foreground">{agent.lastAction ?? agent.description}</p>
        </div>
      </div>
    </GlassCard>
  );
}
