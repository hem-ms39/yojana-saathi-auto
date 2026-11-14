"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "../contexts/auth-context";

interface AuthModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  reason?: string;
}

type Mode = "email" | "sms";
type Step = "input" | "otp";

export function AuthModal({ open, onClose, onSuccess, reason }: AuthModalProps) {
  const { signInWithEmailOtp, verifyEmailOtp, signInWithPhone, verifyPhoneOtp } = useAuth();

  const [mode, setMode] = useState<Mode>("email");
  const [step, setStep] = useState<Step>("input");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resendTimer, setResendTimer] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const otpRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) return;
    setTimeout(() => {
      if (step === "input") inputRef.current?.focus();
      else otpRef.current?.focus();
    }, 100);
  }, [open, step, mode]);

  useEffect(() => {
    if (resendTimer <= 0) return;
    const id = setInterval(() => setResendTimer((t) => t - 1), 1000);
    return () => clearInterval(id);
  }, [resendTimer]);

  useEffect(() => {
    if (!open) {
      setMode("email");
      setStep("input");
      setEmail("");
      setPhone("");
      setOtp("");
      setError(null);
      setLoading(false);
    }
  }, [open]);

  const normalizePhone = (p: string) => {
    const digits = p.replace(/\D/g, "");
    if (digits.length === 10) return `+91${digits}`;
    if (digits.startsWith("91") && digits.length === 12) return `+${digits}`;
    return `+${digits}`;
  };

  // ── Send ────────────────────────────────────────────────────────────
  const handleSend = async () => {
    setLoading(true);
    setError(null);

    if (mode === "email") {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
        setError("Enter a valid email address");
        setLoading(false);
        return;
      }
      const { error } = await signInWithEmailOtp(email.trim());
      setLoading(false);
      if (error) {
        if (error.toLowerCase().includes("rate limit")) {
          setError("Email rate limit reached — use SMS OTP instead ↓");
        } else {
          setError(error);
        }
      } else {
        setStep("otp");
        setResendTimer(30);
      }
    } else {
      const digits = phone.replace(/\D/g, "");
      if (digits.length < 10) {
        setError("Enter a valid 10-digit mobile number");
        setLoading(false);
        return;
      }
      const { error } = await signInWithPhone(normalizePhone(phone));
      setLoading(false);
      if (error) setError(error);
      else { setStep("otp"); setResendTimer(30); }
    }
  };

  // ── Verify ──────────────────────────────────────────────────────────
  const handleVerify = async () => {
    if (otp.length < 6) { setError("Enter the OTP you received"); return; }
    setLoading(true);
    setError(null);

    const { error } =
      mode === "email"
        ? await verifyEmailOtp(email.trim(), otp.trim())
        : await verifyPhoneOtp(normalizePhone(phone), otp.trim());

    setLoading(false);
    if (error) setError(error);
    else { onSuccess?.(); onClose(); }
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" />

      <div className="relative w-full max-w-sm bg-white rounded-2xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-5 text-white">
          <div className="flex items-center justify-between mb-1">
            <span className="text-2xl">🇮🇳</span>
            <button onClick={onClose} className="text-white/70 hover:text-white text-xl">✕</button>
          </div>
          <h2 className="text-lg font-bold">Sign in to Yojana Saathi</h2>
          {reason && <p className="text-blue-100 text-sm mt-0.5">Sign in {reason}</p>}
        </div>

        {/* Mode tabs — Email primary, SMS fallback */}
        <div className="flex border-b border-slate-100">
          <button
            onClick={() => { setMode("email"); setStep("input"); setOtp(""); setError(null); }}
            className={`flex-1 py-2.5 text-sm font-medium transition-colors ${
              mode === "email"
                ? "text-blue-600 border-b-2 border-blue-600"
                : "text-slate-400 hover:text-slate-600"
            }`}
          >
            📧 Email OTP
          </button>
          <button
            onClick={() => { setMode("sms"); setStep("input"); setOtp(""); setError(null); }}
            className={`flex-1 py-2.5 text-sm font-medium transition-colors ${
              mode === "sms"
                ? "text-blue-600 border-b-2 border-blue-600"
                : "text-slate-400 hover:text-slate-600"
            }`}
          >
            📱 SMS OTP
          </button>
        </div>

        <div className="px-6 py-5 space-y-4">
          {step === "input" ? (
            <>
              {mode === "email" ? (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    Email Address
                  </label>
                  <input
                    ref={inputRef}
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    placeholder="you@example.com"
                    className="w-full px-3 py-2.5 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-xs text-slate-400 mt-1.5">
                    A one-time code will be sent to your inbox.
                  </p>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    Mobile Number
                  </label>
                  <div className="flex gap-2">
                    <span className="flex items-center px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-sm text-slate-600 font-medium shrink-0">
                      🇮🇳 +91
                    </span>
                    <input
                      ref={inputRef}
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSend()}
                      placeholder="98765 43210"
                      className="flex-1 px-3 py-2.5 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  <p className="text-xs text-slate-400 mt-1.5">
                    OTP will be sent via SMS to your mobile.
                  </p>
                </div>
              )}

              {error && (
                <div className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">
                  {error}
                  {error.includes("SMS") && (
                    <button
                      onClick={() => { setMode("sms"); setError(null); }}
                      className="block mt-1 text-blue-600 font-medium underline text-xs"
                    >
                      Switch to SMS OTP →
                    </button>
                  )}
                </div>
              )}

              <button
                onClick={handleSend}
                disabled={loading}
                className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold text-sm transition-colors"
              >
                {loading ? "Sending…" : "Send OTP →"}
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => { setStep("input"); setOtp(""); setError(null); }}
                className="text-xs text-blue-600 hover:underline flex items-center gap-1"
              >
                ← Change {mode === "email" ? "email" : "number"}
              </button>

              <p className="text-sm text-slate-600">
                Enter the code sent to{" "}
                <span className="font-semibold text-slate-800">
                  {mode === "email" ? email : `+91 ${phone}`}
                </span>
              </p>

              <input
                ref={otpRef}
                type="text"
                inputMode="numeric"
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 8))}
                onKeyDown={(e) => e.key === "Enter" && handleVerify()}
                placeholder="• • • • • • • •"
                maxLength={8}
                className="w-full px-4 py-3 border border-slate-300 rounded-xl text-center text-2xl font-mono tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-slate-400">
                {mode === "email"
                  ? "Check spam if not received. Enter all digits exactly."
                  : "Enter the SMS code sent to your mobile number."}
              </p>

              {error && (
                <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>
              )}

              <button
                onClick={handleVerify}
                disabled={loading}
                className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold text-sm transition-colors"
              >
                {loading ? "Verifying…" : "Verify & Sign In ✓"}
              </button>

              <div className="text-center">
                {resendTimer > 0 ? (
                  <p className="text-xs text-slate-400">Resend in {resendTimer}s</p>
                ) : (
                  <button
                    onClick={() => { setOtp(""); handleSend(); }}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    Resend OTP
                  </button>
                )}
              </div>
            </>
          )}

          <p className="text-xs text-slate-400 text-center border-t border-slate-100 pt-3">
            Your data is secured and never shared.
          </p>
        </div>
      </div>
    </div>
  );
}
