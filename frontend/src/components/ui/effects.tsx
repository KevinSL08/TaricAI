"use client";

import { motion } from "motion/react";
import { useEffect, useState } from "react";

export function FloatingParticles() {
  const [particles] = useState(() =>
    Array.from({ length: 15 }, (_, i) => ({
      id: i,
      x1: Math.random() * 100,
      y1: Math.random() * 100,
      x2: Math.random() * 100,
      y2: Math.random() * 100,
      opacity: Math.random() * 0.3,
      duration: Math.random() * 20 + 20,
    }))
  );

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          initial={{ x: `${p.x1}%`, y: `${p.y1}%`, opacity: p.opacity }}
          animate={{ y: [`${p.y1}%`, `${p.y2}%`], x: [`${p.x1}%`, `${p.x2}%`] }}
          transition={{ duration: p.duration, repeat: Infinity, ease: "linear" }}
          className="absolute w-1 h-1 bg-cyan rounded-full blur-[1px]"
        />
      ))}
    </div>
  );
}

export function MouseGlow() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div
      className="mouse-glow hidden lg:block"
      style={{ left: mousePos.x, top: mousePos.y }}
    />
  );
}

export function Scanline() {
  return <div className="scanline" />;
}
