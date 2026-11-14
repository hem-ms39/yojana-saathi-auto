import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, Compass } from "lucide-react";
import { ParticleField } from "@/components/fx/ParticleField";
import { VoiceOrb } from "@/components/landing/VoiceOrb";
import { LanguageSwitcher } from "@/components/landing/LanguageSwitcher";
import { Header } from "@/components/layout/Header";
import { useApp } from "@/lib/store";
import { dict } from "@/lib/i18n";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Yojana Saathi — AI for every government benefit" },
      { name: "description", content: "AI agents discover, match, and auto-apply to government schemes for Indian citizens. Voice-first, multilingual, with WhatsApp updates." },
      { property: "og:title", content: "Yojana Saathi — AI for every government benefit" },
      { property: "og:description", content: "Find every government benefit you deserve, powered by AI agents." },
    ],
  }),
  component: Landing,
});

function Landing() {
  const navigate = useNavigate();
  const lang = useApp((s) => s.language);
  const t = dict[lang];
  const [active, setActive] = useState(false);

  return (
    <div className="relative min-h-screen overflow-hidden">
      <ParticleField density={50} />
      <div className="relative z-10">
        <Header />
        <main className="mx-auto flex min-h-[calc(100vh-3.5rem)] max-w-6xl flex-col items-center justify-center px-4 py-10 text-center sm:px-6">
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-8 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-muted-foreground backdrop-blur"
          >
            <span className="h-1.5 w-1.5 rounded-full" style={{ background: "oklch(0.78 0.18 165)" }} />
            {t.poweredBy}
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.05 }}
            className="text-balance text-4xl font-semibold leading-[1.05] tracking-tight sm:text-6xl md:text-7xl"
          >
            <span className="text-gradient">{t.headline}</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="mx-auto mt-5 max-w-xl text-pretty text-base text-muted-foreground sm:text-lg"
          >
            {t.sub}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.25 }}
            className="mt-10"
          >
            <VoiceOrb active={active} onClick={() => setActive((v) => !v)} label={t.tapToSpeak} />
            <p className="mt-4 text-xs text-muted-foreground">
              {active ? t.listening : t.tapToSpeak}
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-10 flex flex-col items-center gap-4 sm:flex-row"
          >
            <button
              onClick={() => navigate({ to: "/dashboard" })}
              className="bg-gradient-primary inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-semibold text-primary-foreground shadow-glow transition-transform hover:scale-105"
            >
              {t.startVoice}
              <ArrowRight className="h-4 w-4" />
            </button>
            <button
              onClick={() => navigate({ to: "/dashboard" })}
              className="glass inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-medium text-foreground hover:bg-white/10"
            >
              <Compass className="h-4 w-4" />
              {t.explore}
            </button>
          </motion.div>

          <div className="mt-10 sm:hidden">
            <LanguageSwitcher />
          </div>
        </main>
      </div>
    </div>
  );
}
