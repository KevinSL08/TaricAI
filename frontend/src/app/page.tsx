"use client";

import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { Features } from "@/components/landing/Features";
import { ClassifierDemo } from "@/components/landing/ClassifierDemo";
import { Pricing } from "@/components/landing/Pricing";
import { Team } from "@/components/landing/Team";
import { Footer } from "@/components/landing/Footer";
import { FloatingParticles, MouseGlow, Scanline } from "@/components/ui/effects";

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-on-surface selection:bg-cyan/30 mesh-bg overflow-hidden">
      <MouseGlow />
      <FloatingParticles />
      <Scanline />
      <Navbar />
      <main className="relative z-10">
        <Hero />
        <Features />
        <ClassifierDemo />
        <Pricing />
        <Team />
      </main>
      <Footer />
    </div>
  );
}
