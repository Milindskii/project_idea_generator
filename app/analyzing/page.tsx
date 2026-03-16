'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useUserInputs } from '@/context/UserInputContext';
import Navbar from '@/components/Navbar';
import { Sparkles, CheckCircle2 } from 'lucide-react';

const LOADING_STATEMENTS = [
  "Reading your inputs...",
  "Understanding your skill level...",
  "Mapping your idea to project domains...",
  "Cross-referencing tech stacks...",
  "Evaluating feasibility...",
  "Almost there — finalizing suggestions...",
];

export default function AnalyzingPage() {
  const [statementIndex, setStatementIndex] = useState(0);
  const { inputs } = useUserInputs();
  const router = useRouter();

  useEffect(() => {
    // Cycle through statements
    const interval = setInterval(() => {
      setStatementIndex((prev) => {
        if (prev < LOADING_STATEMENTS.length - 1) return prev + 1;
        return prev;
      });
    }, 1500);

    // Auto-navigate after ~9 seconds
    const timeout = setTimeout(() => {
      router.push('/results');
    }, 9000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [router]);

  return (
    <div className="min-h-screen flex flex-col bg-paper overflow-hidden">
      <Navbar />
      
      <main className="flex-grow flex flex-col items-center justify-center px-6 relative">
        {/* Subtle Background Animation */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.1, 0.2, 0.1],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="w-[500px] h-[500px] bg-accent rounded-full blur-[120px]"
          />
        </div>

        <div className="z-10 text-center max-w-lg w-full">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="mb-12 inline-block"
          >
            <div className="relative">
              <div className="w-24 h-24 rounded-3xl bg-primary flex items-center justify-center shadow-2xl">
                <Sparkles className="w-10 h-10 text-accent animate-pulse" />
              </div>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                className="absolute -inset-4 border-2 border-dashed border-accent/30 rounded-full"
              />
            </div>
          </motion.div>

          <div className="h-20 flex items-center justify-center">
            <AnimatePresence mode="wait">
              <motion.p
                key={statementIndex}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-2xl font-serif text-primary italic"
              >
                {LOADING_STATEMENTS[statementIndex]}
              </motion.p>
            </AnimatePresence>
          </div>

          {/* Input Summary Card */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-16 card text-left border-accent/10 bg-white/50 backdrop-blur-sm"
          >
            <h3 className="text-xs font-bold uppercase tracking-widest text-primary/40 mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-success" /> Your Input Summary
            </h3>
            <div className="grid grid-cols-2 gap-y-4 gap-x-8">
              <div>
                <p className="text-[10px] uppercase text-primary/40 font-bold">Domain</p>
                <p className="font-medium">{inputs.domain || 'Not selected'}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase text-primary/40 font-bold">Skill Level</p>
                <p className="font-medium">{inputs.skillLevel || 'Not selected'}</p>
              </div>
              <div className="col-span-2">
                <p className="text-[10px] uppercase text-primary/40 font-bold">Your Idea</p>
                <p className="text-sm italic text-primary/70 line-clamp-2">
                  "{inputs.ideaDescription || 'No description provided'}"
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
