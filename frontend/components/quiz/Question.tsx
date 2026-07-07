"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import {
  Mountain,
  Waves,
  Trees,
  Building2,
  Landmark,
  Sparkles,
  Wallet,
  Crown,
  Users,
  UserX,
} from "lucide-react";

interface Props {
  question: string;
  options: string[];
  onAnswer: (answer: string) => void;
}

export default function Question({
  question,
  options,
  onAnswer,
}: Props) {
  const [selected, setSelected] = useState<string | null>(null);

  function getIcon(option: string) {
    switch (option.toLowerCase()) {
      case "adventure":
        return <Mountain size={28} />;
      case "relaxation":
        return <Waves size={28} />;
      case "culture":
        return <Landmark size={28} />;
      case "luxury":
        return <Crown size={28} />;
      case "offbeat":
        return <Sparkles size={28} />;
      case "budget":
        return <Wallet size={28} />;
      case "medium":
        return <Wallet size={28} />;
      case "love crowds":
        return <Users size={28} />;
      case "avoid crowds":
        return <UserX size={28} />;
      case "mountains":
        return <Mountain size={28} />;
      case "beach":
        return <Waves size={28} />;
      case "forest":
        return <Trees size={28} />;
      case "city":
        return <Building2 size={28} />;
      default:
        return <Sparkles size={28} />;
    }
  }

  const handleClick = (option: string) => {
    setSelected(option);

    setTimeout(() => {
      onAnswer(option);
    }, 350);
  };

  return (
    <motion.div
      key={question}
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -40 }}
      transition={{ duration: 0.45 }}
      className="w-full max-w-5xl"
    >
      <div className="mb-14 text-center">

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-2 text-xs uppercase tracking-[0.3em] text-cyan-400"        >
          VoyageAI is learning your travel personality
        </motion.p>

        <h1 className="text-3xl font-bold leading-tight md:text-5xl">
          {question}
        </h1>

      </div>

      <div className="grid gap-6 md:grid-cols-2">

        {options.map((option, index) => (
          <motion.button
            key={option}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              delay: index * 0.08,
            }}
            whileHover={{
              y: -8,
              scale: 1.02,
            }}
            whileTap={{
              scale: 0.98,
            }}
            onClick={() => handleClick(option)}
            className={`relative overflow-hidden rounded-3xl border p-7 transition-all duration-300

            ${
              selected === option
                ? "border-cyan-400 bg-cyan-500/15 shadow-[0_0_40px_rgba(34,211,238,.45)]"
                : "border-white/10 bg-white/5 hover:border-cyan-400/60 hover:bg-white/10"
            }`}
          >
            <div className="flex items-center gap-5">

              <div className="rounded-2xl bg-cyan-500/10 p-4 text-cyan-300">
                {getIcon(option)}
              </div>

              <div className="text-left">

                <h3 className="text-2xl font-semibold">
                  {option}
                </h3>

                <p className="mt-2 text-sm text-zinc-400">
                  Choose this option if it best matches your travel style.
                </p>

              </div>

            </div>

            {selected === option && (
              <motion.div
                layoutId="selected"
                className="absolute inset-0 rounded-3xl border-2 border-cyan-400"
              />
            )}
          </motion.button>
        ))}

      </div>
    </motion.div>
  );
}