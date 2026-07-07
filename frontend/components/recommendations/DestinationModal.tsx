"use client";

import { AnimatePresence, motion } from "framer-motion";
import {
  X,
  Sparkles,
  Mountain,
  Wallet,
  Users,
  CheckCircle2,
  AlertCircle,
  XCircle,
} from "lucide-react";

interface Props {
  destination: any;
  answers: Record<string, string>;
  onClose: () => void;
}

function getMatchLabel(score: number): string {
  if (score >= 90) return "Excellent Match";
  if (score >= 75) return "Great Match";
  if (score >= 60) return "Good Match";
  if (score >= 55) return "Fair Match";
  return "Weak Match";
}

function formatTerrain(regionType?: string): string {
    console.log("RESION TYPE IS: ", regionType)
  if (!regionType) return "Not specified";
  return regionType.charAt(0).toUpperCase() + regionType.slice(1);
}

function formatBudget(budgetLevel?: string): string {
  const map: Record<string, string> = {
    low: "Budget-Friendly",
    medium: "Medium Budget",
    high: "High Budget",
    luxury: "Luxury",
  };
  return budgetLevel ? map[budgetLevel] ?? budgetLevel : "Not specified";
}

function formatCrowd(crowdLevel?: string): string {
  const map: Record<string, string> = {
    low: "Low Crowds",
    medium: "Moderate Crowds",
    high: "High Crowds",
  };
  return crowdLevel ? map[crowdLevel] ?? crowdLevel : "Not specified";
}

// --- Preference comparison logic ---
// Mirrors the ordering used in the backend's budget_match/crowd_match,
// so "close" vs "far" here matches how the destination was actually scored.

type Comparison = { status: "match" | "partial" | "mismatch"; text: string };

const BUDGET_ORDER: Record<string, number> = { low: 1, medium: 2, high: 3, luxury: 4 };
const CROWD_ORDER: Record<string, number> = { low: 1, medium: 2, high: 3 };

function compareBudget(userBudget?: string, destBudget?: string): Comparison | null {
  if (!userBudget || !destBudget || !(userBudget in BUDGET_ORDER) || !(destBudget in BUDGET_ORDER)) {
    return null;
  }
  const diff = BUDGET_ORDER[destBudget] - BUDGET_ORDER[userBudget];
  if (diff === 0) return { status: "match", text: "Matches your budget" };
  const direction = diff > 0 ? "pricier" : "cheaper";
  if (Math.abs(diff) === 1) {
    return { status: "partial", text: `Slightly ${direction} than your budget` };
  }
  return { status: "mismatch", text: `Notably ${direction} than your budget` };
}

function compareCrowd(userCrowd?: string, destCrowd?: string): Comparison | null {
  if (!userCrowd || !destCrowd || !(userCrowd in CROWD_ORDER) || !(destCrowd in CROWD_ORDER)) {
    return null;
  }
  const diff = CROWD_ORDER[destCrowd] - CROWD_ORDER[userCrowd];
  if (diff === 0) return { status: "match", text: "Matches your crowd preference" };
  const direction = diff > 0 ? "more crowded" : "quieter";
  if (Math.abs(diff) === 1) {
    return { status: "partial", text: `Slightly ${direction} than you'd prefer` };
  }
  return { status: "mismatch", text: `Much ${direction} than you'd prefer` };
}

function compareTerrain(userTerrain?: string, destTerrain?: string): Comparison | null {
  if (!userTerrain || !destTerrain) return null;
  const u = userTerrain.toLowerCase().replace(/s$/, "");
  const d = destTerrain.toLowerCase().replace(/s$/, "");
  console.log("U IS:", u, "AND D IS:", d);
  if (u === d) {
    return { status: "match", text: `Matches your preferred ${formatTerrain(d)} terrain` };
  }
  return { status: "mismatch", text: `${formatTerrain(destTerrain)} terrain, not what you asked for` };
}

function ComparisonRow({ comparison }: { comparison: Comparison }) {
  const iconMap = {
    match: <CheckCircle2 className="flex-shrink-0 text-green-400" size={16} />,
    partial: <AlertCircle className="flex-shrink-0 text-amber-400" size={16} />,
    mismatch: <XCircle className="flex-shrink-0 text-red-400" size={16} />,
  };

  return (
    <div className="flex items-center gap-2.5 text-sm">
      {iconMap[comparison.status]}
      {comparison.text}
    </div>
  );
}

