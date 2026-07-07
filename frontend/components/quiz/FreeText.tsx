"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, ArrowRight } from "lucide-react";

interface Props {
  answers: Record<string, string>;
  onContinue: (text: string) => void;
}

const suggestions = [
  "Quiet cafés",
  "Photography",
  "Shopping",
  "Good food",
  "Snow",
  "Road trip",
  "Luxury stay",
  "Hidden gems",
  "Local culture",
  "Beautiful sunsets",
];

export default function FreeText({ answers, onContinue }: Props) {
  const [text, setText] = useState("");

  const crowd =
    answers.crowd_tolerance === "avoid"
      ? "prefer peaceful destinations"
      : answers.crowd_tolerance === "love_crowds"
        ? "enjoy lively places"
        : "don't mind some crowds";

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-auto w-full max-w-5xl py-30"    >
      <div className="text-center">
        <div className="mb-4 flex items-center justify-center gap-2 text-cyan-400">
          <Sparkles size={20} />
          <span className="text-sm uppercase tracking-[0.3em]">
            Almost there
          </span>
        </div>

        <h1 className="text-4xl font-bold">
          Tell me about your dream vacation
        </h1>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-6 rounded-3xl border border-cyan-500/20 bg-cyan-500/5 p-6 backdrop-blur-xl"
      >
        <p className="text-base leading-7 text-zinc-300">
          Great! I think I'm starting to understand your travel style.
          <br />
          <br />
          You're looking for a{" "}
          <span className="font-semibold text-cyan-300">
            {answers.travel_style}
          </span>{" "}
          trip, prefer{" "}
          <span className="font-semibold text-cyan-300">
            {answers.terrain}
          </span>{" "}
          destinations, have a{" "}
          <span className="font-semibold text-cyan-300">
            {answers.budget}
          </span>{" "}
          budget and {crowd}.
          <br />
          <br />
          <span className="font-medium text-white">
            Now tell me something checkboxes can't.
          </span>
          <br />
          What would make this trip unforgettable?
        </p>
      </motion.div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="I'd love somewhere with cozy cafés, amazing food, quiet sunsets, local markets, beautiful mountain views and easy hikes..."
        className="mt-6 h-40 w-full rounded-3xl border border-white/10 bg-white/5 p-5 text-base outline-none backdrop-blur-xl transition-all focus:border-cyan-400 focus:ring-2 focus:ring-cyan-400/30"
      />

      <div className="mt-5 flex flex-wrap justify-center gap-2">
        {suggestions.map((item) => (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.96 }}
            key={item}
            onClick={() =>
              setText((prev) => (prev ? `${prev}, ${item}` : item))
            }
            className="rounded-full border border-cyan-500/20 bg-cyan-500/5 px-3 py-1.5 text-sm text-cyan-300 transition hover:bg-cyan-500/10"
          >
            {item}
          </motion.button>
        ))}
      </div>

      <div className="mt-6 flex justify-center">
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onContinue(text)}
          className="flex items-center gap-3 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 px-7 py-3 text-base font-semibold shadow-[0_0_35px_rgba(34,211,238,0.25)]"
        >
          Find My Destination
          <ArrowRight size={18} />
        </motion.button>
      </div>
    </motion.div>
  );
}