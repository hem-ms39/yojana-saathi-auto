import type { Language } from "./types";

export const dict = {
  en: {
    headline: "Find Every Government Benefit You Deserve",
    sub: "AI agents discover, match, and auto-apply to schemes from 1,200+ programs — so you never miss what's yours.",
    startVoice: "Start with Voice",
    explore: "Explore Schemes",
    listening: "Listening… (demo)",
    tapToSpeak: "Tap to speak",
    poweredBy: "Powered by AI Agents · 1,200+ schemes · WhatsApp updates",
  },
  hi: {
    headline: "हर सरकारी लाभ पाएँ जो आपका हक़ है",
    sub: "AI एजेंट 1,200+ योजनाओं से आपके लिए खोज, मिलान और स्वचालित आवेदन करते हैं।",
    startVoice: "आवाज़ से शुरू करें",
    explore: "योजनाएँ देखें",
    listening: "सुन रहा हूँ… (डेमो)",
    tapToSpeak: "बोलने के लिए टैप करें",
    poweredBy: "AI एजेंट्स · 1,200+ योजनाएँ · WhatsApp अपडेट",
  },
  kn: {
    headline: "ನಿಮಗೆ ಸಲ್ಲಬೇಕಾದ ಪ್ರತಿ ಯೋಜನೆಯ ಲಾಭವನ್ನು ಪಡೆಯಿರಿ",
    sub: "AI ಏಜೆಂಟ್‌ಗಳು 1,200+ ಯೋಜನೆಗಳಿಂದ ಹುಡುಕಿ, ಹೊಂದಿಸಿ ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಅರ್ಜಿ ಸಲ್ಲಿಸುತ್ತವೆ.",
    startVoice: "ಧ್ವನಿಯಿಂದ ಪ್ರಾರಂಭಿಸಿ",
    explore: "ಯೋಜನೆಗಳನ್ನು ನೋಡಿ",
    listening: "ಆಲಿಸುತ್ತಿದೆ… (ಡೆಮೊ)",
    tapToSpeak: "ಮಾತನಾಡಲು ಟ್ಯಾಪ್ ಮಾಡಿ",
    poweredBy: "AI ಏಜೆಂಟ್‌ಗಳು · 1,200+ ಯೋಜನೆಗಳು · WhatsApp ನವೀಕರಣಗಳು",
  },
} as const satisfies Record<Language, Record<string, string>>;

export type Dict = typeof dict["en"];
