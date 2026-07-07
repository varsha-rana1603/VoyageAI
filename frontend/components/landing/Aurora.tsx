"use client";

import { motion } from "framer-motion";

export default function Aurora() {
  return (
    <div className="absolute inset-0 overflow-hidden">
      <motion.div
        animate={{ x: [-150, 100, -150], y: [0, 120, 0] }}
        transition={{ repeat: Infinity, duration: 20, ease: "easeInOut" }}
        className="absolute left-0 top-0 h-[700px] w-[700px] rounded-full bg-cyan-500/20 blur-[140px]"
      />
      <motion.div
        animate={{ x: [100, -120, 100], y: [50, -50, 50] }}
        transition={{ repeat: Infinity, duration: 22, ease: "easeInOut" }}
        className="absolute right-0 top-20 h-[700px] w-[700px] rounded-full bg-purple-500/20 blur-[160px]"
      />
    </div>
  );
}