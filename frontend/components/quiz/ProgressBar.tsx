"use client";

import { motion } from "framer-motion";

interface Props {
  current: number;
  total: number;
}

export default function ProgressBar({ current, total }: Props) {

  const progress = (current / total) * 100;

  return (

    <div className="w-full max-w-xl">

      <div className="mb-3 flex justify-between text-sm text-zinc-400">

        <span>
          Question {current + 1}
        </span>

        <span>
          {Math.round(progress)}%
        </span>

      </div>

      <div className="h-2 rounded-full bg-zinc-800">

        <motion.div

          animate={{
            width: `${progress}%`
          }}

          transition={{
            duration: .5
          }}

          className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500"

        />

      </div>

    </div>

  );

}