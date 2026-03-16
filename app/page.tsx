'use client';

import Navbar from "@/components/Navbar";
import TestimonialFlipper from "@/components/TestimonialFlipper";
import { motion } from "framer-motion";
import { ArrowRight, Brain, Code, Rocket, Users, Sparkles } from "lucide-react";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col bg-mesh">
      <Navbar />
      
      <main className="flex-grow">
        {/* Hero Section */}
        <section className="px-6 pt-40 pb-32 max-w-6xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-accent/10 text-accent text-xs font-bold uppercase tracking-widest mb-8">
              <Sparkles className="w-3 h-3" /> AI-Powered Project Architect
            </div>
            <h1 className="text-6xl md:text-8xl font-serif text-primary mb-8 leading-[1.1] tracking-tight">
              Turn Your Curiosity <br /> Into a <span className="italic font-light text-accent">Masterpiece.</span>
            </h1>
            <p className="text-xl md:text-2xl text-primary/60 mb-12 max-w-3xl mx-auto leading-relaxed font-sans">
              We help students bridge the gap between raw interest and technical execution. 
              Get tailored project roadmaps designed for your specific skill level.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
              <Link href="/questions" className="btn-primary inline-flex items-center gap-3 text-lg px-10 py-4">
                Find My Project Idea <ArrowRight className="w-5 h-5" />
              </Link>
              <span className="text-sm text-primary/40 font-medium">Free for students &amp; builders</span>
            </div>
          </motion.div>
        </section>

        {/* How It Works - Editorial Style */}
        <section id="how-it-works" className="py-32 px-6 border-y border-black/5 bg-white/30">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-end mb-20 gap-8">
              <div className="max-w-xl">
                <h2 className="text-4xl md:text-5xl font-serif mb-6">The IdeaSpark Process</h2>
                <p className="text-lg text-primary/60">A structured approach to finding your next big build, moving from vague interest to a concrete tech stack.</p>
              </div>
              <div className="text-8xl font-serif text-black/5 hidden md:block">01—03</div>
            </div>

<div className="grid md:grid-cols-3 gap-12 lg:gap-16 relative">
              {[
                { step: "01", title: "Define Domain", desc: "Select your area of interest and current skill level to set the foundation." },
                { step: "02", title: "Describe Vision", desc: "Tell us what you're thinking in your own words. No technical jargon required." },
                { step: "03", title: "Receive Roadmap", desc: "Get a curated list of projects with difficulty ratings and full tech stacks." }
              ].map((item, i) => (
                <motion.div 
                  key={i}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ delay: i * 0.2, duration: 0.6, ease: "easeOut" }}
                  className="relative group p-6 -m-6 rounded-2xl transition-all duration-300 hover:bg-white/40"
                >
                  <span className="text-8xl font-serif text-black/5 absolute -top-6 -left-2 select-none pointer-events-none transition-colors duration-500 group-hover:text-accent/10">{item.step}</span>
                  <div className="relative z-10 pt-6">
                    <h3 className="text-2xl font-bold mb-4 pt-4 border-t border-black/10 transition-colors duration-300 group-hover:border-accent/30">{item.title}</h3>
                    <p className="text-primary/60 leading-relaxed group-hover:text-primary/80 transition-colors">{item.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Who Is This For? - Professional Layout */}
        <section id="who-is-it-for" className="py-32 px-6 max-w-7xl mx-auto">
          <div className="grid md:grid-cols-12 gap-12 items-center">
            <div className="md:col-span-7">
              <h2 className="text-5xl font-serif mb-10 leading-tight">Built for the next <br /> generation of <span className="text-accent italic">innovators.</span></h2>
              <div className="grid sm:grid-cols-2 gap-8">
                {[
                  { title: "CS Students", desc: "Find final year projects that actually impress recruiters." },
                  { title: "Hackathon Junkies", desc: "Get unique ideas that stand out to judges in 48 hours." },
                  { title: "Self-Taught Devs", desc: "Bridge the gap between tutorials and real-world builds." },
                  { title: "Engineering Leads", desc: "Help your juniors find meaningful side projects." }
                ].map((item, i) => (
                  <div key={i} className="group">
                    <h4 className="font-bold text-lg mb-2 group-hover:text-accent transition-colors flex items-center gap-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-accent" /> {item.title}
                    </h4>
                    <p className="text-sm text-primary/60 leading-relaxed">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="md:col-span-5">
              <div className="relative">
                <TestimonialFlipper />
                <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-accent rounded-2xl -rotate-6 -z-10 shadow-xl" />
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="py-20 px-6 border-t border-black/5 text-center bg-white/20">
        <div className="bg-primary p-3 rounded-full w-fit mx-auto mb-6">
          <Sparkles className="w-5 h-5 text-accent" />
        </div>
        <p className="text-primary/40 font-medium tracking-widest uppercase text-xs mb-2">IdeaSpark © 2024</p>
        <p className="text-primary/60 italic font-serif text-lg">Built for curious minds.</p>
      </footer>
    </div>
  );
}
