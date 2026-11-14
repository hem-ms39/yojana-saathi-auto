"use client";

import { useEffect, useRef, useState } from "react";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/v1";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  streaming?: boolean;
}

interface SchemeChatbotProps {
  schemeId: string;
  schemeTitle: string;
  language?: string;
}

const SUGGESTED_QUESTIONS = [
  "What documents do I need to apply?",
  "Who is eligible for this scheme?",
  "How much funding can I get?",
  "How do I apply for this scheme?",
  "What is the application deadline?",
];

export function SchemeChatbot({ schemeId, schemeTitle, language = "en" }: SchemeChatbotProps) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 150);
  }, [open]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMsg: ChatMessage = { role: "user", content: text.trim() };

    // Build history for backend (excluding currently streaming message)
    const history = messages
      .filter((m) => !m.streaming)
      .map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [
      ...prev,
      userMsg,
      { role: "assistant", content: "", streaming: true },
    ]);
    setInput("");
    setLoading(true);

    abortRef.current = new AbortController();

    try {
      const res = await fetch(`${BACKEND_URL}/schemes/${encodeURIComponent(schemeId)}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text.trim(),
          language,
          history,
          user_profile: (() => {
            try {
              return JSON.parse(localStorage.getItem("ys_profile") || "{}");
            } catch {
              return {};
            }
          })(),
        }),
        signal: abortRef.current.signal,
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("data:")) {
            try {
              const data = JSON.parse(line.slice(5).trim());
              if (data.text) {
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last?.role === "assistant") {
                    updated[updated.length - 1] = {
                      ...last,
                      content: last.content + data.text,
                    };
                  }
                  return updated;
                });
              }
            } catch {
              // ignore parse errors
            }
          }
        }
      }

      // Mark streaming done
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last?.role === "assistant") {
          updated[updated.length - 1] = { ...last, streaming: false };
        }
        return updated;
      });
    } catch (err) {
      if ((err as Error).name !== "AbortError") {
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last?.role === "assistant") {
            updated[updated.length - 1] = {
              role: "assistant",
              content: "Sorry, I couldn't get an answer. Please try again.",
              streaming: false,
            };
          }
          return updated;
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="mt-6">
      {/* Toggle Button */}
      <button
        onClick={() => setOpen((v) => !v)}
        className={`w-full flex items-center justify-between px-5 py-3.5 rounded-xl border-2 transition-all ${
          open
            ? "border-violet-500 bg-violet-50 text-violet-700"
            : "border-slate-200 bg-white text-slate-700 hover:border-violet-300 hover:bg-violet-50"
        }`}
      >
        <div className="flex items-center gap-3">
          <span className="text-xl">🤖</span>
          <div className="text-left">
            <p className="font-semibold text-sm">Ask about this scheme</p>
            <p className="text-xs text-slate-500 mt-0.5">
              AI assistant powered by scheme data + RAG
            </p>
          </div>
        </div>
        <svg
          className={`w-4 h-4 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Chat Panel */}
      {open && (
        <div className="mt-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-violet-600 to-purple-600 px-4 py-3 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <p className="text-white text-sm font-semibold">
              Yojana Saathi AI — {schemeTitle}
            </p>
          </div>

          {/* Messages */}
          <div className="h-72 overflow-y-auto px-4 py-3 space-y-3 bg-slate-50">
            {messages.length === 0 && (
              <div className="space-y-3">
                <p className="text-xs text-slate-500 text-center py-2">
                  Ask any question about this scheme. I use the scheme data + similar schemes to answer accurately.
                </p>
                <div className="flex flex-wrap gap-2">
                  {SUGGESTED_QUESTIONS.map((q) => (
                    <button
                      key={q}
                      onClick={() => sendMessage(q)}
                      className="text-xs px-2.5 py-1.5 rounded-lg bg-white border border-violet-200 text-violet-700 hover:bg-violet-50 transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] px-3 py-2 rounded-xl text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-violet-600 text-white rounded-br-sm"
                      : "bg-white border border-slate-200 text-slate-700 rounded-bl-sm shadow-sm"
                  }`}
                >
                  {msg.content}
                  {msg.streaming && (
                    <span className="inline-block w-1.5 h-3.5 bg-violet-400 ml-0.5 animate-pulse rounded-sm align-middle" />
                  )}
                  {!msg.content && msg.streaming && (
                    <span className="text-slate-400 text-xs italic">Thinking…</span>
                  )}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="px-3 py-2.5 border-t border-slate-100 bg-white flex gap-2 items-center">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about eligibility, documents, funding…"
              disabled={loading}
              className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-400"
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={loading || !input.trim()}
              className="p-2 rounded-lg bg-violet-600 hover:bg-violet-700 disabled:bg-violet-300 text-white transition-colors shrink-0"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
