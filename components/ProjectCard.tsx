'use client';

import { motion } from 'framer-motion';
import { ExternalLink, Zap } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface ProjectCardProps {
  project: {
    id: number;
    title: string;
    description: string;
    techStack: string[];
    difficulty: string;
    matchScore: number;
  };
  index: number;
}

export default function ProjectCard({ project, index }: ProjectCardProps) {
  const router = useRouter();

  const handleExplore = () => {
    const params = new URLSearchParams({
      title: project.title,
      description: project.description,
      difficulty: project.difficulty,
      tech: project.techStack.join(', '),
    });
    router.push(`/explore/${project.id}?${params.toString()}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 + 0.3 }}
      className="card group hover:shadow-xl transition-all duration-300 flex flex-col h-full"
    >
      <div className="flex justify-between items-start mb-4">
        <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
          project.difficulty === 'Beginner' ? 'bg-success/10 text-success' :
          project.difficulty === 'Intermediate' ? 'bg-blue-500/10 text-blue-600' :
          'bg-purple-500/10 text-purple-600'
        }`}>
          {project.difficulty}
        </span>
        <div className="flex items-center gap-1 text-success font-bold text-sm">
          <Zap className="w-3 h-3 fill-current" />
          {project.matchScore}% Match
        </div>
      </div>

      <h3 className="text-xl font-bold mb-3 group-hover:text-accent transition-colors">
        {project.title}
      </h3>
      <p className="text-primary/60 text-sm mb-6 flex-grow">
        {project.description}
      </p>

      <div className="flex flex-wrap gap-2 mb-6">
        {project.techStack.map((tech) => (
          <span key={tech} className="px-2 py-1 bg-paper rounded text-[10px] font-medium text-primary/70">
            {tech}
          </span>
        ))}
      </div>

      <button
        onClick={handleExplore}
        className="w-full py-3 rounded-xl border border-primary/10 font-medium text-sm flex items-center justify-center gap-2 hover:bg-primary hover:text-white transition-all"
      >
        Explore This Idea <ExternalLink className="w-4 h-4" />
      </button>
    </motion.div>
  );
}
