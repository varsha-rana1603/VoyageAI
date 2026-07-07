"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

interface Particle {
  left: number;
  delay: number;
  duration: number;
}

export default function FloatingParticles() {
  const [particles, setParticles] = useState<Particle[]>([]);

  useEffect(() => {
    const generated = Array.from({ length: 35 }, () => ({
      left: Math.random() * 100,
      delay: Math.random() * 10,
      duration: 12 + Math.random() * 12,
    }));

    setParticles(generated);
  }, []);

  if (particles.length === 0) return null;

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {particles.map((particle, i) => (
        <motion.div
          key={i}
          className="absolute h-1.5 w-1.5 rounded-full bg-cyan-300"
          initial={{
            opacity: 0,
            y: 80,
            left: `${particle.left}%`,
          }}
          animate={{
            opacity: [0, 0.6, 0],
            y: -800,
          }}
          transition={{
            repeat: Infinity,
            duration: particle.duration,
            delay: particle.delay,
            ease: "linear",
          }}
        />
      ))}
    </div>
  );
}