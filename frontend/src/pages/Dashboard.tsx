import React, { useState, useEffect } from 'react';
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
import { HomeService, type DashboardData } from '../services';

// Helper function to get time-based greeting
const getTimeBasedGreeting = (): string => {
  const hour = new Date().getHours();

  if (hour >= 5 && hour < 12) {
    return 'Good morning';
  } else if (hour >= 12 && hour < 17) {
    return 'Good afternoon';
  } else if (hour >= 17 && hour < 22) {
    return 'Good evening';
  } else {
    return 'Good night';
  }
};

// Helper function to get appropriate emoji for time of day
const getTimeEmoji = (): string => {
  const hour = new Date().getHours();

  if (hour >= 5 && hour < 12) {
    return '🌅'; // sunrise
  } else if (hour >= 12 && hour < 17) {
    return '☀️'; // sun
  } else if (hour >= 17 && hour < 22) {
    return '🌆'; // sunset
  } else {
    return '🌙'; // moon
  }
};

// Helper function to get greeting for a specific hour (for demo purposes)
const getGreetingForHour = (hour: number): { greeting: string; emoji: string } => {
  if (hour >= 5 && hour < 12) {
    return { greeting: 'Good morning', emoji: '🌅' };
  } else if (hour >= 12 && hour < 17) {
    return { greeting: 'Good afternoon', emoji: '☀️' };
  } else if (hour >= 17 && hour < 22) {
    return { greeting: 'Good evening', emoji: '🌆' };
  } else {
    return { greeting: 'Good night', emoji: '🌙' };
  }
};

export const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch dashboard data on component mount
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const data = await HomeService.getDashboardData();
        setDashboardData(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err);
        setError('Failed to load dashboard data');
        // Keep existing mock data as fallback
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Use real data from API or fallback to mock data
  const todayStats = {
    activitiesLogged: dashboardData?.stats?.activities_this_week || 0, // Changed from activities_today to activities_this_week
    totalTime: dashboardData?.stats?.time_tracked_today || 0, // minutes
    averageMood: dashboardData?.stats?.avg_mood || 0,
    averageEnergy: dashboardData?.stats?.avg_energy || 0,
    productivityScore: Math.round((dashboardData?.stats?.productivity_score || 0) * 10) // Convert to percentage
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
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight" style={{color: '#026670'}}>
            {getTimeBasedGreeting()}, {loading ? 'User' : (dashboardData?.user?.name || 'User')}! {getTimeEmoji()}
          </h1>
          <p className="mt-2 text-lg font-medium" style={{color: 'rgba(2, 102, 112, 0.7)'}}>
            {formatDate(new Date())} • Let's make today productive
          </p>

        </div>
        <Button icon={<Plus size={18} />} size="lg">
          Log Activity
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatCard
          title="Activities This Week"
          value={todayStats.activitiesLogged}
          icon={<Activity size={20} />}
          color="text-primary-600"
          bgColor="bg-primary-50"
        />
        <StatCard
          title="Time Tracked"
          value={`${Math.floor(todayStats.totalTime / 60)}h ${todayStats.totalTime % 60}m`}
          icon={<Clock size={20} />}
          color="text-success-600"
          bgColor="bg-success-50"
        />
        <StatCard
          title="Avg Mood"
          value={`${todayStats.averageMood}/5`}
          icon={<TrendingUp size={20} />}
          color="text-accent-700"
          bgColor="bg-accent-50"
        />
        <StatCard
          title="Energy Level"
          value={`${todayStats.averageEnergy}/5`}
          icon={<Target size={20} />}
          color="text-warning-700"
          bgColor="bg-warning-50"
        />
        <StatCard
          title="Productivity"
          value={`${todayStats.productivityScore}%`}
          icon={<BarChart3 size={20} />}
          color="text-secondary-700"
          bgColor="bg-secondary-100"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
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
            <div className="space-y-3">
              {recentActivities.map((activity) => (
                <div key={activity.id} className="flex items-center space-x-4 p-4 bg-gradient-to-r from-secondary-50 to-white rounded-xl border border-secondary-200/50 hover:shadow-md hover:scale-[1.01] transition-all duration-200 group">
                  <div className="flex-shrink-0">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl flex items-center justify-center shadow-sm group-hover:shadow-md transition-all duration-200">
                      <span className="text-xl">{getCategoryIcon(activity.category)}</span>
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold truncate" style={{color: '#026670'}}>
                      {activity.title}
                    </h4>
                    <div className="flex items-center space-x-3 mt-2">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold shadow-sm ${getCategoryColor(activity.category)}`}>
                        {activity.category}
                      </span>
                      <span className="text-xs font-medium bg-secondary-100 px-2 py-1 rounded-full" style={{color: '#026670'}}>
                        {activity.duration}m
                      </span>
                    </div>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <p className="text-sm font-semibold" style={{color: '#026670'}}>
                      {formatTime(activity.startTime)}
                    </p>
                    <div className="flex items-center space-x-2 mt-2">
                      <span className="text-sm bg-yellow-100 px-2 py-1 rounded-full">😊</span>
                      <span className="text-sm bg-blue-100 px-2 py-1 rounded-full">⚡</span>
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
                    <h4 className="text-sm font-medium truncate" style={{color: '#026670'}}>
                      {task.title}
                    </h4>
                    <p className="text-xs" style={{color: 'rgba(2, 102, 112, 0.6)'}}>
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl border border-primary-200/50 shadow-sm hover:shadow-md transition-all duration-200 hover:scale-[1.02]">
            <h4 className="font-bold mb-3 text-lg" style={{color: '#026670'}}>🎯 Productivity Peak</h4>
            <p className="text-sm font-medium leading-relaxed" style={{color: '#026670'}}>
              Your most productive hours are between 9-11 AM. Consider scheduling important tasks during this time.
            </p>
          </div>
          <div className="p-6 bg-gradient-to-br from-accent-50 to-accent-100 rounded-xl border border-accent-200/50 shadow-sm hover:shadow-md transition-all duration-200 hover:scale-[1.02]">
            <h4 className="font-bold mb-3 text-lg" style={{color: '#026670'}}>💪 Energy Optimization</h4>
            <p className="text-sm font-medium leading-relaxed" style={{color: '#026670'}}>
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
    <Card padding="md" hover className="group">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className={`p-3 rounded-xl ${bgColor} shadow-sm group-hover:shadow-md transition-all duration-200`}>
            <div className={`${color} transition-transform duration-200 group-hover:scale-110`}>
              {icon}
            </div>
          </div>
          <div className="ml-4">
            <p className="text-sm font-semibold uppercase tracking-wide" style={{color: '#026670'}}>{title}</p>
            <p className="text-2xl font-bold mt-1" style={{color: '#026670'}}>{value}</p>
          </div>
        </div>
        <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="w-2 h-8 bg-gradient-to-b from-primary-400 to-primary-600 rounded-full"></div>
        </div>
      </div>
    </Card>
  );
};
