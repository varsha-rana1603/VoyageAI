"use client";

import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

interface Props {
  score: number;
}

export default function MatchCircle({ score }: Props) {
  function label(score: number) {
    if (score >= 90) return "Excellent";
    if (score >= 80) return "Great";
    if (score >= 70) return "Good";
    return "Fair";
  }

  return (
    <div className="w-36">

      <CircularProgressbar
        value={score}
        text={`${Math.round(score)}%`}
        styles={buildStyles({
          pathColor: "#22d3ee",
          textColor: "white",
          trailColor: "#27272a",
        })}
      />

      <p className="mt-4 text-center text-cyan-400 font-semibold">
        {label(score)}
      </p>

    </div>
  );
}