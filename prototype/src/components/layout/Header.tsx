import { Link, useRouterState } from "@tanstack/react-router";
import { Sparkles } from "lucide-react";
import { LanguageSwitcher } from "@/components/landing/LanguageSwitcher";
import { cn } from "@/lib/utils";

export function Header() {
  const path = useRouterState({ select: (r) => r.location.pathname });
  const navItem = (to: string, label: string) => (
    <Link
      to={to}
      className={cn(
        "rounded-full px-3 py-1.5 text-sm transition-colors",
        path === to ? "text-foreground" : "text-muted-foreground hover:text-foreground"
      )}
    >
      {label}
    </Link>
  );
  return (
    <header className="sticky top-0 z-40 border-b border-white/5 bg-background/40 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link to="/" className="flex items-center gap-2">
          <span className="bg-gradient-primary flex h-8 w-8 items-center justify-center rounded-lg shadow-glow">
            <Sparkles className="h-4 w-4 text-primary-foreground" />
          </span>
          <span className="text-sm font-semibold tracking-tight">
            Yojana<span className="text-gradient">Saathi</span>
          </span>
        </Link>
        <nav className="hidden items-center gap-1 sm:flex">
          {navItem("/", "Home")}
          {navItem("/dashboard", "Dashboard")}
        </nav>
        <div className="hidden sm:block">
          <LanguageSwitcher />
        </div>
      </div>
    </header>
  );
}
