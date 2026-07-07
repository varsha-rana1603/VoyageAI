"use client";

import MatchCircle from "./MatchCircle";
import ScoreBar from "./ScoreBar";
import { CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";

interface Props {
  destination: any;
  onSelect: (destination: any) => void;
}

export default function HeroRecommendation({
  destination,
  onSelect
}: Props) {
  return (
    <motion.section
      initial={{
        opacity: 0,
        y: 80,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="rounded-[40px] border border-white/10 bg-white/5 p-10 backdrop-blur-xl"
    >
      <div className="grid gap-10 lg:grid-cols-2">

        <div>

          <p className="mb-3 text-cyan-400 uppercase tracking-[0.3em]">
            Your Perfect Match
          </p>

          <h1 className="text-6xl font-bold">
            {destination.name}
          </h1>

          <p className="mt-2 text-zinc-400">
            {destination.state}
          </p>

          <p className="mt-8 text-lg text-zinc-300 leading-8">
            {destination.description}
          </p>

          <div className="mt-10 space-y-4">

            {destination.reasons.map((reason: string) => (
              <div
                key={reason}
                className="flex items-center gap-3"
              >
                <CheckCircle2 className="text-cyan-400" />

                <span>{reason}</span>

              </div>
            ))}

          </div>

        </div>

        <div className="flex flex-col items-center">

          <MatchCircle score={destination.final_score} />

          <div className="mt-12 w-full space-y-6">

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

        </div>

      </div>
    </motion.section>
  );
}