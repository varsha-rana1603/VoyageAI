"use client";

import MatchCircle from "./MatchCircle";
import ScoreBar from "./ScoreBar";
import { CheckCircle2, Hotel } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
  destination: any;
  onExploreStays: (destination: any) => void;
}

export default function HeroRecommendation({
  destination,
  onExploreStays,
}: Props) {
  return (
    <motion.section
      initial={{
        opacity: 0,
        y: 60,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="rounded-3xl border border-white/10 bg-white/5 p-6 md:p-8 lg:p-10 backdrop-blur-xl"
    >
      <div className="grid items-start gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        {/* LEFT */}
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.35em] text-cyan-400 md:text-sm">
            Your Perfect Match
          </p>

          <h1 className="text-4xl font-bold leading-tight md:text-5xl lg:text-6xl">
            {destination.name}
          </h1>

          <p className="mt-2 text-base text-zinc-400 md:text-lg">
            {destination.state}
          </p>

          <p className="mt-6 text-base leading-7 text-zinc-300 md:text-lg">
            {destination.description}
          </p>

          <div className="mt-8 space-y-3">
            {destination.reasons.map((reason: string) => (
              <div
                key={reason}
                className="flex items-start gap-3"
              >
                <CheckCircle2
                  size={20}
                  className="mt-0.5 shrink-0 text-cyan-400"
                />

                <span className="text-sm leading-6 text-zinc-200 md:text-base">
                  {reason}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT */}
        <div className="flex flex-col items-center">
          <MatchCircle score={destination.final_score} />

          <div className="mt-8 w-full space-y-4">
            <ScoreBar
              title="Semantic Match"
              score={destination.semantic_score}
            />

            <ScoreBar
              title="Budget Match"
              score={destination.budget_score}
            />

            <ScoreBar
              title="Terrain Match"
              score={destination.terrain_score}
            />

            <ScoreBar
              title="Crowd Match"
              score={destination.crowd_score}
            />
          </div>

          <motion.button
            whileHover={{
              scale: 1.03,
            }}
            whileTap={{
              scale: 0.98,
            }}
            onClick={() => onExploreStays(destination)}
            className="
              mt-8
              flex
              w-full
              items-center
              justify-center
              gap-3
              rounded-2xl
              bg-gradient-to-r
              from-cyan-400
              to-blue-500
              px-6
              py-4
              text-base
              font-semibold
              text-black
              shadow-[0_0_30px_rgba(34,211,238,0.25)]
              transition
            "
          >
            <Hotel size={20} />

            Explore Recommended Stays
          </motion.button>
        </div>
      </div>
    </motion.section>
  );
}