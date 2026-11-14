import { motion } from "framer-motion";
import { Mic } from "lucide-react";

export function VoiceOrb({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <div className="relative flex h-72 w-72 items-center justify-center sm:h-80 sm:w-80">
      {/* halo gradient */}
      <div
        className="absolute inset-0 rounded-full opacity-70 blur-3xl"
        style={{ background: "radial-gradient(circle, oklch(0.78 0.18 165 / 50%), transparent 60%)" }}
      />
      {/* pulse rings */}
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="absolute rounded-full border border-[oklch(0.78_0.18_165_/_40%)]"
          initial={{ width: 180, height: 180, opacity: 0.6 }}
          animate={
            active
              ? { width: [180, 320], height: [180, 320], opacity: [0.6, 0] }
              : { width: 200 + i * 24, height: 200 + i * 24, opacity: 0.25 }
          }
          transition={{ duration: 2.4, repeat: Infinity, delay: i * 0.6, ease: "easeOut" }}
        />
      ))}

      <motion.button
        onClick={onClick}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="bg-gradient-primary relative z-10 flex h-32 w-32 items-center justify-center rounded-full text-primary-foreground shadow-glow ring-1 ring-white/20"
        aria-label={label}
      >
        <Mic className="h-12 w-12" strokeWidth={2.2} />
      </motion.button>

      {/* waveform */}
      <div className="absolute -bottom-2 flex items-end gap-1.5">
        {Array.from({ length: 18 }).map((_, i) => (
          <motion.span
            key={i}
            className="block w-1 rounded-full bg-gradient-to-t from-emerald to-blue"
            style={{ background: "linear-gradient(to top, oklch(0.78 0.18 165), oklch(0.70 0.17 240))" }}
            animate={
              active
                ? { height: [4, 6 + Math.random() * 28, 4] }
                : { height: [4, 8, 4] }
            }
            transition={{ duration: 0.9 + Math.random() * 0.6, repeat: Infinity, delay: i * 0.05 }}
          />
        ))}
      </div>
    </div>
  );
}
