"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import {
  getScheme,
  applyForScheme,
  uploadDocument,
  attemptPortalSubmit,
  backendStaticUrl,
  type PortalAttemptResult,
} from "../../../lib/api";
import type { SchemeDetail, UserProfile } from "../../../types";
import { useAuth } from "../../../contexts/auth-context";
import { AuthModal } from "../../../components/auth-modal";
import { SchemeChatbot } from "../../../components/scheme-chatbot";

interface ApplyForm {
  // Personal
  full_name: string;
  dob: string;
  gender: string;
  mobile: string;
  // Identity
  aadhaar: string;
  pan: string;
  // Address
  state: string;
  district: string;
  pincode: string;
  // Financial
  income_annual: string;
  caste_category: string;
  bank_account: string;
  ifsc_code: string;
  // Occupation
  occupation: string;
  business_type: string;
}

const EMPTY_FORM: ApplyForm = {
  full_name: "",
  dob: "",
  gender: "",
  mobile: "",
  aadhaar: "",
  pan: "",
  state: "",
  district: "",
  pincode: "",
  income_annual: "",
  caste_category: "",
  bank_account: "",
  ifsc_code: "",
  occupation: "",
  business_type: "",
};

const STATES = [
  "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
  "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka",
  "Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram",
  "Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
  "Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Delhi","Jammu & Kashmir",
];

function formatAmount(amount: number): string {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)} Crore`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)} Lakh`;
  if (amount >= 1000) return `₹${(amount / 1000).toFixed(0)}K`;
  return `₹${amount}`;
}

function profileToForm(p: UserProfile): Partial<ApplyForm> {
  return {
    gender: p.gender ?? "",
    state: p.state ?? "",
    district: p.district ?? "",
    income_annual: p.income_annual ? String(p.income_annual) : "",
    caste_category: p.caste_category ?? "",
    occupation: p.occupation ?? "",
    business_type: p.business_intent ?? "",
  };
}

function Field({
  label,
  required,
  children,
  hint,
  ocr,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
  hint?: string;
  ocr?: boolean;
}) {
  return (
    <div>
      <div className="flex items-center gap-1.5 mb-1">
        <label className="block text-sm font-medium text-slate-700">
          {label}
          {required && <span className="text-red-500 ml-0.5">*</span>}
        </label>
        {ocr && (
          <span className="text-xs bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded font-medium">
            ✦ OCR
          </span>
        )}
      </div>
      {children}
      {hint && <p className="text-xs text-slate-400 mt-1">{hint}</p>}
    </div>
  );
}

const inputCls = (filled?: boolean) =>
  `w-full rounded-lg border px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:border-transparent ${
    filled
      ? "border-emerald-400 bg-emerald-50 focus:ring-emerald-400"
      : "border-slate-300 focus:ring-blue-500"
  }`;
const selectCls = (filled?: boolean) => inputCls(filled) + " bg-white";

