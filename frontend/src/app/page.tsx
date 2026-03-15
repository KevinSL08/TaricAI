import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { Problem } from "@/components/landing/Problem";
import { Solution } from "@/components/landing/Solution";
import { Features } from "@/components/landing/Features";
import { ClassifierDemo } from "@/components/landing/ClassifierDemo";
import { Pricing } from "@/components/landing/Pricing";
import { Team } from "@/components/landing/Team";
import { Footer } from "@/components/landing/Footer";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Problem />
        <Solution />
        <Features />
        <ClassifierDemo />
        <Pricing />
        <Team />
      </main>
      <Footer />
    </>
  );
}
