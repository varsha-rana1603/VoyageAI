"use client";

import { useState } from "react";
import HeroRecommendation from "./HeroRecommendation";
import RecommendationCarousel from "./RecommendationCarousel";
import DestinationModal from "./DestinationModal";

interface ResultsPageProps {
  recommendations: any[];
  error: string | null;
  answers: Record<string,string>;
}

export default function ResultsPage({ recommendations, error,answers }: ResultsPageProps) {
  const [selectedDestination, setSelectedDestination] = useState<any>(null);

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#05060b] px-6">
        <div className="max-w-xl text-center">
          <h2 className="mb-4 text-2xl font-bold text-red-400">
            Failed to load recommendations
          </h2>
          <p className="mb-6 text-gray-300">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="rounded-lg bg-white px-4 py-2 text-black"
          >
            Retry
          </button>
        </div>
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
          onSelect={() => setSelectedDestination(recommendations[0])}
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
          onClose={() => setSelectedDestination(null)}
        />
      )}
    </main>
  );
}