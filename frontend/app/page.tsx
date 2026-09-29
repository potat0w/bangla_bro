import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Hero } from "@/components/home/Hero";
import { AboutSection } from "@/components/home/AboutSection";
import { HowItWorksSection } from "@/components/home/HowItWorksSection";
import { AskIdeasSection } from "@/components/home/AskIdeasSection";
import { BookSection } from "@/components/home/BookSection";
import { ExampleSection } from "@/components/home/ExampleSection";
import { FinalCta } from "@/components/home/FinalCta";

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main>
        <Hero />
        <AboutSection />
        <HowItWorksSection />
        <AskIdeasSection />
        <BookSection />
        <ExampleSection />
        <FinalCta />
      </main>
      <Footer />
    </div>
  );
}
