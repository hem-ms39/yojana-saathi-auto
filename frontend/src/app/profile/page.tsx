"use client";

import { useEffect, useState } from "react";
import { useAuth } from "../../contexts/auth-context";
import { AuthModal } from "../../components/auth-modal";
import { getSupabase } from "../../lib/supabase";

interface Application {
  id: string;
  scheme_id: string;
  status: string;
  applied_at: string;
  form_data: Record<string, unknown>;
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "numeric", month: "short", year: "numeric",
  });
}

const STATUS_COLORS: Record<string, string> = {
  applied: "bg-blue-100 text-blue-700",
  pending: "bg-amber-100 text-amber-700",
  approved: "bg-emerald-100 text-emerald-700",
  rejected: "bg-red-100 text-red-700",
};

export default function ProfilePage() {
  const { user, loading } = useAuth();
  const [showAuth, setShowAuth] = useState(false);
  const [applications, setApplications] = useState<Application[]>([]);
  const [fetching, setFetching] = useState(false);

  useEffect(() => {
    if (!user) return;
    setFetching(true);
    const supabase = getSupabase();
    supabase
      .from("applications")
      .select("id, scheme_id, status, applied_at, form_data")
      .order("applied_at", { ascending: false })
      .then(({ data }) => {
        setApplications((data as Application[]) ?? []);
        setFetching(false);
      });
  }, [user]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-20 bg-slate-100 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (!user) {
    return (
      <>
        <div className="max-w-md mx-auto px-4 py-24 text-center space-y-6">
          <div className="text-6xl">🔐</div>
          <h1 className="text-2xl font-bold text-slate-900">Sign in to view your profile</h1>
          <p className="text-slate-500 text-sm">
            Track all your scheme applications and their statuses in one place.
          </p>
          <button
            onClick={() => setShowAuth(true)}
            className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold transition-colors"
          >
            Sign In with Mobile →
          </button>
        </div>
        <AuthModal
          open={showAuth}
          onClose={() => setShowAuth(false)}
          reason="to view your applications"
        />
      </>
    );
  }

  const displayName = user.phone
    ? `+91 ••••${user.phone.slice(-4)}`
    : user.email ?? "User";

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      {/* Profile header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex items-center gap-4">
        <div className="w-14 h-14 rounded-full bg-blue-600 text-white flex items-center justify-center text-2xl font-bold shrink-0">
          {displayName[0]?.toUpperCase() ?? "U"}
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-900">{displayName}</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {applications.length} application{applications.length !== 1 ? "s" : ""} submitted
          </p>
        </div>
      </div>

      {/* Applications list */}
      <div>
        <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
          My Applications
        </h2>

        {fetching ? (
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <div key={i} className="h-20 bg-slate-100 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : applications.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-10 text-center">
            <div className="text-4xl mb-3">📭</div>
            <p className="text-slate-500 text-sm">No applications yet.</p>
            <a
              href="/"
              className="inline-block mt-4 text-sm text-blue-600 hover:underline"
            >
              Find schemes to apply for →
            </a>
          </div>
        ) : (
          <div className="space-y-3">
            {applications.map((app) => {
              const schemeTitle = (app.form_data?.scheme_title as string) ?? app.scheme_id;
              const appId = (app.form_data?._public_application_id as string) ?? app.id;
              const statusColor = STATUS_COLORS[app.status] ?? "bg-slate-100 text-slate-600";
              return (
                <div
                  key={app.id}
                  className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm flex items-start justify-between gap-4"
                >
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-900 truncate">{schemeTitle}</p>
                    <p className="text-xs text-slate-400 mt-1 font-mono">{appId}</p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Applied {formatDate(app.applied_at)}
                    </p>
                  </div>
                  <span
                    className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-semibold capitalize ${statusColor}`}
                  >
                    {app.status}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
