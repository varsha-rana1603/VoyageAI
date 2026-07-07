"use client";

import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation } from "swiper/modules";
import { ChevronLeft, ChevronRight } from "lucide-react";

import "swiper/css";
import "swiper/css/navigation";

import RecommendationCard from "./RecommendationCard";

interface Props {
  destinations: any[];
  onSelect: (destination: any) => void;
}

export default function RecommendationCarousel({ destinations, onSelect }: Props) {
  return (
    <div className="relative px-2 py-0">
      <Swiper
        modules={[Navigation]}
        navigation={{
          prevEl: ".voyage-prev",
          nextEl: ".voyage-next",
        }}
        grabCursor
        spaceBetween={30}
        className="!overflow-hidden"
        breakpoints={{
          320: {
            slidesPerView: 1.2,
          },
          768: {
            slidesPerView: 2,
          },
          1280: {
            slidesPerView: 3,
          },
        }}
      >
        {destinations.map((destination) => (
          <SwiperSlide key={destination.name} className="!overflow-visible">
            <RecommendationCard destination={destination} onSelect={onSelect} />
          </SwiperSlide>
        ))}
      </Swiper>

      <button className="voyage-prev absolute left-0 top-1/2 z-20 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/10 bg-white/10 p-4 backdrop-blur-xl transition hover:scale-110 hover:bg-cyan-500/20">
        <ChevronLeft className="text-white" />
      </button>

      <button className="voyage-next absolute right-0 top-1/2 z-20 translate-x-1/2 -translate-y-1/2 rounded-full border border-white/10 bg-white/10 p-4 backdrop-blur-xl transition hover:scale-110 hover:bg-cyan-500/20">
        <ChevronRight className="text-white" />
      </button>
    </div>
  );
}