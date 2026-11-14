"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { LanguageToggle } from "../components/language-toggle";
import { VoiceButton } from "../components/voice-button";
import type { Language } from "../types";

const PLACEHOLDERS: Record<Language, string> = {
  en: 'e.g. "I am a 22-year-old woman from Bangalore wanting to start a tailoring business"',
  hi: 'उदा. "मैं 22 साल की हूं, बैंगलोर से, सिलाई का व्यवसाय शुरू करना चाहती हूं"',
  kn: 'ಉದಾ. "ನಾನು 22 ವರ್ಷದ ಮಹಿಳೆ, ಬೆಂಗಳೂರಿನಿಂದ, ಹೊಲಿಗೆ ವ್ಯವಹಾರ ಪ್ರಾರಂಭಿಸಲು ಬಯಸುತ್ತೇನೆ"',
};

const QUICK_QUERIES = [
  "🏭 Business Loans",
  "📚 Scholarships",
  "👩 Women Schemes",
  "🌾 Farmer Aid",
  "🏠 Housing",
  "💼 Skill Training",
];

export default function LandingPage() {
  const router = useRouter();
  const [language, setLanguage] = useState<Language>("en");
  const [query, setQuery] = useState("");

  const handleSubmit = useCallback(
    (text: string) => {
      const q = text.trim();
      if (!q) return;
      router.push(`/results?q=${encodeURIComponent(q)}&lang=${language}`);
    },
    [language, router]
  );

  const onTranscript = useCallback((text: string) => {
    setQuery(text);
  }, []);

  useEffect(() => {
    if (query) {
      const handler = setTimeout(() => {
        // auto-submit after voice transcript
      }, 0);
      return () => clearTimeout(handler);
    }
  }, [query]);

  return (
    <div className="max-w-3xl mx-auto px-4 py-16 flex flex-col items-center gap-10">
      {/* Header row */}
      <div className="w-full flex justify-end">
        <LanguageToggle language={language} onChange={setLanguage} />
      </div>

      {/* Hero */}
      <div className="text-center space-y-3">
        <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 leading-tight">
          Find every government rupee{" "}
          <span className="text-blue-600">you deserve</span>
        </h1>
        <p className="text-slate-500 text-lg max-w-xl mx-auto">
          Speak or type your situation. Our AI agents search 200+ schemes and
          tell you exactly what you qualify for — in seconds.
        </p>
      </div>

      {/* Voice button */}
      <VoiceButton language={language} onTranscript={onTranscript} />

      {/* Text input */}
      <form
        className="w-full space-y-3"
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit(query);
        }}
      >
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={PLACEHOLDERS[language]}
          rows={3}
          className="w-full rounded-xl border border-slate-300 px-4 py-3 text-slate-800 placeholder-slate-400 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm"
        />
        <button
          type="submit"
          disabled={!query.trim()}
          className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-semibold text-base transition-colors shadow-sm"
        >
          Find My Schemes →
        </button>
      </form>

      {/* Quick query chips */}
      <div className="w-full">
        <p className="text-xs text-slate-400 uppercase tracking-wide mb-2 text-center">
          Popular searches
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {QUICK_QUERIES.map((q) => (
            <button
              key={q}
              onClick={() => handleSubmit(q)}
              className="text-sm px-3 py-1.5 rounded-full bg-white border border-slate-200 text-slate-600 hover:border-blue-400 hover:text-blue-600 transition-colors shadow-sm"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Stats bar */}
      <div className="w-full grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-slate-200">
        {[
          { value: "₹45,000 Cr", label: "Unclaimed annually" },
          { value: "200+", label: "Schemes searchable" },
          { value: "3", label: "Languages" },
          { value: "8s", label: "Avg response time" },
        ].map((stat) => (
          <div key={stat.label} className="text-center">
            <p className="text-xl font-bold text-blue-700">{stat.value}</p>
            <p className="text-xs text-slate-500">{stat.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
