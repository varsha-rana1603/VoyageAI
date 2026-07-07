"use client";

import { useMemo, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { ArrowLeft, MapPin, Building2 } from "lucide-react";

interface StaysResultsPageProps {
  recommendations: any[];
  destination: any;
  error: string | null;
  onBack: () => void;
}

type SortKey = "match" | "price" | "distance";

function parseMatchPercentage(value: unknown): number {
  if (typeof value === "number") return value;

  if (typeof value === "string") {
    // Excellent Match
    if (value.includes("95")) return 95;

    // 85–95%
    if (value.includes("85")) return 90;

    // 75–85%
    if (value.includes("79")) return 80;

    // <75%
    if (value.includes("<75")) return 70;

    const num = parseFloat(value.replace(/[^\d.]/g, ""));
    return Number.isNaN(num) ? 0 : num;
  }

  return 0;
}

function priceTier(priceLevel: string | number | undefined): number {
  if (typeof priceLevel === "number") return Math.min(4, Math.max(1, priceLevel));
  if (typeof priceLevel === "string") {
    const count = (priceLevel.match(/₹/g) || []).length;
    if (count > 0) return Math.min(4, count);
  }
  return 1;
}

function MatchRing({ score }: { score: number }) {
  const radius = 22;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex h-14 w-14 flex-shrink-0 items-center justify-center">
      <svg width="56" height="56" viewBox="0 0 56 56" className="-rotate-90">
        <circle cx="28" cy="28" r={radius} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="5" />
        <motion.circle
          cx="28"
          cy="28"
          r={radius}
          fill="none"
          stroke="url(#stayScoreGradient)"
          strokeWidth="5"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
        />
        <defs>
          <linearGradient id="stayScoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#22d3ee" />
            <stop offset="100%" stopColor="#a855f7" />
          </linearGradient>
        </defs>
      </svg>
      <span className="absolute text-[11px] font-bold text-white">{Math.round(score)}%</span>
    </div>
  );
}

function PriceTier({ level }: { level: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4].map((tier) => (
        <span
          key={tier}
          className={`text-sm font-semibold ${
            tier <= level ? "text-cyan-400" : "text-white/15"
          }`}
        >
          ₹
        </span>
      ))}
    </div>
  );
}

const SORT_OPTIONS: { key: SortKey; label: string }[] = [
  { key: "match", label: "Best Match" },
  { key: "price", label: "Price" },
  { key: "distance", label: "Distance" },
];

export default function StaysResultsPage({
  recommendations,
  destination,
  error,
  onBack,
}: StaysResultsPageProps) {
  const [sortKey, setSortKey] = useState<SortKey>("match");
  const reduceMotion = useReducedMotion();

  const sortedStays = useMemo(() => {
    const copy = [...recommendations];

    copy.sort((a, b) => {
      if (sortKey === "match") {
        return parseMatchPercentage(b.match_percentage) - parseMatchPercentage(a.match_percentage);
      }
      if (sortKey === "price") {
        return priceTier(a.price_level) - priceTier(b.price_level);
      }
      // distance
      return (a.distance_from_center ?? 0) - (b.distance_from_center ?? 0);
    });

    return copy;
  }, [recommendations, sortKey]);

  return (
    <main className="min-h-screen bg-[#05060b] px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl">
        <button
          onClick={onBack}
          className="mb-8 flex items-center gap-2 text-sm text-zinc-400 transition hover:text-cyan-400"
        >
          <ArrowLeft size={16} />
          Back to destinations
        </button>

        <motion.div
          initial={reduceMotion ? undefined : { opacity: 0, y: 20 }}
          animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col justify-between gap-6 border-b border-white/10 pb-8 sm:flex-row sm:items-end"
        >
          <div>
            <div className="flex items-center gap-2 text-cyan-400">
              <Building2 size={16} />
              <span className="text-sm uppercase tracking-[0.2em]">Stays</span>
            </div>
            <h1 className="mt-2 text-4xl font-bold sm:text-5xl">
              Where to stay in {destination?.name}
            </h1>
            <p className="mt-3 text-zinc-400">
              {sortedStays.length} stay{sortedStays.length !== 1 ? "s" : ""} matched to your trip
            </p>
          </div>

          {/* Sort chips */}
          <div className="flex flex-shrink-0 gap-2">
            {SORT_OPTIONS.map((option) => (
              <button
                key={option.key}
                onClick={() => setSortKey(option.key)}
                className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                  sortKey === option.key
                    ? "border-cyan-400/40 bg-cyan-500/15 text-cyan-300"
                    : "border-white/10 bg-white/5 text-zinc-400 hover:border-white/20 hover:text-white"
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </motion.div>

        {error && (
          <div className="mt-10 rounded-2xl border border-red-500/20 bg-red-500/10 p-6 text-red-300">
            {error}
          </div>
        )}

        {!error && sortedStays.length === 0 && (
          <div className="mt-10 rounded-2xl border border-white/10 bg-white/5 p-10 text-center text-zinc-400">
            <p className="text-lg text-white">No stays found yet</p>
            <p className="mt-2 text-sm">
              Try a different destination, or check back once more stays are added.
            </p>
          </div>
        )}

        {!error && sortedStays.length > 0 && (
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <AnimatePresence mode="popLayout">
              {sortedStays.map((stay, i) => (
                <motion.div
                  key={stay.id}
                  layout
                  initial={reduceMotion ? undefined : { opacity: 0, y: 24 }}
                  animate={reduceMotion ? undefined : { opacity: 1, y: 0 }}
                  exit={reduceMotion ? undefined : { opacity: 0, y: -12 }}
                  transition={{ duration: 0.4, delay: reduceMotion ? 0 : i * 0.05 }}
                  whileHover={{ y: -6 }}
                  className="flex flex-col rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl transition-colors hover:border-cyan-500/30"
                >
                  <div className="flex items-start justify-between gap-3">
                    <h2 className="text-lg font-semibold leading-snug">{stay.name}</h2>
                    <MatchRing score={parseMatchPercentage(stay.match_percentage)} />
                  </div>

                  <div className="mt-3 flex items-start gap-2 text-sm text-zinc-400">
                    <MapPin size={14} className="mt-0.5 flex-shrink-0" />
                    <span className="line-clamp-2">{stay.address}</span>
                  </div>

                  <div className="mt-auto flex items-center justify-between border-t border-white/10 pt-4 text-sm">
                    <PriceTier level={priceTier(stay.price_level)} />

                    <span className="text-zinc-400">
                      {stay.distance_from_center} km away
                    </span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </main>
  );
}