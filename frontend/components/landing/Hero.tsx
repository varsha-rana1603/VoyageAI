"use client";

import Aurora from "./Aurora";
import FloatingParticles from "./FloatingParticles";
import AnimatedGlobe from "./AnimatedGlobe";
import CTAButton from "./CTAButton";
import { motion, useReducedMotion, type Variants } from "framer-motion";

const container: Variants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.15, delayChildren: 0.2 },
  },
};

const item: Variants = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: "easeOut" },
  },
};

export default function Hero() {
  const reduceMotion = useReducedMotion();

  return (
    <section className="relative flex min-h-screen items-center overflow-hidden">
      <div className="absolute inset-0 z-0 pointer-events-none">
        <Aurora />
      </div>
      <div className="absolute inset-0 z-10 pointer-events-none">
        <AnimatedGlobe />
      </div>
      <div className="absolute inset-0 z-20 pointer-events-none">
        <FloatingParticles />
      </div>

      <div className="relative z-30 mx-auto grid w-full max-w-7xl grid-cols-1 gap-12 px-6 py-24 md:grid-cols-2 md:items-center">
        <motion.div
          variants={reduceMotion ? undefined : container}
          initial={reduceMotion ? undefined : "hidden"}
          animate={reduceMotion ? undefined : "show"}
          className="flex select-none flex-col items-center text-center md:items-start md:text-left"
        >
          <motion.h1
            variants={reduceMotion ? undefined : item}
            className="text-4xl font-black leading-[1.1] sm:text-6xl md:text-7xl"
          >
            Where will
            <span className="block bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text pb-2 text-transparent">
              curiosity take you?
            </span>
          </motion.h1>

          <motion.p
            variants={reduceMotion ? undefined : item}
            className="mt-8 max-w-md text-lg text-zinc-400"
          >
            VoyageAI understands how you love to travel and recommends
            destinations you never knew existed.
          </motion.p>

          <motion.div variants={reduceMotion ? undefined : item} className="mt-8">
            <CTAButton />
          </motion.div>
        </motion.div>

        {/* Spacer only reserves grid width — must not intercept pointer events over the globe beneath it */}
        <div className="hidden pointer-events-none md:block" aria-hidden="true" />
      </div>
    </section>
  );
}