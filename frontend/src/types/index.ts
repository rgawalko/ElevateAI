// User types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  createdAt: Date;
  updatedAt: Date;
}

// Activity types
export interface Activity {
  id: string;
  userId: string;
  title: string;
  description?: string;
  category: ActivityCategory;
  duration: number; // in minutes
  startTime: Date;
  endTime: Date;
  mood?: MoodLevel;
  energyLevel?: EnergyLevel;
  productivityScore?: number; // 1-10
  tags: string[];
  createdAt: Date;
  updatedAt: Date;
}

export enum ActivityCategory {
  WORK = 'work',
  EXERCISE = 'exercise',
  LEARNING = 'learning',
  SOCIAL = 'social',
  PERSONAL = 'personal',
  HEALTH = 'health',
  ENTERTAINMENT = 'entertainment',
  COMMUTE = 'commute',
  SLEEP = 'sleep',
  MEALS = 'meals',
}

export enum MoodLevel {
  VERY_LOW = 1,
  LOW = 2,
  NEUTRAL = 3,
  GOOD = 4,
  EXCELLENT = 5,
}

export enum EnergyLevel {
  VERY_LOW = 1,
  LOW = 2,
  MODERATE = 3,
  HIGH = 4,
  VERY_HIGH = 5,
}

// Schedule types
export interface Schedule {
  id: string;
  userId: string;
  title: string;
  description?: string;
  date: Date;
  tasks: ScheduleTask[];
  isGenerated: boolean; // true if AI-generated
  createdAt: Date;
  updatedAt: Date;
}

export interface ScheduleTask {
  id: string;
  title: string;
  description?: string;
  startTime: Date;
  endTime: Date;
  category: ActivityCategory;
  priority: Priority;
  isCompleted: boolean;
  estimatedDuration: number; // in minutes
  actualDuration?: number; // in minutes
}

export enum Priority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  URGENT = 'urgent',
}

// Insights types
export interface Insight {
  id: string;
  userId: string;
  type: InsightType;
  title: string;
  description: string;
  data: Record<string, any>;
  actionable: boolean;
  recommendations: string[];
  createdAt: Date;
}

export enum InsightType {
  PRODUCTIVITY_PATTERN = 'productivity_pattern',
  MOOD_CORRELATION = 'mood_correlation',
  ENERGY_OPTIMIZATION = 'energy_optimization',
  TIME_ALLOCATION = 'time_allocation',
  WELLNESS_TREND = 'wellness_trend',
  GOAL_PROGRESS = 'goal_progress',
}

// Goal types
export interface Goal {
  id: string;
  userId: string;
  title: string;
  description?: string;
  category: GoalCategory;
  priority?: Priority;
  targetValue: number;
  currentValue: number;
  unit: string;
  deadline?: Date;
  targetDate?: Date; // Alias for deadline for backward compatibility
  isCompleted: boolean;
  progress: number; // Progress percentage (0-100)
  status: 'not_started' | 'in_progress' | 'completed' | 'paused';
  createdAt: Date;
  updatedAt: Date;
}

export enum GoalCategory {
  PRODUCTIVITY = 'productivity',
  HEALTH = 'health',
  LEARNING = 'learning',
  PERSONAL = 'personal',
  PROFESSIONAL = 'professional',
  FINANCIAL = 'financial',
  CAREER = 'career',
  SOCIAL = 'social',
}

// Analytics types
export interface Analytics {
  userId: string;
  period: AnalyticsPeriod;
  data: {
    totalActivities: number;
    averageProductivity: number;
    averageMood: number;
    averageEnergy: number;
    categoryBreakdown: Record<ActivityCategory, number>;
    moodTrend: Array<{ date: Date; mood: number }>;
    productivityTrend: Array<{ date: Date; productivity: number }>;
    energyTrend: Array<{ date: Date; energy: number }>;
  };
  generatedAt: Date;
}

export enum AnalyticsPeriod {
  DAILY = 'daily',
  WEEKLY = 'weekly',
  MONTHLY = 'monthly',
  YEARLY = 'yearly',
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// Re-export form types
export type { ActivityFormData } from './forms';

export interface ScheduleFormData {
  title: string;
  description?: string;
  date: Date;
  preferences: {
    workHours: { start: string; end: string };
    breakDuration: number;
    priorities: ActivityCategory[];
  };
}

// Component props types
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

// Re-export schedule generation types
export * from './scheduleGeneration';
