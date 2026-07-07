"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Brain,
  Sparkles,
  Globe2,
  BarChart3,
  CheckCircle2,
  Loader2,
} from "lucide-react";

const pipeline = [
  {
    icon: Brain,
    title: "Understanding your travel personality...",
    completed: "Completed",
  },
  {
    icon: Sparkles,
    title: "Generating semantic embedding...",
    completed: "Completed",
  },
  {
    icon: Globe2,
    title: "Comparing against 534 destinations...",
    completed: "Top 20 candidates found",
  },
  {
    icon: BarChart3,
    title: "Calculating hybrid ranking...",
    completed: "Scores computed",
  },
  {
    icon: CheckCircle2,
    title: "Generating explainable recommendations...",
    completed: "Ready!",
  },
];

export default function ThinkingScreen({
  onFinished,
}: {
  onFinished: () => void;
}) {
  const [completedSteps, setCompletedSteps] = useState(0);

  useEffect(() => {
    if (completedSteps === pipeline.length) {
      setTimeout(() => {
        onFinished();
      }, 800);

      return;
    }

    const timer = setTimeout(() => {
      setCompletedSteps((prev) => prev + 1);
    }, 1200);

    return () => clearTimeout(timer);
  }, [completedSteps, onFinished]);

  return (
    <section className="flex min-h-screen items-center justify-center bg-[#05060b] px-6">

      <div className="w-full max-w-3xl rounded-3xl border border-white/10 bg-white/5 p-10 backdrop-blur-2xl">

        <h1 className="mb-3 text-center text-4xl font-bold">
          VoyageAI is planning your trip
        </h1>

        <p className="mb-12 text-center text-zinc-400">
          Running semantic search and hybrid ranking...
        </p>

        <div className="space-y-8">

          {pipeline.map((step, index) => {
            const Icon = step.icon;

            const done = index < completedSteps;

            const active = index === completedSteps;

            return (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start gap-5"
              >
                <div className="mt-1">
                  {done ? (
                    <CheckCircle2
                      size={28}
                      className="text-green-400"
                    />
                  ) : active ? (
                    <Loader2
                      size={28}
                      className="animate-spin text-cyan-400"
                    />
                  ) : (
                    <Icon
                      size={28}
                      className="text-zinc-600"
                    />
                  )}
                </div>

                <div className="flex-1">

                  <p
                    className={`text-xl ${
                      done || active
                        ? "text-white"
                        : "text-zinc-500"
                    }`}
                  >
                    {step.title}
                  </p>

                  {done && (
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="mt-2 text-green-400"
                    >
                      ✓ {step.completed}
                    </motion.p>
                  )}

                  {active && (
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: "100%" }}
                      transition={{ duration: 1 }}
                      className="mt-4 h-[3px] rounded-full bg-gradient-to-r from-cyan-400 via-blue-500 to-cyan-400"
                    />
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}