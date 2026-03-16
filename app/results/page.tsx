'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter as useNextRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import Navbar from '@/components/Navbar';
import AIThoughtsPanel from '@/components/AIThoughtsPanel';
import ProjectCard from '@/components/ProjectCard';
import { useUserInputs } from '@/context/UserInputContext';
import { RefreshCw, RotateCcw, Sparkles, AlertCircle } from 'lucide-react';

interface Project {
  id: number;
  title: string;
  description: string;
  techStack: string[];
  difficulty: string;
  matchScore: number;
}

interface BackendData {
  analysis: string;
  projects: Project[];
}

export default function ResultsPage() {
  const router = useNextRouter();
  const { inputs } = useUserInputs();
  const [data, setData] = useState<BackendData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [regenerateKey, setRegenerateKey] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('http://localhost:8000/api/generate-ideas', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(inputs),
        });

        if (!response.ok) {
          throw new Error('Failed to fetch project ideas');
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unexpected error occurred');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [inputs, regenerateKey]);

  const handleRegenerate = () => {
    setRegenerateKey((k) => k + 1);
  };

  const handleStartOver = () => {
    router.push('/questions');
  };

  if (loading && !data) {
    return (
      <div className="min-h-screen flex flex-col bg-paper">
        <Navbar />
        <main className="flex-grow flex flex-col items-center justify-center p-6 text-center">
          <div className="bg-accent/10 p-4 rounded-2xl mb-6 animate-pulse">
            <Sparkles className="w-8 h-8 text-accent grayscale" />
          </div>
          <h2 className="text-2xl font-serif text-primary mb-2">Analyzing Your Idea</h2>
          <p className="text-primary/60 max-w-md">Our AI is processing your inputs to build a custom roadmap...</p>
          <div className="mt-8 flex gap-2">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="w-2 h-2 rounded-full bg-accent"
                animate={{ scale: [1, 1.5, 1], opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
              />
            ))}
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col bg-paper">
        <Navbar />
        <main className="flex-grow flex flex-col items-center justify-center p-6 text-center">
          <div className="bg-red-50 to-red-100 p-4 rounded-2xl mb-6">
            <AlertCircle className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="text-2xl font-serif text-primary mb-2">Something went wrong</h2>
          <p className="text-primary/60 max-w-md mb-8">{error}. Please make sure the backend server is running.</p>
          <button onClick={() => setRegenerateKey(k => k + 1)} className="btn-primary">Try Again</button>
        </main>
      </div>
    );
  }

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

        {data && <AIThoughtsPanel text={data.analysis} />}

        <div className="mb-8 flex items-center justify-between">
          <h2 className="text-2xl font-serif text-primary">Recommended Project Ideas</h2>
          <div className="h-px flex-grow mx-6 bg-black/5 hidden md:block" />
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-16">
          {data?.projects.map((project, index) => (
            <ProjectCard key={project.id} project={project} index={index} />
          ))}
        </div>

        <div className="flex flex-col md:flex-row items-center justify-center gap-4">
          <button
            onClick={handleRegenerate}
            disabled={loading}
            className="btn-primary flex items-center gap-2 min-w-[200px] justify-center"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            {loading ? 'Regenerating...' : 'Regenerate Ideas'}
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
