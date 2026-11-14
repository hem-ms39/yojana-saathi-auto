import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

export function GlassCard({
  children,
  className,
  hover = true,
  glow = false,
}: {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
}) {
  return (
    <motion.div
      whileHover={hover ? { y: -4, scale: 1.005 } : undefined}
      transition={{ type: "spring", stiffness: 300, damping: 24 }}
      className={cn(
        "glass gradient-border relative rounded-2xl p-5",
        glow && "shadow-glow",
        className
      )}
    >
      {children}
    </motion.div>
  );
}
