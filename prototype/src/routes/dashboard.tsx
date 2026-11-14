import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Header } from "@/components/layout/Header";
import { AgentCard } from "@/components/dashboard/AgentCard";
import { LogStream } from "@/components/dashboard/LogStream";
import { SchemeCard } from "@/components/dashboard/SchemeCard";
import { useApp } from "@/lib/store";
import { getLogScript, mockSchemes } from "@/lib/mock";
import type { AgentId } from "@/lib/types";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Dashboard — Yojana Saathi" },
      { name: "description", content: "Live AI agent orchestration finding government schemes that match you." },
    ],
  }),
  component: Dashboard,
});

const CATEGORIES = ["All", "Farmers", "Healthcare", "Housing", "Education", "Entrepreneurship", "Women", "Pension"];

function Dashboard() {
  const agents = useApp((s) => s.agents);
  const setAgentStatus = useApp((s) => s.setAgentStatus);
  const pushLog = useApp((s) => s.pushLog);
  const reset = useApp((s) => s.reset);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState<string>("All");

  // simulate streaming
  useEffect(() => {
    reset();
    const script = getLogScript();
    const timers: ReturnType<typeof setTimeout>[] = [];
    const order: AgentId[] = ["profile", "discovery", "eligibility", "form", "notification"];
    order.forEach((id, i) => {
      timers.push(setTimeout(() => setAgentStatus(id, "working", "Starting…"), 400 + i * 900));
    });
    script.forEach((line, i) => {
      timers.push(setTimeout(() => {
        pushLog({ agentId: line.agent, message: line.msg, level: line.level ?? "info" });
        setAgentStatus(line.agent, "working", line.msg);
      }, 700 + i * 700));
    });
    timers.push(setTimeout(() => {
      setAgentStatus("profile", "done", "Profile ready");
      setAgentStatus("discovery", "done", "84 candidates");
      setAgentStatus("eligibility", "done", "12 matches found");
      setLoading(false);
    }, 700 + script.length * 700 + 400));
    return () => { timers.forEach(clearTimeout); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const schemes = useMemo(
    () => mockSchemes.filter((s) => category === "All" || s.category === category),
    [category]
  );

  return (
    <div className="relative min-h-screen">
      <Header />
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="mb-6 flex flex-wrap items-end justify-between gap-3"
        >
          <div>
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Live session</p>
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Your <span className="text-gradient">AI agents</span> are working
            </h1>
          </div>
          <p className="text-xs text-muted-foreground">Mock data · demo mode</p>
        </motion.div>

        <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
          {/* Agent panel */}
          <aside className="space-y-3">
            {agents.map((a) => (
              <AgentCard key={a.id} agent={a} />
            ))}
            <div className="pt-2">
              <LogStream />
            </div>
          </aside>

          {/* Schemes */}
          <section>
            <div className="mb-4 flex flex-wrap gap-2">
              {CATEGORIES.map((c) => (
                <button
                  key={c}
                  onClick={() => setCategory(c)}
                  className={
                    "rounded-full px-3 py-1.5 text-xs transition-all " +
                    (category === c
                      ? "bg-gradient-primary text-primary-foreground shadow-glow"
                      : "glass text-muted-foreground hover:text-foreground")
                  }
                >
                  {c}
                </button>
              ))}
            </div>

            {loading ? (
              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="glass shimmer h-56 rounded-2xl" />
                ))}
              </div>
            ) : schemes.length === 0 ? (
              <div className="glass flex h-64 flex-col items-center justify-center rounded-2xl text-center">
                <p className="text-sm font-medium">No schemes in this category</p>
                <p className="mt-1 text-xs text-muted-foreground">Try another filter.</p>
              </div>
            ) : (
              <motion.div
                initial="hidden"
                animate="show"
                variants={{ show: { transition: { staggerChildren: 0.05 } } }}
                className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3"
              >
                {schemes.map((s) => (
                  <motion.div
                    key={s.id}
                    variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } }}
                  >
                    <SchemeCard scheme={s} />
                  </motion.div>
                ))}
              </motion.div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
