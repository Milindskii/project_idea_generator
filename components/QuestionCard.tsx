'use client';

import { motion } from 'framer-motion';

interface QuestionCardProps {
  step: any;
  value: string;
  onChange: (val: string) => void;
}

export default function QuestionCard({ step, value, onChange }: QuestionCardProps) {
  return (
    <div className="w-full">
      <h2 className="text-3xl md:text-4xl font-serif text-primary mb-8 leading-tight">
        {step.question}
      </h2>

      {step.type === 'cards' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {step.options.map((option: string) => (
            <button
              key={option}
              onClick={() => onChange(option)}
              className={`p-6 rounded-2xl text-left transition-all border-2 ${
                value === option
                  ? 'border-accent bg-accent/5 shadow-md'
                  : 'border-transparent bg-white hover:border-black/10 shadow-sm'
              }`}
            >
              <span className={`text-lg font-medium ${value === option ? 'text-accent' : 'text-primary'}`}>
                {option}
              </span>
            </button>
          ))}
        </div>
      )}

      {step.type === 'visual-selector' && (
        <div className="flex flex-col gap-4">
          {step.options.map((option: string) => (
            <button
              key={option}
              onClick={() => onChange(option)}
              className={`p-6 rounded-2xl flex items-center justify-between transition-all border-2 ${
                value === option
                  ? 'border-accent bg-accent/5 shadow-md'
                  : 'border-transparent bg-white hover:border-black/10 shadow-sm'
              }`}
            >
              <span className={`text-lg font-medium ${value === option ? 'text-accent' : 'text-primary'}`}>
                {option}
              </span>
              {value === option && (
                <motion.div
                  layoutId="check"
                  className="w-6 h-6 rounded-full bg-accent flex items-center justify-center"
                >
                  <div className="w-2 h-2 rounded-full bg-white" />
                </motion.div>
              )}
            </button>
          ))}
        </div>
      )}

      {step.type === 'textarea' && (
        <div className="w-full">
          <textarea
            autoFocus
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={step.placeholder}
            className="w-full h-48 p-6 rounded-2xl bg-white border-2 border-transparent focus:border-accent outline-none shadow-sm text-lg resize-none transition-all placeholder:text-primary/20"
          />
          <p className="mt-4 text-sm text-primary/40 italic">
            Tip: Be as specific as possible for better results.
          </p>
        </div>
      )}
    </div>
  );
}
