'use client';

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const testimonials = [
  {
    quote: "IdeaSpark helped me find a project that got me my first internship at a top tech firm.",
    author: "Sarah Chen",
    role: "CS Junior",
    image: "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?auto=format&fit=crop&q=80"
  },
  {
    quote: "I finally built something useful instead of just watching another tutorial. The roadmap was perfect.",
    author: "Marcus Rodriguez",
    role: "Self-Taught Dev",
    image: "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&q=80"
  },
  {
    quote: "The project roadmap it gave our team won us 1st place at the university hackathon.",
    author: "Priya Patel",
    role: "Hackathon Winner",
    image: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&q=80"
  },
  {
    quote: "It felt like having a senior engineer mentoring me. My portfolio actually stands out now.",
    author: "David Kim",
    role: "Bootcamp Grad",
    image: "https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&q=80"
  },
  {
    quote: "A game-changer for finding final year projects that hit the sweet spot of challenging but doable.",
    author: "Aisha Johnson",
    role: "Engineering Lead",
    image: "https://images.unsplash.com/photo-1531545514256-b1400bc00f31?auto=format&fit=crop&q=80"
  }
];

export default function TestimonialFlipper() {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % testimonials.length);
    }, 8000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div 
      className="relative aspect-[4/5] w-full cursor-pointer rotate-2 group"
      style={{ perspective: "1000px" }}
      onClick={() => setCurrentIndex((prev) => (prev + 1) % testimonials.length)}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 1.0, ease: "easeInOut" }}
          className="absolute inset-0 bg-primary rounded-2xl overflow-hidden shadow-2xl"
        >
          <div 
            className="absolute inset-0 bg-cover bg-center mix-blend-overlay opacity-50 transition-transform duration-700 group-hover:scale-105"
            style={{ backgroundImage: `url('${testimonials[currentIndex].image}')` }}
          />
          <div className="absolute inset-0 p-10 flex flex-col justify-end text-white bg-gradient-to-t from-black/80 via-black/20 to-transparent">

            
            <p className="text-2xl font-serif italic mb-4">"{testimonials[currentIndex].quote}"</p>
            <p className="font-bold uppercase tracking-widest text-xs opacity-80">— {testimonials[currentIndex].author}, {testimonials[currentIndex].role}</p>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
