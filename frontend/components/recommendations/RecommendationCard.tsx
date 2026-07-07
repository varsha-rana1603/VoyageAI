"use client";

import { motion } from "framer-motion";
import { MapPin } from "lucide-react";

interface Props {
  destination: any;
  onSelect: (destination: any) => void;
}

export default function RecommendationCard({ destination, onSelect }: Props) {
  const score = destination.final_score ?? 0;

  // Circle math for the progress ring
  const radius = 46; // reduced from 50 so an 8px stroke has room within the viewBox
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <motion.div
      whileHover={{ y: -6, scale: 1.02 }}
      onClick={() => onSelect(destination)}
      className="flex h-[180px] cursor-pointer items-center justify-between gap-4 rounded-[24px] border border-white/10 bg-white/5 p-5 backdrop-blur-xl transition-colors hover:border-cyan-500/30"
    >
      <div className="min-w-0 flex-1">
        <h2 className="truncate text-xl font-bold leading-tight">{destination.name}</h2>

        <div className="mt-2 flex items-center gap-2 text-sm text-zinc-400">
          <MapPin size={14} />
          {destination.state}
        </div>

        <p className="mt-4 line-clamp-2 text-sm text-zinc-300">{destination.summary}</p>
      </div>

      <div className="relative flex h-[100px] w-[100px] flex-shrink-0 items-center justify-center">
        <svg width="100" height="100" viewBox="0 0 100 100" className="-rotate-90 overflow-visible">
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.08)"
            strokeWidth="8"
          />
          <motion.circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            stroke="url(#scoreGradient)"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: "easeOut", delay: 0.2 }}
          />
          <defs>
            <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#22d3ee" />
              <stop offset="100%" stopColor="#a855f7" />
            </linearGradient>
          </defs>
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-bold text-white">{score}%</span>
          <span className="text-[9px] uppercase tracking-widest text-zinc-400">
            Match
          </span>
        </div>
      </div>
    </motion.div>
  );
}