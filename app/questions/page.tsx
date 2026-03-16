'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useUserInputs } from '@/context/UserInputContext';
import Navbar from '@/components/Navbar';
import ProgressBar from '@/components/ProgressBar';
import QuestionCard from '@/components/QuestionCard';
import { ArrowLeft, ArrowRight, Sparkles } from 'lucide-react';

const STEPS = [
  {
    id: 'domain',
    question: 'What domain interests you?',
    options: ['AI', 'Web Dev', 'IoT', 'Mobile Apps', 'Cybersecurity', 'Data Science'],
    type: 'cards',
  },
  {
    id: 'skillLevel',
    question: 'What is your current skill level?',
    options: ['Beginner', 'Intermediate', 'Advanced'],
    type: 'visual-selector',
  },
  {
    id: 'timeframe',
    question: 'How much time do you have?',
    options: ['1 week', '1 month', '3 months', '6+ months'],
    type: 'cards',
  },
  {
    id: 'goal',
    question: "What's your goal?",
    options: ['Learn a skill', 'Build a portfolio', 'Win a hackathon', 'Final year project'],
    type: 'cards',
  },
  {
    id: 'ideaDescription',
    question: 'Describe your idea or interest in your own words',
    placeholder: 'e.g. I want to build something that helps farmers detect crop disease using AI...',
    type: 'textarea',
  },
];

export default function QuestionsPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const { inputs, updateInput } = useUserInputs();
  const router = useRouter();

  const handleNext = () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      router.push('/analyzing');
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else {
      router.push('/');
    }
  };

  const isStepValid = () => {
    const step = STEPS[currentStep];
    const value = inputs[step.id as keyof typeof inputs];
    return value && value.trim().length > 0;
  };

  return (
    <div className="min-h-screen flex flex-col bg-paper">
      <Navbar />
      
      <main className="flex-grow flex flex-col items-center px-6 pt-12 pb-24">
        <div className="w-full max-w-2xl">
          <ProgressBar current={currentStep + 1} total={STEPS.length} />
          
          <div className="mt-12 relative min-h-[400px]">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <QuestionCard
                  step={STEPS[currentStep]}
                  value={inputs[STEPS[currentStep].id as keyof typeof inputs]}
                  onChange={(val) => updateInput(STEPS[currentStep].id as any, val)}
                />
              </motion.div>
            </AnimatePresence>
          </div>

          <div className="flex items-center justify-between mt-12">
            <button
              onClick={handleBack}
              className="flex items-center gap-2 text-primary/60 hover:text-primary font-medium transition-colors"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
            
            <button
              onClick={handleNext}
              disabled={!isStepValid()}
              className={`btn-primary flex items-center gap-2 ${
                !isStepValid() ? 'opacity-50 cursor-not-allowed grayscale' : ''
              }`}
            >
              {currentStep === STEPS.length - 1 ? (
                <>Analyze My Idea <Sparkles className="w-4 h-4" /></>
              ) : (
                <>Next <ArrowRight className="w-4 h-4" /></>
              )}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
