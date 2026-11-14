"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getSupabase } from "../../../lib/supabase";

export default function AuthCallbackPage() {
  const router = useRouter();

  useEffect(() => {
    // Supabase puts the auth tokens in the URL hash — exchange them for a session
    const supabase = getSupabase();
    supabase.auth.getSession().then(({ data }) => {
      if (data.session) {
        router.replace("/");
      } else {
        // Try exchanging the code from the URL
        const code = new URLSearchParams(window.location.search).get("code");
        if (code) {
          supabase.auth.exchangeCodeForSession(code).then(() => {
            router.replace("/");
          });
        } else {
          router.replace("/");
        }
      }
    });
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50">
      <div className="text-center space-y-3">
        <div className="text-4xl animate-pulse">🇮🇳</div>
        <p className="text-slate-600 font-medium">Signing you in…</p>
        <p className="text-slate-400 text-sm">You'll be redirected shortly</p>
      </div>
    </div>
  );
}
