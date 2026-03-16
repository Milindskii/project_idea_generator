'use client';

import { motion } from 'framer-motion';
import { BrainCircuit } from 'lucide-react';

interface AIThoughtsPanelProps {
  text: string;
}

export default function AIThoughtsPanel({ text }: AIThoughtsPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-primary/5 border-l-4 border-accent p-8 rounded-r-2xl mb-12 relative overflow-hidden"
    >
      <div className="absolute top-0 right-0 p-4 opacity-10">
        <BrainCircuit className="w-24 h-24 text-primary" />
      </div>
      <div className="relative z-10">
        <h3 className="text-xs font-bold uppercase tracking-widest text-accent mb-4 flex items-center gap-2">
          AI Analysis & Feasibility
        </h3>
        <p className="text-xl font-serif italic text-primary/80 leading-relaxed">
          "{text}"
        </p>
      </div>
    </motion.div>
  );
}
