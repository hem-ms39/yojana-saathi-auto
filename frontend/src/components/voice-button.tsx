"use client";

import { useEffect, useRef } from "react";
import type { Language } from "../types";
import { useVoice } from "../hooks/use-voice";

interface VoiceButtonProps {
  language: Language;
  onTranscript: (text: string) => void;
}

export function VoiceButton({ language, onTranscript }: VoiceButtonProps) {
  const { isListening, transcript, isSupported, start, stop, reset } = useVoice(language);
  const onTranscriptRef = useRef(onTranscript);
  onTranscriptRef.current = onTranscript;

  const handleClick = () => {
    if (isListening) {
      stop();
    } else {
      reset();
      start();
    }
  };

  // Pass transcript up when it changes (via effect, not during render)
  useEffect(() => {
    if (transcript) {
      onTranscriptRef.current(transcript);
    }
  }, [transcript]);

  if (!isSupported) {
    return (
      <div className="text-sm text-slate-400 text-center">
        Voice not supported in this browser. Use text input.
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center gap-3">
      <button
        onClick={handleClick}
        className={`relative w-20 h-20 rounded-full flex items-center justify-center text-3xl transition-all duration-200 shadow-lg ${
          isListening
            ? "bg-red-500 hover:bg-red-600 scale-110"
            : "bg-blue-600 hover:bg-blue-700"
        }`}
        title={isListening ? "Stop listening" : "Tap to speak"}
      >
        {isListening && (
          <span className="absolute inset-0 rounded-full bg-red-400 animate-ping opacity-60" />
        )}
        <span className="relative">{isListening ? "⏹" : "🎤"}</span>
      </button>
      <p className="text-sm text-slate-500">
        {isListening ? `Listening… ${transcript || ""}` : "Tap to speak"}
      </p>
    </div>
  );
}

