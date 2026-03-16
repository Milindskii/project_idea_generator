'use client';

import { motion } from 'framer-motion';

interface ProgressBarProps {
  current: number;
  total: number;
}

export default function ProgressBar({ current, total }: ProgressBarProps) {
  const progress = (current / total) * 100;

  return (
    <div className="w-full">
      <div className="flex justify-between items-end mb-4">
        <span className="text-sm font-medium text-primary/40 uppercase tracking-wider">
          Step {current} of {total}
        </span>
        <span className="text-2xl font-serif font-bold text-primary">
          {Math.round(progress)}%
        </span>
      </div>
      <div className="h-2 w-full bg-black/5 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: "circOut" }}
          className="h-full bg-accent"
        />
      </div>
    </div>
  );
}
