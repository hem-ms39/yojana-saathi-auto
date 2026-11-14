import { useApp } from "@/lib/store";
import type { Language } from "@/lib/types";
import { cn } from "@/lib/utils";

const langs: { code: Language; label: string }[] = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी" },
  { code: "kn", label: "ಕನ್ನಡ" },
];

export function LanguageSwitcher() {
  const language = useApp((s) => s.language);
  const setLanguage = useApp((s) => s.setLanguage);
  return (
    <div className="glass inline-flex rounded-full p-1 text-sm">
      {langs.map((l) => (
        <button
          key={l.code}
          onClick={() => setLanguage(l.code)}
          className={cn(
            "rounded-full px-4 py-1.5 transition-all",
            language === l.code
              ? "bg-gradient-primary text-primary-foreground shadow-glow"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          {l.label}
        </button>
      ))}
    </div>
  );
}
