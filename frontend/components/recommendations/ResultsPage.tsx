"use client";

import { useEffect, useState } from "react";

import HeroRecommendation from "./HeroRecommendation";
import RecommendationCarousel from "./RecommendationCarousel";
import DestinationModal from "./DestinationModal";

import ThinkingScreen, {
  stayPipeline,
} from "../thinking/ThinkingScreen";

import StayResultsPage from "../stays/StaysResultsPage";

interface ResultsPageProps {
  recommendations: any[];
  error: string | null;
  answers: Record<string, string>;
}

type Stage =
  | "destinations"
  | "stayThinking"
  | "stays";

export default function ResultsPage({
  recommendations,
  error,
  answers,
}: ResultsPageProps) {

  const [stage, setStage] =
    useState<Stage>("destinations");

  const [selectedDestination, setSelectedDestination] =
    useState<any>(null);

  const [stayRecommendations, setStayRecommendations] =
    useState<any[]>([]);

  const [stayError, setStayError] =
    useState<string | null>(null);

  const [animationDone, setAnimationDone] =
    useState(false);

  const [fetchDone, setFetchDone] =
    useState(false);
  const [currentStage, setCurrentStage] =
    useState("searching");

  const [progress, setProgress] =
    useState(0);

  useEffect(() => {
    if (stage !== "stayThinking" || !selectedDestination) return;

    console.log("Starting stay recommendation fetch");

    console.log(
      "Thinking state:",
      currentStage,
      progress,
      animationDone,
      fetchDone
    );

    const requestBody = {
      destination_name: selectedDestination.name,
      travel_style: answers.travel_style,
      budget: answers.budget,
      crowd_tolerance: answers.crowd_tolerance,
      terrain: answers.terrain,
      free_text: answers.free_text ?? "",
    };

    console.log("Stay request body:", requestBody);

    let cancelled = false;

    async function fetchStays() {

      const stages = [
        {
          stage: "searching",
          progress: 10,
        },
        {
          stage: "enriching",
          progress: 30,
        },
        {
          stage: "embedding",
          progress: 50,
        },
        {
          stage: "matching",
          progress: 70,
        },
        {
          stage: "finalizing",
          progress: 90,
        },
      ];


      let stageIndex = 0;


      const timer = setInterval(() => {

        if (stageIndex < stages.length) {

          console.log(
            "Updating thinking stage:",
            stages[stageIndex]
          );


          setCurrentStage(
            stages[stageIndex].stage
          );


          setProgress(
            stages[stageIndex].progress
          );


          stageIndex++;

        }

      }, 1000);



      try {

        const res = await fetch(
          "http://127.0.0.1:8001/recommend-stays",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(requestBody),
          }
        );


        const data = await res.json();


        console.log(
          "Stay response:",
          data
        );


        setStayRecommendations(
          data.recommendations ?? data
        );


      }
      catch (err: any) {

        setStayError(err.message);

      }
      finally {


        clearInterval(timer);


        setCurrentStage("complete");

        setProgress(100);


        setFetchDone(true);

      }

    }
    fetchStays();

    return () => {
      cancelled = true;
    };
  }, [stage, selectedDestination?.name, answers]);

  useEffect(() => {

    if (
      stage === "stayThinking" &&
      animationDone &&
      fetchDone
    ) {

      setStage("stays");

    }

  }, [
    stage,
    animationDone,
    fetchDone,
  ]);

  if (stage === "stayThinking") {

    return (
      <ThinkingScreen

        title="VoyageAI is planning your trip"

        subtitle="
        Running semantic search and hybrid ranking...
        "

        pipeline={stayPipeline}

        currentStage={currentStage}

        progress={progress}

        onFinished={() => {
          setAnimationDone(true);
        }}

      />
    );

  }

  if (stage === "stays") {
    return (
      <StayResultsPage
        recommendations={stayRecommendations}
        destination={selectedDestination}
        error={stayError}
        onBack={() => setStage("destinations")}
      />
    );
  }

  if (error) {

    return (
      <main className="flex min-h-screen items-center justify-center bg-[#05060b] text-white">
        {error}
      </main>
    );

  }

  if (!recommendations.length) {

    return (
      <main className="flex min-h-screen items-center justify-center bg-[#05060b] text-white">
        No recommendations found
      </main>
    );

  }

  return (

    <main className="min-h-screen bg-[#05060b] px-6 py-10">

      <div className="mx-auto max-w-7xl">

        <HeroRecommendation
          destination={recommendations[0]}
          onExploreStays={(destination) => {

            setSelectedDestination(destination);

            setAnimationDone(false);

            setFetchDone(false);

            setStayError(null);

            setStayRecommendations([]);

            setCurrentStage("searching");

            setProgress(0);

            setStage("stayThinking");

          }}
        />

        <section className="mt-10">

          <h2 className="mb-10 text-4xl font-bold text-white">
            Other Great Matches
          </h2>

          <RecommendationCarousel
            destinations={recommendations.slice(1)}
            onSelect={setSelectedDestination}
          />

        </section>

      </div>

      {selectedDestination && (
        <DestinationModal
          destination={selectedDestination}
          answers={answers}
          onClose={() =>
            setSelectedDestination(null)
          }
          onStartPlanning={(destination) => {

            setSelectedDestination(destination);

            setAnimationDone(false);

            setFetchDone(false);

            setStayError(null);

            setStayRecommendations([]);

            setCurrentStage("searching");

            setProgress(0);

            setStage("stayThinking");

          }}
        />
      )}

    </main>

  );

}