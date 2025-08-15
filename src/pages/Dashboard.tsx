import React from 'react';
import { 
  Plus, 
  TrendingUp, 
  Clock, 
  Target, 
  Brain,
  Calendar,
  Activity,
  BarChart3
} from 'lucide-react';
import { Card, Button, IconButton } from '../components';
import { formatDate, formatTime, getCategoryColor, getCategoryIcon } from '../utils';
import { ActivityCategory, MoodLevel, EnergyLevel } from '../types';

export const Dashboard: React.FC = () => {
  // Mock data - in a real app, this would come from API/state management
  const todayStats = {
    activitiesLogged: 8,
    totalTime: 480, // minutes
    averageMood: 4.2,
    averageEnergy: 3.8,
    productivityScore: 85
  };

  const recentActivities = [
    {
      id: '1',
      title: 'Morning Workout',
      category: ActivityCategory.EXERCISE,
      duration: 45,
      startTime: new Date('2024-01-15T07:00:00'),
      mood: MoodLevel.GOOD,
      energyLevel: EnergyLevel.HIGH
    },
    {
      id: '2',
      title: 'Project Planning',
      category: ActivityCategory.WORK,
      duration: 90,
      startTime: new Date('2024-01-15T09:00:00'),
      mood: MoodLevel.GOOD,
      energyLevel: EnergyLevel.MODERATE
    },
    {
      id: '3',
      title: 'Lunch Break',
      category: ActivityCategory.MEALS,
      duration: 30,
      startTime: new Date('2024-01-15T12:00:00'),
      mood: MoodLevel.NEUTRAL,
      energyLevel: EnergyLevel.MODERATE
    }
  ];

  const upcomingTasks = [
    {
      id: '1',
      title: 'Team Meeting',
      time: '2:00 PM',
      category: ActivityCategory.WORK,
      priority: 'high'
    },
    {
      id: '2',
      title: 'Code Review',
      time: '3:30 PM',
      category: ActivityCategory.WORK,
      priority: 'medium'
    },
    {
      id: '3',
      title: 'Gym Session',
      time: '6:00 PM',
      category: ActivityCategory.EXERCISE,
      priority: 'low'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">
            Good morning, John! 👋
          </h1>
          <p className="text-secondary-600 mt-1">
            {formatDate(new Date())} • Let's make today productive
          </p>
        </div>
        <Button icon={<Plus size={16} />}>
          Log Activity
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatCard
          title="Activities"
          value={todayStats.activitiesLogged}
          icon={<Activity size={20} />}
          color="text-blue-600"
          bgColor="bg-blue-50"
        />
        <StatCard
          title="Time Tracked"
          value={`${Math.floor(todayStats.totalTime / 60)}h ${todayStats.totalTime % 60}m`}
          icon={<Clock size={20} />}
          color="text-green-600"
          bgColor="bg-green-50"
        />
        <StatCard
          title="Avg Mood"
          value={`${todayStats.averageMood}/5`}
          icon={<TrendingUp size={20} />}
          color="text-purple-600"
          bgColor="bg-purple-50"
        />
        <StatCard
          title="Energy Level"
          value={`${todayStats.averageEnergy}/5`}
          icon={<Target size={20} />}
          color="text-orange-600"
          bgColor="bg-orange-50"
        />
        <StatCard
          title="Productivity"
          value={`${todayStats.productivityScore}%`}
          icon={<BarChart3 size={20} />}
          color="text-primary-600"
          bgColor="bg-primary-50"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <div className="lg:col-span-2">
          <Card 
            title="Recent Activities" 
            subtitle="Your latest logged activities"
            action={
              <Button variant="outline" size="sm">
                View All
              </Button>
            }
          >
            <div className="space-y-4">
              {recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-center space-x-4 p-3 bg-secondary-50 rounded-lg">
                  <div className="flex-shrink-0">
                    <span className="text-2xl">{getCategoryIcon(activity.category)}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-secondary-900 truncate">
                      {activity.title}
                    </h4>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(activity.category)}`}>
                        {activity.category}
                      </span>
                      <span className="text-xs text-secondary-500">
                        {activity.duration}m
                      </span>
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <p className="text-sm text-secondary-900">
                      {formatTime(activity.startTime)}
                    </p>
                    <div className="flex items-center space-x-1 mt-1">
                      <span className="text-xs">😊</span>
                      <span className="text-xs">⚡</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Upcoming Tasks */}
        <div>
          <Card 
            title="Upcoming Tasks" 
            subtitle="Your schedule for today"
            action={
              <IconButton variant="outline" size="sm" icon={<Calendar size={16} />} />
            }
          >
            <div className="space-y-3">
              {upcomingTasks.map((task) => (
                <div key={task.id} className="flex items-center space-x-3 p-2 hover:bg-secondary-50 rounded-lg transition-colors">
                  <div className="flex-shrink-0">
                    <span className="text-lg">{getCategoryIcon(task.category)}</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-secondary-900 truncate">
                      {task.title}
                    </h4>
                    <p className="text-xs text-secondary-500">
                      {task.time}
                    </p>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${
                    task.priority === 'high' ? 'bg-red-400' :
                    task.priority === 'medium' ? 'bg-yellow-400' : 'bg-green-400'
                  }`} />
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* AI Insights */}
      <Card 
        title="AI Insights" 
        subtitle="Personalized recommendations based on your data"
        action={
          <Button variant="outline" size="sm" icon={<Brain size={16} />}>
            View All Insights
          </Button>
        }
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h4 className="font-medium text-blue-900 mb-2">🎯 Productivity Peak</h4>
            <p className="text-sm text-blue-700">
              Your most productive hours are between 9-11 AM. Consider scheduling important tasks during this time.
            </p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="font-medium text-green-900 mb-2">💪 Energy Optimization</h4>
            <p className="text-sm text-green-700">
              Taking a 15-minute walk after lunch could boost your afternoon energy levels by 20%.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, bgColor }) => {
  return (
    <Card padding="md" hover>
      <div className="flex items-center">
        <div className={`p-2 rounded-lg ${bgColor}`}>
          <div className={color}>
            {icon}
          </div>
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-secondary-600">{title}</p>
          <p className="text-2xl font-bold text-secondary-900">{value}</p>
        </div>
      </div>
    </Card>
  );
};
