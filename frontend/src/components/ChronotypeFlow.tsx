import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChronotypeQuiz, ChronotypeResult } from './ChronotypeQuiz';

interface ChronotypeResult {
  answers: number[];
  total: number;
  chronotype: string;
  peak_window: {
    start: string;
    end: string;
  };
  secondary_window: {
    start: string;
    end: string;
  };
  description: string;
  recommendations: string[];
}

interface ChronotypeFlowProps {
  onComplete?: () => void;
}

export const ChronotypeFlow: React.FC<ChronotypeFlowProps> = ({ onComplete }) => {
  const [currentStep, setCurrentStep] = useState<'quiz' | 'result'>('quiz');
  const [quizResult, setQuizResult] = useState<ChronotypeResult | null>(null);
  const navigate = useNavigate();

  const handleQuizComplete = (result: ChronotypeResult) => {
    setQuizResult(result);
    setCurrentStep('result');
  };

  const handleSkipQuiz = () => {
    // Navigate directly to dashboard if user skips
    navigate('/dashboard');
    if (onComplete) {
      onComplete();
    }
  };

  const handleContinue = () => {
    // Navigate to dashboard after viewing results
    navigate('/dashboard');
    if (onComplete) {
      onComplete();
    }
  };

  if (currentStep === 'quiz') {
    return (
      <ChronotypeQuiz 
        onComplete={handleQuizComplete}
        onSkip={handleSkipQuiz}
      />
    );
  }

  if (currentStep === 'result' && quizResult) {
    return (
      <ChronotypeResult 
        result={quizResult}
        onContinue={handleContinue}
      />
    );
  }

  return null;
};
