"use client";

import { motion } from "framer-motion";

interface Props {
  title: string;
  score: number;
}

export default function ScoreBar({ title, score }: Props) {
  return (
    <div>

      <div className="mb-2 flex justify-between">

        <span>{title}</span>

        <span>{score}%</span>

      </div>

      <div className="h-3 rounded-full bg-zinc-800">

        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1 }}
          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500"
        />

      </div>

    </div>
  );
}