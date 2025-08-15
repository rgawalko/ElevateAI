import React, { useState, useEffect } from 'react';
import { Plus, Target, Calendar, TrendingUp, CheckCircle, Clock } from 'lucide-react';
import { Card, Button } from '../components';
import type { Goal, GoalCategory, Priority } from '../types';
import { GoalCategory as GoalCategoryEnum, Priority as PriorityEnum } from '../types';
import { goalService, type GoalCreateData } from '../services/goalService';

export const Goals: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load goals from API
  useEffect(() => {
    loadGoals();
  }, []);

  const loadGoals = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await goalService.getGoals({
        activeOnly: true,
        page: 1,
        perPage: 50
      });

      setGoals(response.goals);
      console.log('✅ Goals loaded successfully:', response.goals);
    } catch (error) {
      console.error('❌ Error loading goals:', error);
      setError('Failed to load goals. Please try again.');

      // Fallback to mock data if API fails
      setGoals([
    {
      id: '1',
      title: 'Complete React Project',
      description: 'Finish the productivity app with all features',
      category: GoalCategoryEnum.PROFESSIONAL,
      priority: PriorityEnum.HIGH,
      targetDate: new Date('2024-02-15'),
      progress: 75,
      status: 'in_progress',
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-01-15')
    },
    {
      id: '2',
      title: 'Read 12 Books This Year',
      description: 'Expand knowledge through consistent reading',
      category: GoalCategoryEnum.PERSONAL,
      priority: PriorityEnum.MEDIUM,
      targetDate: new Date('2024-12-31'),
      progress: 25,
      status: 'in_progress',
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-01-10')
    },
    {
      id: '3',
      title: 'Exercise 4x per Week',
      description: 'Maintain consistent fitness routine',
      category: GoalCategoryEnum.HEALTH,
      priority: PriorityEnum.HIGH,
      targetDate: new Date('2024-12-31'),
      progress: 60,
      status: 'in_progress',
      createdAt: new Date('2024-01-01'),
      updatedAt: new Date('2024-01-14')
    }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const stats = {
    totalGoals: goals.length,
    completedGoals: goals.filter(g => g.status === 'completed').length,
    inProgressGoals: goals.filter(g => g.status === 'in_progress').length,
    averageProgress: Math.round(goals.reduce((acc, goal) => acc + goal.progress, 0) / goals.length)
  };

  const getCategoryColor = (category: GoalCategory): string => {
    const colors = {
      [GoalCategoryEnum.PERSONAL]: 'bg-blue-100 text-blue-800 border-blue-200',
      [GoalCategoryEnum.PROFESSIONAL]: 'bg-green-100 text-green-800 border-green-200',
      [GoalCategoryEnum.HEALTH]: 'bg-red-100 text-red-800 border-red-200',
      [GoalCategoryEnum.FINANCIAL]: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      [GoalCategoryEnum.LEARNING]: 'bg-purple-100 text-purple-800 border-purple-200'
    };
    return colors[category] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getPriorityColor = (priority: Priority): string => {
    const colors = {
      [PriorityEnum.LOW]: 'text-green-600',
      [PriorityEnum.MEDIUM]: 'text-yellow-600',
      [PriorityEnum.HIGH]: 'text-red-600'
    };
    return colors[priority];
  };

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight" style={{color: '#026670'}}>Goals</h1>
          <p className="mt-2 text-lg font-medium" style={{color: '#026670'}}>
            Set, track, and achieve your personal and professional goals
          </p>
        </div>
        <Button onClick={() => setShowForm(true)} icon={<Plus size={18} />} size="lg">
          Add Goal
        </Button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-3 text-secondary-600">Loading your goals...</span>
        </div>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-red-800">Error loading goals</p>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={loadGoals}
              className="border-red-300 text-red-700 hover:bg-red-100"
            >
              Try Again
            </Button>
          </div>
        </Card>
      )}

      {/* Stats Overview */}
      {!isLoading && !error && (
      <>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card hover className="group">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-sm group-hover:shadow-md transition-all duration-200">
                <Target className="w-6 h-6 text-blue-600 transition-transform duration-200 group-hover:scale-110" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-semibold uppercase tracking-wide" style={{color: '#026670'}}>Total Goals</p>
                <p className="text-2xl font-bold mt-1" style={{color: '#026670'}}>{stats.totalGoals}</p>
              </div>
            </div>
          </div>
        </Card>

        <Card hover className="group">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-green-50 to-green-100 rounded-xl shadow-sm group-hover:shadow-md transition-all duration-200">
                <CheckCircle className="w-6 h-6 text-green-600 transition-transform duration-200 group-hover:scale-110" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-semibold uppercase tracking-wide" style={{color: '#026670'}}>Completed</p>
                <p className="text-2xl font-bold mt-1" style={{color: '#026670'}}>{stats.completedGoals}</p>
              </div>
            </div>
          </div>
        </Card>

        <Card hover className="group">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl shadow-sm group-hover:shadow-md transition-all duration-200">
                <Clock className="w-6 h-6 text-yellow-600 transition-transform duration-200 group-hover:scale-110" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-semibold uppercase tracking-wide" style={{color: '#026670'}}>In Progress</p>
                <p className="text-2xl font-bold mt-1" style={{color: '#026670'}}>{stats.inProgressGoals}</p>
              </div>
            </div>
          </div>
        </Card>

        <Card hover className="group">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl shadow-sm group-hover:shadow-md transition-all duration-200">
                <TrendingUp className="w-6 h-6 text-purple-600 transition-transform duration-200 group-hover:scale-110" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-semibold uppercase tracking-wide" style={{color: '#026670'}}>Avg Progress</p>
                <p className="text-2xl font-bold mt-1" style={{color: '#026670'}}>{stats.averageProgress}%</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Goals List */}
      <Card title="Your Goals" className="space-y-4">
        {goals.map((goal) => (
          <div key={goal.id} className="p-6 bg-gradient-to-r from-secondary-50 to-white rounded-xl border border-secondary-200/50 hover:shadow-md hover:scale-[1.01] transition-all duration-200 group">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-3">
                  <h3 className="text-lg font-bold" style={{color: '#026670'}}>{goal.title}</h3>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${getCategoryColor(goal.category)}`}>
                    {goal.category}
                  </span>
                  <span className={`text-sm font-semibold ${getPriorityColor(goal.priority)}`}>
                    {goal.priority} priority
                  </span>
                </div>
                
                <p className="mb-4 font-medium" style={{color: '#026670'}}>{goal.description}</p>
                
                <div className="flex items-center space-x-6 mb-4">
                  <div className="flex items-center space-x-2">
                    <Calendar className="w-4 h-4 text-secondary-400" />
                    <span className="text-sm font-medium" style={{color: 'rgba(2, 102, 112, 0.7)'}}>
                      Target: {formatDate(goal.targetDate)}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4 text-secondary-400" />
                    <span className="text-sm font-medium" style={{color: 'rgba(2, 102, 112, 0.7)'}}>
                      Progress: {Math.round(goal.progress)}%
                    </span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-secondary-200 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-primary-500 to-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.round(goal.progress)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </Card>
      </>
      )}
    </div>
  );
};
