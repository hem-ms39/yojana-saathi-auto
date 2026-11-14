import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Header } from "@/components/layout/Header";
import { GlassCard } from "@/components/fx/GlassCard";
import { mockSchemes } from "@/lib/mock";
import { ArrowLeft, Check, FileText, Loader2, MessageCircle, ScanLine, Upload, Sparkles } from "lucide-react";
import { toast } from "sonner";

export const Route = createFileRoute("/apply/$schemeId")({
  head: () => ({
    meta: [{ title: "Apply — Yojana Saathi" }],
  }),
  component: Apply,
});

const STEPS = ["Profile", "Documents", "Verification", "Submit", "Done"];

function Apply() {
  const { schemeId } = Route.useParams();
  const scheme = mockSchemes.find((s) => s.id === schemeId) ?? mockSchemes[0];
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [files, setFiles] = useState<{ name: string; size: number }[]>([]);
  const [ocrText, setOcrText] = useState("");
  const [verified, setVerified] = useState(false);

  // OCR typing animation
  useEffect(() => {
    if (step !== 2) return;
    const full = `Name: Anjali Sharma\nDOB: 14-Aug-1992\nAadhaar: XXXX-XXXX-9421\nIncome: ₹2,40,000 / yr\nState: Karnataka\nCategory: Eligible ✓`;
    let i = 0;
    setOcrText("");
    const t = setInterval(() => {
      i += 2;
      setOcrText(full.slice(0, i));
      if (i >= full.length) { clearInterval(t); setTimeout(() => setVerified(true), 500); }
    }, 30);
    return () => clearInterval(t);
  }, [step]);

  const next = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));

  return (
    <div className="relative min-h-screen">
      <Header />
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <Link to="/dashboard" className="mb-4 inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-3.5 w-3.5" /> Back to dashboard
        </Link>

        <div className="mb-6">
          <p className="text-[10px] uppercase tracking-wider text-muted-foreground">{scheme.ministry}</p>
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{scheme.name}</h1>
          <p className="mt-1 text-sm text-muted-foreground">{scheme.description}</p>
        </div>

        {/* Stepper */}
        <div className="mb-8 flex items-center gap-2">
          {STEPS.map((s, i) => (
            <div key={s} className="flex flex-1 items-center gap-2">
              <div
                className={
                  "flex h-7 w-7 items-center justify-center rounded-full text-[11px] font-semibold transition-all " +
                  (i <= step ? "bg-gradient-primary text-primary-foreground shadow-glow" : "bg-white/5 text-muted-foreground")
                }
              >
                {i < step ? <Check className="h-3.5 w-3.5" /> : i + 1}
              </div>
              {i < STEPS.length - 1 && (
                <div className="h-px flex-1" style={{ background: i < step ? "linear-gradient(to right, oklch(0.78 0.18 165), oklch(0.70 0.17 240))" : "oklch(1 0 0 / 8%)" }} />
              )}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            {step === 0 && (
              <GlassCard className="space-y-3">
                <h2 className="text-lg font-semibold">Confirm your profile</h2>
                <div className="grid gap-3 sm:grid-cols-2 text-sm">
                  {[
                    ["Name", "Anjali Sharma"],
                    ["State", "Karnataka"],
                    ["Annual income", "₹2,40,000"],
                    ["Category", "General"],
                  ].map(([k, v]) => (
                    <div key={k} className="rounded-lg border border-white/5 bg-white/5 p-3">
                      <p className="text-[10px] uppercase tracking-wider text-muted-foreground">{k}</p>
                      <p className="mt-0.5 font-medium">{v}</p>
                    </div>
                  ))}
                </div>
              </GlassCard>
            )}

            {step === 1 && (
              <GlassCard className="space-y-4">
                <h2 className="text-lg font-semibold">Upload documents</h2>
                <label className="glass flex cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-white/15 p-8 text-center hover:bg-white/5">
                  <Upload className="mb-2 h-6 w-6 text-muted-foreground" />
                  <p className="text-sm">Drop files or click to upload</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">Aadhaar, income proof, bank passbook</p>
                  <input
                    type="file"
                    multiple
                    className="hidden"
                    onChange={(e) => {
                      const list = Array.from(e.target.files ?? []).map((f) => ({ name: f.name, size: f.size }));
                      setFiles((prev) => [...prev, ...list]);
                    }}
                  />
                </label>
                {files.length === 0 && (
                  <button
                    onClick={() => setFiles([{ name: "aadhaar.pdf", size: 234120 }, { name: "income-proof.jpg", size: 812340 }])}
                    className="text-xs text-muted-foreground underline"
                  >
                    Use demo files
                  </button>
                )}
                <div className="space-y-2">
                  {files.map((f, i) => (
                    <div key={i} className="flex items-center gap-2 rounded-lg border border-white/5 bg-white/5 p-2.5 text-sm">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span className="flex-1 truncate">{f.name}</span>
                      <span className="text-xs text-muted-foreground">{(f.size / 1024).toFixed(0)} KB</span>
                      <Check className="h-4 w-4" style={{ color: "oklch(0.85 0.16 165)" }} />
                    </div>
                  ))}
                </div>
              </GlassCard>
            )}

            {step === 2 && (
              <GlassCard className="space-y-3">
                <div className="flex items-center gap-2">
                  <ScanLine className="h-4 w-4" style={{ color: "oklch(0.85 0.16 165)" }} />
                  <h2 className="text-lg font-semibold">AI verification</h2>
                </div>
                <p className="text-xs text-muted-foreground">Extracting fields from your documents…</p>
                <pre className="glass min-h-[160px] whitespace-pre-wrap rounded-xl p-4 font-mono text-xs leading-relaxed">
                  {ocrText}
                  <span className="ml-0.5 inline-block h-3 w-1 animate-pulse bg-foreground/70 align-middle" />
                </pre>
                {verified && (
                  <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex items-center gap-2 text-sm" style={{ color: "oklch(0.88 0.14 165)" }}>
                    <Check className="h-4 w-4" /> All fields verified
                  </motion.div>
                )}
              </GlassCard>
            )}

            {step === 3 && (
              <GlassCard className="space-y-4">
                <h2 className="text-lg font-semibold">Ready to submit</h2>
                <p className="text-sm text-muted-foreground">Form Agent will file your application and notify you on WhatsApp.</p>
                <button
                  onClick={() => {
                    toast.success("Application submitted", { description: "WhatsApp confirmation queued." });
                    next();
                  }}
                  className="bg-gradient-primary inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-glow"
                >
                  <Sparkles className="h-4 w-4" />
                  Submit application
                </button>
              </GlassCard>
            )}

            {step === 4 && (
              <GlassCard className="text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, damping: 14 }}
                  className="bg-gradient-primary mx-auto flex h-16 w-16 items-center justify-center rounded-full shadow-glow"
                >
                  <Check className="h-8 w-8 text-primary-foreground" />
                </motion.div>
                <h2 className="mt-4 text-xl font-semibold">Application submitted!</h2>
                <p className="mt-1 text-sm text-muted-foreground">Reference: YS-{scheme.id.toUpperCase()}-{Math.floor(Math.random() * 90000 + 10000)}</p>

                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="glass mx-auto mt-6 flex max-w-sm items-center gap-3 rounded-2xl p-3 text-left"
                  style={{ borderColor: "oklch(0.78 0.18 165 / 30%)" }}
                >
                  <div className="flex h-10 w-10 items-center justify-center rounded-full" style={{ background: "oklch(0.78 0.18 165 / 20%)" }}>
                    <MessageCircle className="h-5 w-5" style={{ color: "oklch(0.88 0.14 165)" }} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium">WhatsApp sent</p>
                    <p className="truncate text-xs text-muted-foreground">Updates will be sent to +91 ●●●●● 4321</p>
                  </div>
                </motion.div>

                <button
                  onClick={() => navigate({ to: "/dashboard" })}
                  className="glass mt-6 inline-flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-medium hover:bg-white/10"
                >
                  Back to schemes
                </button>
              </GlassCard>
            )}
          </motion.div>
        </AnimatePresence>

        {step < 3 && (
          <div className="mt-6 flex justify-between">
            <button onClick={prev} disabled={step === 0} className="text-sm text-muted-foreground disabled:opacity-30">
              Back
            </button>
            <button
              onClick={next}
              disabled={step === 2 && !verified}
              className="bg-gradient-primary inline-flex items-center gap-2 rounded-full px-5 py-2 text-sm font-semibold text-primary-foreground shadow-glow disabled:opacity-50"
            >
              {step === 2 && !verified ? (<><Loader2 className="h-4 w-4 animate-spin" />Verifying</>) : "Continue"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
