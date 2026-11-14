"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { Language } from "../types";

const LANG_MAP: Record<Language, string> = {
  en: "en-IN",
  hi: "hi-IN",
  kn: "kn-IN",
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyRecognition = any;

interface UseSpeechRecognition {
  isListening: boolean;
  transcript: string;
  isSupported: boolean;
  start: () => void;
  stop: () => void;
  reset: () => void;
}

export function useVoice(language: Language = "en"): UseSpeechRecognition {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef<AnyRecognition>(null);
  // Track whether user intentionally stopped vs Chrome's auto-stop
  const stoppedByUserRef = useRef(false);

  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    setIsSupported(!!(w.SpeechRecognition || w.webkitSpeechRecognition));
  }, []);

  const start = useCallback(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    const SR = w.SpeechRecognition || w.webkitSpeechRecognition;
    if (!SR) return;

    stoppedByUserRef.current = false;

    const recognition = new SR();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = LANG_MAP[language];

    recognition.onresult = (event: AnyRecognition) => {
      let finalText = "";
      let interimText = "";
      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += result[0].transcript;
        } else {
          interimText += result[0].transcript;
        }
      }
      setTranscript(finalText || interimText);
    };

    recognition.onerror = (e: AnyRecognition) => {
      // "no-speech" and "aborted" are recoverable — don't kill the session
      if (e.error === "no-speech" || e.error === "aborted") {
        console.warn("SpeechRecognition recoverable error:", e.error);
        return;
      }
      console.error("SpeechRecognition fatal error:", e.error);
      stoppedByUserRef.current = true; // prevent auto-restart
      setIsListening(false);
    };

    recognition.onend = () => {
      // Chrome fires onend after silence or network blip even in continuous mode.
      // Auto-restart unless the user explicitly pressed stop.
      if (!stoppedByUserRef.current) {
        try {
          recognition.start();
          return; // successfully restarted, stay in listening state
        } catch {
          // start() can throw if called too quickly — fall through to stop
        }
      }
      setIsListening(false);
    };

    recognition.start();
    recognitionRef.current = recognition;
    setIsListening(true);
  }, [language]);

  const stop = useCallback(() => {
    stoppedByUserRef.current = true;
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  const reset = useCallback(() => {
    setTranscript("");
  }, []);

  return { isListening, transcript, isSupported, start, stop, reset };
}