export default function DestinationModal({ destination, answers, onClose }: Props) {
  if (!destination) return null;

  const matchLabel = getMatchLabel(destination.final_score ?? 0);
  const highlights: string[] = destination.pros ?? [];

  const scores = [
    { label: "Semantic", value: destination.semantic_score },
    { label: "Budget", value: destination.budget_score },
    { label: "Terrain", value: destination.terrain_score },
    { label: "Crowds", value: destination.crowd_score },
  ];

  const comparisons = [
    compareBudget(answers.budget, destination.budget_level),
    compareCrowd(answers.crowd_tolerance, destination.crowd_level),
    compareTerrain(answers.terrain, destination.region_type),
  ].filter((c): c is Comparison => c !== null);

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-6 backdrop-blur-xl"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.92, y: 40 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.92 }}
          transition={{ type: "spring", stiffness: 120, damping: 18 }}
          onClick={(e) => e.stopPropagation()}
          className="relative flex max-h-[80vh] w-full max-w-5xl flex-col overflow-hidden rounded-[28px] border border-white/10 bg-[#0A0D14] shadow-[0_40px_120px_rgba(0,0,0,.45)]"
        >
          <button
            onClick={onClose}
            className="absolute right-6 top-6 z-10 rounded-full bg-white/5 p-2.5 transition hover:bg-white/10"
          >
            <X size={20} />
          </button>

          <div className="overflow-y-auto p-8">
            {/* Header */}
            <div className="flex items-start justify-between gap-6">
              <div className="min-w-0 flex-1">
                <p className="text-cyan-400">{destination.state}</p>
                <h1 className="mt-1 truncate text-3xl font-bold">{destination.name}</h1>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-400">
                  {destination.summary ?? destination.description}
                </p>
              </div>

              <div className="flex flex-shrink-0 flex-col items-center">
                <div className="flex h-30 w-30 items-center justify-center rounded-full border-[6px] border-cyan-400 bg-cyan-500/10 shadow-[0_0_40px_rgba(34,211,238,.25)]">
                  <div className="text-center">
                    <h2 className="text-2xl font-bold">{destination.final_score}%</h2>
                  </div>
                </div>
                <p className="mt-1.5 text-xs text-cyan-300">{matchLabel}</p>
              </div>
            </div>

            <div className="my-6 h-px bg-white/10" />

            <div className="grid grid-cols-2 gap-8">
              {/* LEFT */}
              <div>
                <h2 className="mb-3 text-lg font-semibold">Why VoyageAI recommends this</h2>

                <div className="space-y-2.5">
                  {destination.reasons.map((reason: string) => (
                    <motion.div
                      key={reason}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="flex items-center gap-3 rounded-xl bg-white/5 p-3"
                    >
                      <Sparkles className="flex-shrink-0 text-cyan-400" size={16} />
                      <p className="text-sm">{reason}</p>
                    </motion.div>
                  ))}
                </div>

                {/* NEW: how this compares to what the user actually asked for */}
                {comparisons.length > 0 && (
                  <div className="mt-6">
                    <h2 className="mb-3 text-lg font-semibold">How This Compares</h2>
                    <div className="space-y-2.5 rounded-2xl bg-white/5 p-4">
                      {comparisons.map((c) => (
                        <ComparisonRow key={c.text} comparison={c} />
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-6">
                   {highlights.length > 0 && (
                  <div className="mt-6 rounded-2xl border border-green-500/20 bg-green-500/10 p-5">
                    <h3 className="mb-3 text-base font-semibold">Highlights</h3>
                    <div className="space-y-2.5">
                      {highlights.map((highlight) => (
                        <div key={highlight} className="flex items-center gap-2.5 text-sm">
                          <CheckCircle2 className="flex-shrink-0 text-green-400" size={16} />
                          {highlight}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                </div>
              </div>

              {/* RIGHT */}
              <div>
                <h2 className="mb-4 text-lg font-semibold">Match Breakdown</h2>
                <div className="space-y-4">
                  {scores.map((score) => (
                    <div key={score.label}>
                      <div className="mb-1.5 flex justify-between text-sm">
                        <span>{score.label}</span>
                        <span>{score.value}%</span>
                      </div>
                      <div className="h-2 rounded-full bg-white/10">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${score.value}%` }}
                          transition={{ duration: 1 }}
                          className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"
                        />
                      </div>
                    </div>
                  ))}
                </div>

                {/* {highlights.length > 0 && (
                  <div className="mt-6 rounded-2xl border border-green-500/20 bg-green-500/10 p-5">
                    <h3 className="mb-3 text-base font-semibold">Highlights</h3>
                    <div className="space-y-2.5">
                      {highlights.map((highlight) => (
                        <div key={highlight} className="flex items-center gap-2.5 text-sm">
                          <CheckCircle2 className="flex-shrink-0 text-green-400" size={16} />
                          {highlight}
                        </div>
                      ))}
                    </div>
                  </div>
                )} */}

                <motion.button
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.98 }}
                  className="mt-6 w-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 py-3 text-base font-semibold"
                >
                  Start Planning →
                </motion.button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}