"use client";

import { useState } from "react";
import { useAuth } from "../contexts/auth-context";
import { AuthModal } from "./auth-modal";

export function NavBar() {
  const { user, loading, signOut } = useAuth();
  const [showAuth, setShowAuth] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);

  // Display email username (e.g. john from john@gmail.com)
  const displayName = user?.email?.split("@")[0] ?? user?.phone?.slice(-4) ?? "User";

  return (
    <>
      <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2 font-bold text-blue-700 text-lg">
            🇮🇳 Yojana Saathi
          </a>

          <nav className="flex items-center gap-4 text-sm text-slate-600">
            <a href="/" className="hover:text-blue-600 transition-colors">Home</a>

            {!loading && (
              user ? (
                <div className="relative">
                  <button
                    onClick={() => setShowDropdown((v) => !v)}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium transition-colors"
                  >
                    <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-xs font-bold">
                      {displayName[0]?.toUpperCase() ?? "U"}
                    </span>
                    <span className="hidden sm:inline">{displayName}</span>
                    <svg className="w-3.5 h-3.5 opacity-60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>

                  {showDropdown && (
                    <>
                      <div className="fixed inset-0 z-10" onClick={() => setShowDropdown(false)} />
                      <div className="absolute right-0 mt-1 w-44 bg-white rounded-xl shadow-lg border border-slate-200 py-1 z-20">
                        <a
                          href="/profile"
                          className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50"
                          onClick={() => setShowDropdown(false)}
                        >
                          📋 My Applications
                        </a>
                        <hr className="my-1 border-slate-100" />
                        <button
                          onClick={() => { signOut(); setShowDropdown(false); }}
                          className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50"
                        >
                          🚪 Sign Out
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                <button
                  onClick={() => setShowAuth(true)}
                  className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm transition-colors"
                >
                  Sign In
                </button>
              )
            )}
          </nav>
        </div>
      </header>

      <AuthModal
        open={showAuth}
        onClose={() => setShowAuth(false)}
        reason="to track your applications"
      />
    </>
  );
}
