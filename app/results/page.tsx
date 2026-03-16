'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Navbar from '@/components/Navbar';
import AIThoughtsPanel from '@/components/AIThoughtsPanel';
import ProjectCard from '@/components/ProjectCard';
import { MOCK_RESULTS } from '@/data/mockResults';
import { RefreshCw, RotateCcw, Sparkles } from 'lucide-react';

export default function ResultsPage() {
  const router = useRouter();
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleRegenerate = () => {
    setIsRegenerating(true);
    setTimeout(() => {
      setIsRegenerating(false);
    }, 1500);
  };

  const handleStartOver = () => {
    router.push('/questions');
  };

  return (
    <div className="min-h-screen flex flex-col bg-paper pb-24">
      <Navbar />
      
      <main className="flex-grow max-w-6xl mx-auto px-6 pt-12">
        <header className="mb-12 text-center md:text-left">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3 mb-4 justify-center md:justify-start"
          >
            <div className="bg-accent/10 p-2 rounded-lg">
              <Sparkles className="w-5 h-5 text-accent" />
            </div>
            <span className="text-sm font-bold uppercase tracking-widest text-primary/40">
              Analysis Complete
            </span>
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-5xl font-serif text-primary"
          >
            Your Project Roadmap
          </motion.h1>
        </header>

        <AIThoughtsPanel text={MOCK_RESULTS.analysis} />

        <div className="mb-8 flex items-center justify-between">
          <h2 className="text-2xl font-serif text-primary">Recommended Project Ideas</h2>
          <div className="h-px flex-grow mx-6 bg-black/5 hidden md:block" />
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-16">
          {MOCK_RESULTS.projects.map((project, index) => (
            <ProjectCard key={project.id} project={project} index={index} />
          ))}
        </div>

        <div className="flex flex-col md:flex-row items-center justify-center gap-4">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="btn-primary flex items-center gap-2 min-w-[200px] justify-center"
          >
            <RefreshCw className={`w-4 h-4 ${isRegenerating ? 'animate-spin' : ''}`} />
            {isRegenerating ? 'Regenerating...' : 'Regenerate Ideas'}
          </button>
          <button
            onClick={handleStartOver}
            className="px-8 py-3 rounded-xl font-medium text-primary/60 hover:text-primary hover:bg-black/5 transition-all flex items-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Start Over
          </button>
        </div>
      </main>
    </div>
  );
}
