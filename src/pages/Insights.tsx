import React from 'react';
import { 
  Brain, 
  TrendingUp, 
  Clock, 
  Target, 
  Lightbulb,
  BarChart3,
  PieChart,
  Activity
} from 'lucide-react';
import { Card, Button } from '../components';
import { Insight, InsightType, ActivityCategory } from '../types';
import { formatDate, getCategoryColor, getCategoryIcon } from '../utils';

export const Insights: React.FC = () => {
  // Mock insights data - in a real app, this would come from API
  const insights: Insight[] = [
    {
      id: '1',
      userId: 'user1',
      type: InsightType.PRODUCTIVITY_PATTERN,
      title: 'Peak Productivity Hours',
      description: 'Your most productive hours are between 9-11 AM with an average productivity score of 8.5/10.',
      data: {
        peakHours: '9-11 AM',
        averageScore: 8.5,
        confidence: 0.85
      },
      actionable: true,
      recommendations: [
        'Schedule your most important tasks during 9-11 AM',
        'Avoid meetings during peak productivity hours',
        'Use this time for deep work and complex problem-solving'
      ],
      createdAt: new Date('2024-01-15T10:00:00')
    },
    {
      id: '2',
      userId: 'user1',
      type: InsightType.ENERGY_OPTIMIZATION,
      title: 'Energy Dip Pattern',
      description: 'You experience a consistent energy drop around 2-3 PM. A 15-minute walk could boost your energy by 20%.',
      data: {
        dipTime: '2-3 PM',
        energyDrop: 1.5,
        suggestedBoost: 0.8
      },
      actionable: true,
      recommendations: [
        'Take a 15-minute walk after lunch',
        'Consider a healthy snack around 2 PM',
        'Schedule lighter tasks during this period'
      ],
      createdAt: new Date('2024-01-15T15:30:00')
    },
    {
      id: '3',
      userId: 'user1',
      type: InsightType.MOOD_CORRELATION,
      title: 'Exercise & Mood Connection',
      description: 'Your mood improves by 40% on days when you exercise in the morning.',
      data: {
        correlation: 0.75,
        moodImprovement: 1.6,
        sampleSize: 30
      },
      actionable: true,
      recommendations: [
        'Maintain your morning exercise routine',
        'Consider adding weekend morning workouts',
        'Track mood changes on rest days'
      ],
      createdAt: new Date('2024-01-15T08:00:00')
    },
    {
      id: '4',
      userId: 'user1',
      type: InsightType.TIME_ALLOCATION,
      title: 'Work-Life Balance Analysis',
      description: 'You spend 65% of tracked time on work activities. Consider allocating more time to personal activities.',
      data: {
        workPercentage: 65,
        personalPercentage: 20,
        healthPercentage: 15
      },
      actionable: true,
      recommendations: [
        'Set boundaries for work hours',
        'Schedule regular personal time',
        'Increase health-related activities to 20%'
      ],
      createdAt: new Date('2024-01-15T18:00:00')
    }
  ];

  const weeklyStats = {
    totalActivities: 42,
    averageProductivity: 7.8,
    averageMood: 4.1,
    averageEnergy: 3.9,
    topCategory: ActivityCategory.WORK,
    improvementAreas: ['Energy Management', 'Work-Life Balance']
  };

  const categoryBreakdown = [
    { category: ActivityCategory.WORK, percentage: 65, hours: 32 },
    { category: ActivityCategory.PERSONAL, percentage: 20, hours: 10 },
    { category: ActivityCategory.EXERCISE, percentage: 10, hours: 5 },
    { category: ActivityCategory.LEARNING, percentage: 5, hours: 2.5 }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">AI Insights</h1>
          <p className="text-secondary-600 mt-1">
            Personalized recommendations based on your activity data
          </p>
        </div>
        <Button icon={<Brain size={16} />}>
          Generate New Insights
        </Button>
      </div>

      {/* Weekly Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <div className="flex items-center">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Activities This Week</p>
              <p className="text-2xl font-bold text-secondary-900">{weeklyStats.totalActivities}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-2 bg-green-50 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Avg Productivity</p>
              <p className="text-2xl font-bold text-secondary-900">{weeklyStats.averageProductivity}/10</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-2 bg-purple-50 rounded-lg">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Avg Mood</p>
              <p className="text-2xl font-bold text-secondary-900">{weeklyStats.averageMood}/5</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-2 bg-orange-50 rounded-lg">
              <Clock className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Avg Energy</p>
              <p className="text-2xl font-bold text-secondary-900">{weeklyStats.averageEnergy}/5</p>
            </div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* AI Insights */}
        <div className="lg:col-span-2 space-y-6">
          <Card title="AI-Generated Insights" subtitle="Personalized recommendations for you">
            <div className="space-y-6">
              {insights.map((insight) => (
                <InsightCard key={insight.id} insight={insight} />
              ))}
            </div>
          </Card>
        </div>

        {/* Category Breakdown */}
        <div className="space-y-6">
          <Card title="Time Allocation" subtitle="How you spend your time">
            <div className="space-y-4">
              {categoryBreakdown.map((item) => (
                <div key={item.category} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{getCategoryIcon(item.category)}</span>
                    <div>
                      <p className="text-sm font-medium text-secondary-900 capitalize">
                        {item.category}
                      </p>
                      <p className="text-xs text-secondary-500">
                        {item.hours}h this week
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-secondary-900">
                      {item.percentage}%
                    </p>
                    <div className="w-16 h-2 bg-secondary-200 rounded-full mt-1">
                      <div 
                        className={`h-full rounded-full ${getCategoryColor(item.category).split(' ')[0]}`}
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card title="Improvement Areas" subtitle="Focus areas for next week">
            <div className="space-y-3">
              {weeklyStats.improvementAreas.map((area, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <Lightbulb className="w-5 h-5 text-yellow-600" />
                  <span className="text-sm font-medium text-yellow-800">{area}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

interface InsightCardProps {
  insight: Insight;
}

const InsightCard: React.FC<InsightCardProps> = ({ insight }) => {
  const getInsightIcon = (type: InsightType) => {
    switch (type) {
      case InsightType.PRODUCTIVITY_PATTERN:
        return <BarChart3 className="w-5 h-5 text-blue-600" />;
      case InsightType.ENERGY_OPTIMIZATION:
        return <TrendingUp className="w-5 h-5 text-green-600" />;
      case InsightType.MOOD_CORRELATION:
        return <Target className="w-5 h-5 text-purple-600" />;
      case InsightType.TIME_ALLOCATION:
        return <PieChart className="w-5 h-5 text-orange-600" />;
      default:
        return <Brain className="w-5 h-5 text-primary-600" />;
    }
  };

  const getInsightColor = (type: InsightType) => {
    switch (type) {
      case InsightType.PRODUCTIVITY_PATTERN:
        return 'bg-blue-50 border-blue-200';
      case InsightType.ENERGY_OPTIMIZATION:
        return 'bg-green-50 border-green-200';
      case InsightType.MOOD_CORRELATION:
        return 'bg-purple-50 border-purple-200';
      case InsightType.TIME_ALLOCATION:
        return 'bg-orange-50 border-orange-200';
      default:
        return 'bg-primary-50 border-primary-200';
    }
  };

  return (
    <div className={`p-4 rounded-lg border ${getInsightColor(insight.type)}`}>
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          {getInsightIcon(insight.type)}
        </div>
        <div className="flex-1">
          <h4 className="font-medium text-secondary-900 mb-1">
            {insight.title}
          </h4>
          <p className="text-sm text-secondary-700 mb-3">
            {insight.description}
          </p>
          
          {insight.actionable && insight.recommendations.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-medium text-secondary-600 uppercase tracking-wide">
                Recommendations
              </p>
              <ul className="space-y-1">
                {insight.recommendations.map((rec, index) => (
                  <li key={index} className="text-sm text-secondary-600 flex items-start">
                    <span className="text-primary-500 mr-2">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          <p className="text-xs text-primary-800 mt-3">
            Generated {formatDate(insight.createdAt)}
          </p>
        </div>
      </div>
    </div>
  );
};
