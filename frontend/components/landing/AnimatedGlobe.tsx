"use client";

import { useEffect, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { motion } from "framer-motion";
import * as THREE from "three";

import Earth from "./Earth";
import StarField from "./Stars";

function RotatingGroup({
  earthX,
  hoverRef,
}: {
  earthX: number;
  hoverRef: React.MutableRefObject<{ x: number; y: number; active: boolean }>;
}) {
  const group = useRef<THREE.Group>(null!);
  const autoSpin = useRef(0);

  useFrame(() => {
    if (hoverRef.current.active) {
      // Free rotation driven by cursor position on the sphere —
      // wider multipliers than before so it feels like real manual rotation
      const targetX = hoverRef.current.y * 0.9;
      const targetY = autoSpin.current + hoverRef.current.x * 1.4;

      group.current.rotation.x = THREE.MathUtils.lerp(group.current.rotation.x, targetX, 0.08);
      group.current.rotation.y = THREE.MathUtils.lerp(group.current.rotation.y, targetY, 0.08);
    } else {
      // No hover: keep spinning on its own, ease pitch back to level
      autoSpin.current += 0.0015;
      group.current.rotation.y = THREE.MathUtils.lerp(group.current.rotation.y, autoSpin.current, 0.05);
      group.current.rotation.x = THREE.MathUtils.lerp(group.current.rotation.x, 0, 0.05);
    }
  });

  const handleHoverMove = (x: number, y: number) => {
    hoverRef.current = { x, y, active: true };
  };
  const handleHoverEnd = () => {
    hoverRef.current.active = false;
  };

  return (
    <group ref={group} position={[earthX, -0.3, -0.4]}>
      <Earth onHoverMove={handleHoverMove} onHoverEnd={handleHoverEnd} />
    </group>
  );
}

export default function AnimatedGlobe() {
  const [isDesktop, setIsDesktop] = useState(false);
  const hover = useRef({ x: 0, y: 0, active: false });

  useEffect(() => {
    const mq = window.matchMedia("(min-width: 768px)");
    const update = () => setIsDesktop(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);

  const earthX = isDesktop ? 2.4 : 0;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4, delay: 0.3, ease: "easeOut" }}
      className="pointer-events-auto h-full w-full"
    >
      <Canvas camera={{ position: [0, 0, 6], fov: 50 }}>
        <ambientLight intensity={2} />
        <directionalLight intensity={5} position={[5, 3, 5]} />
        <StarField />
        <RotatingGroup earthX={earthX} hoverRef={hover} />
      </Canvas>
    </motion.div>
  );
}