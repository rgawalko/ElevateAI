import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface QuizOption {
  text: string;
  score: number;
}

interface QuizQuestion {
  id: number;
  section: string;
  question: string;
  options: QuizOption[];
}

interface QuizData {
  title: string;
  description: string;
  sections: string[];
  questions: QuizQuestion[];
}

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

interface ChronotypeQuizProps {
  onComplete: (result: ChronotypeResult) => void;
  onSkip?: () => void;
}

interface ChronotypeResultProps {
  result: ChronotypeResult;
  onContinue: () => void;
}

export const ChronotypeResult: React.FC<ChronotypeResultProps> = ({ result, onContinue }) => {
  const getChronotypeColor = (chronotype: string) => {
    switch (chronotype) {
      case 'Lark': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'Intermediate': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'Owl': return 'text-purple-600 bg-purple-50 border-purple-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getChronotypeIcon = (chronotype: string) => {
    switch (chronotype) {
      case 'Lark':
        return (
          <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        );
      case 'Intermediate':
        return (
          <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        );
      case 'Owl':
        return (
          <svg className="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto h-16 w-16 bg-green-500 rounded-full flex items-center justify-center mb-4">
            <svg className="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Quiz Complete!</h1>
          <p className="text-gray-600">Here are your personalized chronotype results</p>
        </div>

        {/* Results Card */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Chronotype Header */}
          <div className={`p-8 border-b-4 ${getChronotypeColor(result.chronotype)}`}>
            <div className="flex items-center justify-center mb-4">
              <div className={`p-3 rounded-full ${getChronotypeColor(result.chronotype)}`}>
                {getChronotypeIcon(result.chronotype)}
              </div>
            </div>
            <h2 className="text-3xl font-bold text-center mb-2">
              You are a <span className={getChronotypeColor(result.chronotype).split(' ')[0]}>{result.chronotype}</span>
            </h2>
            <p className="text-center text-gray-600 text-lg">
              Score: {result.total}/45
            </p>
          </div>

          <div className="p-8">
            {/* Description */}
            <div className="mb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-3">What this means</h3>
              <p className="text-gray-700 leading-relaxed">{result.description}</p>
            </div>

            {/* Peak Performance Windows */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                <h4 className="font-semibold text-green-800 mb-2 flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Primary Peak Window
                </h4>
                <p className="text-2xl font-bold text-green-700">
                  {result.peak_window.start} - {result.peak_window.end}
                </p>
                <p className="text-sm text-green-600 mt-1">Best time for important tasks</p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h4 className="font-semibold text-blue-800 mb-2 flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707" />
                  </svg>
                  Secondary Peak Window
                </h4>
                <p className="text-2xl font-bold text-blue-700">
                  {result.secondary_window.start} - {result.secondary_window.end}
                </p>
                <p className="text-sm text-blue-600 mt-1">Good for moderate tasks</p>
              </div>
            </div>

            {/* Recommendations */}
            <div className="mb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Personalized Recommendations</h3>
              <div className="space-y-3">
                {result.recommendations?.map((recommendation, index) => (
                  <div key={index} className="flex items-start">
                    <div className="flex-shrink-0 w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                      <span className="text-indigo-600 text-sm font-semibold">{index + 1}</span>
                    </div>
                    <p className="text-gray-700">{recommendation}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Continue Button */}
            <div className="text-center">
              <button
                onClick={onContinue}
                className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 transition-colors font-semibold"
              >
                Continue to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export const ChronotypeQuiz: React.FC<ChronotypeQuizProps> = ({ onComplete, onSkip }) => {
  const [quizData, setQuizData] = useState<QuizData | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchQuizData();
  }, []);

  const fetchQuizData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/chronotype/quiz');
      const data = await response.json();
      
      if (data.success) {
        setQuizData(data.data);
        setAnswers(new Array(data.data.questions.length).fill(0));
      } else {
        setError('Failed to load quiz data');
      }
    } catch (error) {
      console.error('Error fetching quiz data:', error);
      setError('Failed to load quiz. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerSelect = (score: number) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = score;
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < (quizData?.questions.length || 0) - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      submitQuiz();
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const submitQuiz = async () => {
    if (!quizData) return;

    setIsSubmitting(true);
    try {
      const token = localStorage.getItem('elevate_auth_token');
      const response = await fetch('http://localhost:8000/api/chronotype/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ answers })
      });

      const data = await response.json();
      
      if (data.success && data.result) {
        onComplete(data.result);
      } else {
        setError(data.message || 'Failed to submit quiz');
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
      setError('Failed to submit quiz. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getChronotypeColor = (chronotype: string) => {
    switch (chronotype) {
      case 'Lark': return 'text-yellow-600';
      case 'Intermediate': return 'text-blue-600';
      case 'Owl': return 'text-purple-600';
      default: return 'text-gray-600';
    }
  };

  const getProgressPercentage = () => {
    if (!quizData) return 0;
    return ((currentQuestion + 1) / quizData.questions.length) * 100;
  };

  const isCurrentAnswered = () => {
    return answers[currentQuestion] > 0;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading chronotype quiz...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="text-red-500 mb-4">
            <svg className="h-12 w-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Quiz</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!quizData) return null;

  const currentQuestionData = quizData.questions[currentQuestion];
  const sectionNames = {
    'A': 'Sleep Preferences',
    'B': 'Energy Levels', 
    'C': 'Lifestyle & Behavior'
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="mx-auto h-12 w-12 bg-indigo-600 rounded-lg flex items-center justify-center mb-4">
            <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{quizData.title}</h1>
          <p className="text-gray-600">{quizData.description}</p>
          
          {/* Skip option */}
          {onSkip && (
            <button
              onClick={onSkip}
              className="mt-4 text-sm text-gray-500 hover:text-gray-700 underline"
            >
              Skip for now
            </button>
          )}
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Question {currentQuestion + 1} of {quizData.questions.length}</span>
            <span>{Math.round(getProgressPercentage())}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getProgressPercentage()}%` }}
            ></div>
          </div>
        </div>

        {/* Quiz Card */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Section Header */}
          <div className="mb-6">
            <span className="inline-block bg-indigo-100 text-indigo-800 text-xs font-semibold px-2.5 py-0.5 rounded-full mb-2">
              Section {currentQuestionData.section}: {sectionNames[currentQuestionData.section as keyof typeof sectionNames]}
            </span>
            <h2 className="text-xl font-semibold text-gray-900">
              {currentQuestionData.question}
            </h2>
          </div>

          {/* Answer Options */}
          <div className="space-y-3 mb-8">
            {currentQuestionData.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswerSelect(option.score)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ${
                  answers[currentQuestion] === option.score
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-900'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center">
                  <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                    answers[currentQuestion] === option.score
                      ? 'border-indigo-500 bg-indigo-500'
                      : 'border-gray-300'
                  }`}>
                    {answers[currentQuestion] === option.score && (
                      <div className="w-full h-full rounded-full bg-white scale-50"></div>
                    )}
                  </div>
                  <span className="font-medium">{option.text}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <button
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            
            <button
              onClick={handleNext}
              disabled={!isCurrentAnswered() || isSubmitting}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Submitting...
                </>
              ) : currentQuestion === quizData.questions.length - 1 ? (
                'Complete Quiz'
              ) : (
                'Next'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
