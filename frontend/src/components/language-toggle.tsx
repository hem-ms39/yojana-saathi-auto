"use client";

import type { Language } from "../types";

const OPTIONS: { value: Language; label: string }[] = [
  { value: "en", label: "EN" },
  { value: "hi", label: "हिं" },
  { value: "kn", label: "ಕನ್ನ" },
];

interface LanguageToggleProps {
  language: Language;
  onChange: (lang: Language) => void;
}

export function LanguageToggle({ language, onChange }: LanguageToggleProps) {
  return (
    <div className="flex rounded-lg border border-slate-200 overflow-hidden">
      {OPTIONS.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          className={`px-3 py-1.5 text-sm font-medium transition-colors ${
            language === opt.value
              ? "bg-blue-600 text-white"
              : "bg-white text-slate-600 hover:bg-slate-50"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