export default function SchemeDetailPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const schemeId = decodeURIComponent(params.id as string);
  const lang = searchParams.get("lang") ?? "en";
  const autoApply = searchParams.get("apply") === "1";
  const { user } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  const [scheme, setScheme] = useState<SchemeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const [showApplyForm, setShowApplyForm] = useState(autoApply);
  const [form, setForm] = useState<ApplyForm>(EMPTY_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [applying, setApplying] = useState(false);
  const [applicationResult, setApplicationResult] = useState<{
    application_id: string;
    whatsapp_sent: boolean;
    next_steps?: string | null;
  } | null>(null);

  const [portalAttempt, setPortalAttempt] = useState<PortalAttemptResult | null>(null);
  const [portalAttemptLoading, setPortalAttemptLoading] = useState(false);
  const [portalAttemptError, setPortalAttemptError] = useState<string | null>(null);

  // OCR state
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrError, setOcrError] = useState<string | null>(null);
  const [ocrFilled, setOcrFilled] = useState<Set<string>>(new Set());
  const [ocrDocType, setOcrDocType] = useState<string | null>(null);
  const [ocrConfidence, setOcrConfidence] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load scheme
  useEffect(() => {
    getScheme(schemeId, lang)
      .then(setScheme)
      .catch((err: Error) => setFetchError(err.message))
      .finally(() => setLoading(false));
  }, [schemeId, lang]);

  // Pre-fill form from profile saved during search
  useEffect(() => {
    if (!showApplyForm) return;
    try {
      const raw = localStorage.getItem("ys_profile");
      if (raw) {
        const profile = JSON.parse(raw) as UserProfile;
        setForm((prev) => ({ ...prev, ...profileToForm(profile) }));
      }
    } catch {
      // ignore
    }
  }, [showApplyForm]);

  const set = (field: keyof ApplyForm) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleDocumentUpload = async (file: File) => {
    setOcrLoading(true);
    setOcrError(null);
    setOcrFilled(new Set());

    try {
      const result = await uploadDocument(file, schemeId, "auto");
      const p = result.user_profile;
      const filled = new Set<string>();

      const GENDER_MAP: Record<string, string> = { M: "male", F: "female", Other: "other" };

      const updates: Partial<ApplyForm> = {};
      if (p.name)            { updates.full_name     = p.name;           filled.add("full_name"); }
      if (p.dob)             { updates.dob            = p.dob;            filled.add("dob"); }
      if (p.gender)          { updates.gender         = GENDER_MAP[p.gender] ?? p.gender.toLowerCase(); filled.add("gender"); }
      if (p.aadhaar)         { updates.aadhaar        = p.aadhaar;        filled.add("aadhaar"); }
      if (p.pan)             { updates.pan            = p.pan;            filled.add("pan"); }
      if (p.state)           { updates.state          = p.state;          filled.add("state"); }
      if (p.district)        { updates.district       = p.district;       filled.add("district"); }
      if (p.pincode)         { updates.pincode        = p.pincode;        filled.add("pincode"); }
      if (p.annual_income)   { updates.income_annual  = String(p.annual_income); filled.add("income_annual"); }
      if (p.caste_category)  { updates.caste_category = p.caste_category; filled.add("caste_category"); }
      if (p.bank_account)    { updates.bank_account   = p.bank_account;   filled.add("bank_account"); }
      if (p.ifsc)            { updates.ifsc_code      = p.ifsc;           filled.add("ifsc_code"); }

      setForm((prev) => ({ ...prev, ...updates }));
      setOcrFilled(filled);
      setOcrDocType(result.document?.type ?? null);
      setOcrConfidence(result.document?.confidence ?? null);
    } catch (err) {
      setOcrError(err instanceof Error ? err.message : "OCR failed");
    } finally {
      setOcrLoading(false);
    }
  };

  const validate = (): string | null => {
    if (!form.full_name.trim()) return "Full name is required";
    if (!form.dob) return "Date of birth is required";
    if (!form.mobile.trim()) return "Mobile number is required";
    const aadhaarClean = form.aadhaar.replace(/[\s-]/g, "");
    const isFull = /^\d{12}$/.test(aadhaarClean);
    const isMasked = /^[Xx*]{8}\d{4}$/.test(aadhaarClean);
    if (!isFull && !isMasked)
      return "Enter a valid Aadhaar number (12 digits or as shown on card)";
    if (!form.state) return "State is required";
    return null;
  };

  const handleApply = async () => {
    const err = validate();
    if (err) { setFormError(err); return; }
    setFormError(null);
    setApplying(true);

    try {
      const result = await applyForScheme({
        user_id: `user-${form.aadhaar.slice(-4) || "demo"}`,
        scheme_id: schemeId,
        form_data: {
          full_name: form.full_name,
          dob: form.dob,
          gender: form.gender,
          aadhaar: form.aadhaar,
          pan: form.pan,
          state: form.state,
          district: form.district,
          pincode: form.pincode,
          income_annual: form.income_annual ? Number(form.income_annual) : null,
          caste_category: form.caste_category,
          bank_account: form.bank_account,
          ifsc_code: form.ifsc_code,
          occupation: form.occupation,
          business_type: form.business_type,
          scheme_title: scheme?.title,
        },
        notify_phone: form.mobile || undefined,
        user_profile: {
          age: form.dob
            ? new Date().getFullYear() - new Date(form.dob).getFullYear()
            : undefined,
          gender: form.gender || undefined,
          state: form.state || undefined,
          district: form.district || undefined,
          income_annual: form.income_annual ? Number(form.income_annual) : undefined,
          caste_category: form.caste_category || undefined,
          occupation: form.occupation || undefined,
          business_intent: form.business_type || undefined,
        },
      });
      setApplicationResult(result);
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "Apply failed");
    } finally {
      setApplying(false);
    }
  };

  // ── Loading ──────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-24 bg-slate-100 rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (fetchError || !scheme) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <p className="text-red-600 mb-4">{fetchError ?? "Scheme not found"}</p>
        <a href="/" className="text-blue-600 hover:underline text-sm">← Back to search</a>
      </div>
    );
  }

  // ── Success ──────────────────────────────────────────────────────────────
  if (applicationResult) {
    const handlePortalAttempt = async () => {
      setPortalAttemptLoading(true);
      setPortalAttemptError(null);
      setPortalAttempt(null);
      try {
        const result = await attemptPortalSubmit({
          full_name: form.full_name || "Demo User",
          aadhaar: "111111111111",
          application_id: applicationResult.application_id,
          headless: false,
        });
        setPortalAttempt(result);
      } catch (err) {
        setPortalAttemptError(
          err instanceof Error ? err.message : "Portal attempt failed",
        );
      } finally {
        setPortalAttemptLoading(false);
      }
    };

    const screenshotSrc = backendStaticUrl(portalAttempt?.screenshot_url ?? null);

    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center space-y-6">
        <div className="text-6xl">🎉</div>
        <h2 className="text-2xl font-bold text-slate-900">Application Submitted!</h2>
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 text-left space-y-3">
          <p className="text-sm">
            <span className="text-slate-500">Application ID:</span>{" "}
            <span className="font-mono font-semibold text-emerald-700">
              {applicationResult.application_id}
            </span>
          </p>
          <p className="text-sm">
            <span className="text-slate-500">Scheme:</span>{" "}
            <span className="font-medium text-slate-800">{scheme.title}</span>
          </p>
          <p className="text-sm">
            <span className="text-slate-500">WhatsApp:</span>{" "}
            {applicationResult.whatsapp_sent ? (
              <span className="text-emerald-600 font-medium">✅ Confirmation sent</span>
            ) : (
              <span className="text-slate-400">Not configured</span>
            )}
          </p>
          {applicationResult.next_steps && (
            <p className="text-sm text-slate-600 bg-white rounded-lg p-3 border border-emerald-100">
              {applicationResult.next_steps}
            </p>
          )}
        </div>

        {/* Real-portal attempt section */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 text-left space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-slate-800 uppercase tracking-wide">
              Try on the real Government portal
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Demonstrates that the system can drive a live Govt of India portal.
              We send a fake Aadhaar (111111111111) so the portal correctly rejects
              it — proving the integration is real, not simulated.
            </p>
          </div>

          {!portalAttempt && !portalAttemptLoading && (
            <button
              onClick={handlePortalAttempt}
              className="w-full py-2.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white font-medium text-sm transition-colors"
            >
              Attempt submission on udyamregistration.gov.in →
            </button>
          )}

          {portalAttemptLoading && (
            <div className="flex items-center gap-3 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <svg className="animate-spin h-5 w-5 text-amber-600 shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              <div>
                <p className="text-sm font-medium text-amber-800">Driving the real portal…</p>
                <p className="text-xs text-amber-600">A browser window will pop up. Watch it fill the form and get rejected.</p>
              </div>
            </div>
          )}

          {portalAttemptError && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {portalAttemptError}
            </div>
          )}

          {portalAttempt && (
            <div className="space-y-3">
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-left">
                <p className="text-xs font-semibold text-red-700 uppercase tracking-wide">
                  Portal rejected — as expected
                </p>
                <p className="text-sm text-red-800 mt-1">
                  {portalAttempt.error_message}
                </p>
                {portalAttempt.fake_aadhaar_used && (
                  <p className="text-xs text-red-500 mt-2">
                    Submitted with: {portalAttempt.fake_aadhaar_used}
                  </p>
                )}
              </div>

              {screenshotSrc && (
                <a
                  href={screenshotSrc}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={screenshotSrc}
                    alt="Portal rejection screenshot"
                    className="w-full rounded-lg border border-slate-200 hover:border-blue-400 transition-colors"
                  />
                  <p className="text-xs text-center text-slate-400 mt-1">
                    Click to open full size — captured from {portalAttempt.portal}
                  </p>
                </a>
              )}

              {portalAttempt.field_log.length > 0 && (
                <details className="text-xs">
                  <summary className="cursor-pointer text-slate-500 hover:text-slate-700">
                    Automation log ({portalAttempt.field_log.length} steps)
                  </summary>
                  <ul className="mt-2 space-y-1 pl-4 text-slate-600">
                    {portalAttempt.field_log.map((step, i) => (
                      <li key={i} className="font-mono">→ {step}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          )}
        </div>

        <a
          href="/"
          className="inline-block px-6 py-2.5 rounded-xl bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
        >
          Search more schemes
        </a>
      </div>
    );
  }

  // ── Main detail view ─────────────────────────────────────────────────────
  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-6">
      <button
        onClick={() => window.history.back()}
        className="text-sm text-blue-600 hover:underline"
      >
        ← Back to results
      </button>

      {/* Scheme header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h1 className="text-2xl font-bold text-slate-900">{scheme.title}</h1>
        <div className="flex flex-wrap gap-6">
          {scheme.funding_amount > 0 && (
            <div>
              <p className="text-3xl font-bold text-blue-700">
                {formatAmount(scheme.funding_amount)}
              </p>
              <p className="text-xs text-slate-500">Maximum funding</p>
            </div>
          )}
          {scheme.deadline && (
            <div>
              <p className="text-lg font-semibold text-slate-800">{scheme.deadline}</p>
              <p className="text-xs text-slate-500">Deadline</p>
            </div>
          )}
          {scheme.ministry && (
            <div>
              <p className="text-sm font-medium text-slate-700">{scheme.ministry}</p>
              <p className="text-xs text-slate-500">Ministry</p>
            </div>
          )}
        </div>
        {scheme.summary && (
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">About</h3>
            <p className="text-sm text-slate-600 leading-relaxed">{scheme.summary}</p>
          </div>
        )}
      </div>

      {scheme.eligibility_text && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Eligibility Criteria
          </h3>
          <p className="text-sm text-slate-600 whitespace-pre-line leading-relaxed">
            {scheme.eligibility_text}
          </p>
        </div>
      )}

      {scheme.documents_required?.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">
            Documents Required
          </h3>
          <ul className="space-y-1.5">
            {scheme.documents_required.map((doc) => (
              <li key={doc} className="flex items-center gap-2 text-sm text-slate-600">
                <span className="text-emerald-500">✓</span> {doc}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Scheme Q&A Chatbot */}
      {scheme && (
        <SchemeChatbot
          schemeId={schemeId}
          schemeTitle={scheme.title}
          language={lang}
        />
      )}

      {/* Apply CTA or Form */}
      {!showApplyForm ? (
        <>
          {user ? (
            <button
              onClick={() => setShowApplyForm(true)}
              className="w-full py-4 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg transition-colors shadow-md"
            >
              Auto-Apply for this scheme →
            </button>
          ) : (
            <button
              onClick={() => setShowAuthModal(true)}
              className="w-full py-4 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-lg transition-colors shadow-md flex items-center justify-center gap-2"
            >
              🔐 Sign In to Apply
            </button>
          )}
        </>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="bg-blue-600 px-6 py-4">
            <h2 className="text-white font-bold text-lg">Application Form</h2>
            <p className="text-blue-100 text-sm mt-0.5">
              Fields marked <span className="text-white font-bold">*</span> are required.
              Pre-filled from your search where possible.
            </p>
          </div>

          <div className="p-6 space-y-8">

            {/* ── Aadhaar / Document Upload ── */}
            <section>
              <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide border-b border-slate-100 pb-2 mb-4">
                Upload ID Document <span className="text-slate-400 font-normal normal-case">(auto-fills the form)</span>
              </h3>

              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.webp"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleDocumentUpload(file);
                  e.target.value = "";
                }}
              />

              {!ocrDocType && !ocrLoading && (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full border-2 border-dashed border-slate-300 hover:border-blue-400 rounded-xl p-6 text-center transition-colors group"
                >
                  <div className="text-3xl mb-2">📄</div>
                  <p className="text-sm font-medium text-slate-700 group-hover:text-blue-600">
                    Upload Aadhaar, PAN, Passbook, or Income Certificate
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    PDF, JPG, PNG supported · Gemini Vision extracts all fields automatically
                  </p>
                  <span className="inline-block mt-3 px-4 py-1.5 rounded-lg bg-blue-600 text-white text-xs font-medium">
                    Choose File
                  </span>
                </button>
              )}

              {ocrLoading && (
                <div className="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                  <svg className="animate-spin h-5 w-5 text-blue-600 shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-blue-800">Extracting details with AI…</p>
                    <p className="text-xs text-blue-500">Gemini Vision is reading your document</p>
                  </div>
                </div>
              )}

              {ocrError && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex items-start gap-2">
                  <span className="shrink-0">⚠️</span>
                  <div>
                    <p className="font-medium">Could not extract details</p>
                    <p className="text-xs text-red-500 mt-0.5">{ocrError}</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => { setOcrError(null); fileInputRef.current?.click(); }}
                    className="ml-auto text-xs underline text-red-600 shrink-0"
                  >
                    Try again
                  </button>
                </div>
              )}

              {ocrDocType && !ocrLoading && (
                <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-emerald-800">
                      ✅ {ocrFilled.size} fields auto-filled
                    </p>
                    <div className="flex items-center gap-2">
                      {ocrConfidence !== null && (
                        <span className="text-xs text-emerald-600">
                          {Math.round(ocrConfidence * 100)}% confidence
                        </span>
                      )}
                      <button
                        type="button"
                        onClick={() => { setOcrDocType(null); setOcrFilled(new Set()); fileInputRef.current?.click(); }}
                        className="text-xs text-emerald-700 underline"
                      >
                        Upload another
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-emerald-600 capitalize">
                    Document detected: {ocrDocType.replace(/_/g, " ")}
                  </p>
                  <p className="text-xs text-slate-500">
                    Review the fields below and fill in anything that was not extracted.
                  </p>
                </div>
              )}
            </section>

            {/* Section 1: Personal */}
            <section>
              <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide border-b border-slate-100 pb-2 mb-4">
                Personal Information
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Full Name" required ocr={ocrFilled.has("full_name")}>
                  <input type="text" value={form.full_name} onChange={set("full_name")}
                    placeholder="As on Aadhaar card" className={inputCls(ocrFilled.has("full_name"))} />
                </Field>
                <Field label="Date of Birth" required ocr={ocrFilled.has("dob")}>
                  <input type="date" value={form.dob} onChange={set("dob")} className={inputCls(ocrFilled.has("dob"))} />
                </Field>
                <Field label="Gender" ocr={ocrFilled.has("gender")}>
                  <select value={form.gender} onChange={set("gender")} className={selectCls(ocrFilled.has("gender"))}>
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other / Prefer not to say</option>
                  </select>
                </Field>
                <Field label="Mobile Number" required hint="Used for WhatsApp application updates">
                  <input type="tel" value={form.mobile} onChange={set("mobile")}
                    placeholder="+91 98765 43210" className={inputCls()} />
                </Field>
              </div>
            </section>

            {/* Section 2: Identity */}
            <section>
              <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide border-b border-slate-100 pb-2 mb-4">
                Identity Documents
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Aadhaar Number" required hint="Last 4 digits shown when extracted from document" ocr={ocrFilled.has("aadhaar")}>
                  <input type="text" value={form.aadhaar} onChange={set("aadhaar")}
                    placeholder="XXXX XXXX XXXX" maxLength={14} className={inputCls(ocrFilled.has("aadhaar"))} />
                </Field>
                <Field label="PAN Number" hint="Optional – required for income-based schemes" ocr={ocrFilled.has("pan")}>
                  <input type="text" value={form.pan} onChange={set("pan")}
                    placeholder="ABCDE1234F" maxLength={10}
                    className={inputCls(ocrFilled.has("pan")) + " uppercase"} />
                </Field>
              </div>
            </section>

            {/* Section 3: Address */}
            <section>
              <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide border-b border-slate-100 pb-2 mb-4">
                Address
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="State" required ocr={ocrFilled.has("state")}>
                  <select value={form.state} onChange={set("state")} className={selectCls(ocrFilled.has("state"))}>
                    <option value="">Select state</option>
                    {STATES.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </Field>
                <Field label="District" ocr={ocrFilled.has("district")}>
                  <input type="text" value={form.district} onChange={set("district")}
                    placeholder="e.g. Bengaluru Urban" className={inputCls(ocrFilled.has("district"))} />
                </Field>
                <Field label="Pincode" ocr={ocrFilled.has("pincode")}>
                  <input type="text" value={form.pincode} onChange={set("pincode")}
                    placeholder="6-digit pincode" maxLength={6} className={inputCls(ocrFilled.has("pincode"))} />
                </Field>
              </div>
            </section>

            {/* Section 4: Financial */}
            <section>
              <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide border-b border-slate-100 pb-2 mb-4">
                Financial Details
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Annual Income (₹)" hint="Household annual income in rupees" ocr={ocrFilled.has("income_annual")}>
                  <input type="number" value={form.income_annual} onChange={set("income_annual")}
                    placeholder="e.g. 150000" className={inputCls(ocrFilled.has("income_annual"))} />
                </Field>
                <Field label="Caste Category" ocr={ocrFilled.has("caste_category")}>
                  <select value={form.caste_category} onChange={set("caste_category")} className={selectCls(ocrFilled.has("caste_category"))}>
                    <option value="">Select category</option>
                    <option value="General">General</option>
                    <option value="OBC">OBC</option>
                    <option value="SC">SC (Scheduled Caste)</option>
                    <option value="ST">ST (Scheduled Tribe)</option>
                    <option value="NT">NT (Nomadic Tribe)</option>
                  </select>
                </Field>
                <Field label="Bank Account Number" hint="Where the scheme benefit will be deposited" ocr={ocrFilled.has("bank_account")}>
                  <input type="text" value={form.bank_account} onChange={set("bank_account")}
                    placeholder="Account number" className={inputCls(ocrFilled.has("bank_account"))} />
                </Field>
                <Field label="IFSC Code" ocr={ocrFilled.has("ifsc_code")}>
                  <input type="text" value={form.ifsc_code} onChange={set("ifsc_code")}
                    placeholder="e.g. SBIN0001234" maxLength={11}
                    className={inputCls(ocrFilled.has("ifsc_code")) + " uppercase"} />
                </Field>
              </div>
            </section>

            {/* Section 5: Occupation */}
            <section>
              <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide border-b border-slate-100 pb-2 mb-4">
                Occupation
              </h3>
              <div className="grid gap-4 sm:grid-cols-2">
                <Field label="Occupation">
                  <input type="text" value={form.occupation} onChange={set("occupation")}
                    placeholder="e.g. Tailor, Farmer, Student" className={inputCls()} />
                </Field>
                <Field label="Business Type" hint="If applying for a business scheme">
                  <input type="text" value={form.business_type} onChange={set("business_type")}
                    placeholder="e.g. Tailoring, Food processing" className={inputCls()} />
                </Field>
              </div>
            </section>

            {/* Error */}
            {formError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {formError}
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <button
                onClick={() => setShowApplyForm(false)}
                className="flex-1 py-3 rounded-xl border border-slate-300 text-slate-600 text-sm font-medium hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleApply}
                disabled={applying}
                className="flex-2 flex-grow py-3 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold text-sm transition-colors"
              >
                {applying ? "Submitting…" : "Submit Application"}
              </button>
            </div>
          </div>
        </div>
      )}

      {scheme.application_url && (
        <a
          href={scheme.application_url}
          target="_blank"
          rel="noopener noreferrer"
          className="block text-center text-sm text-blue-600 hover:underline pb-6"
        >
          Apply directly on official portal ↗
        </a>
      )}

      {/* Auth gate modal */}
      <AuthModal
        open={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={() => { setShowAuthModal(false); setShowApplyForm(true); }}
        reason="to apply for this scheme"
      />
    </div>
  );
}
