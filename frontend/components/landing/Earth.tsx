"use client";

import { useRef } from "react";
import { useFrame, useLoader, type ThreeEvent } from "@react-three/fiber";
import * as THREE from "three";

export default function Earth({
  position = [0, 0, 0] as [number, number, number],
  onHoverMove,
  onHoverEnd,
}: {
  position?: [number, number, number];
  onHoverMove?: (x: number, y: number) => void;
  onHoverEnd?: () => void;
}) {
  const mesh = useRef<THREE.Mesh>(null!);

  const color = useLoader(THREE.TextureLoader, "/textures/earth.jpg");
  const normal = useLoader(THREE.TextureLoader, "/textures/earthNormal.jpg");

  const handlePointerMove = (e: ThreeEvent<PointerEvent>) => {
    e.stopPropagation();
    // e.uv is the hit point in the mesh's own 0-1 texture space —
    // independent of camera position or the group's world offset
    if (e.uv) onHoverMove?.(e.uv.x * 2 - 1, e.uv.y * 2 - 1);
  };

  return (
    <mesh
      ref={mesh}
      position={position}
      onPointerMove={handlePointerMove}
      onPointerOut={() => onHoverEnd?.()}
    >
      <sphereGeometry args={[2, 128, 128]} />
      <meshStandardMaterial map={color} normalMap={normal} />
    </mesh>
  );
}