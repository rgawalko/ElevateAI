import type {
  User,
  Activity,
  Schedule,
  Insight,
  Goal
} from '../types';
import {
  ActivityCategory,
  MoodLevel,
  EnergyLevel,
  Priority,
  InsightType,
  GoalCategory
} from '../types';
import type {
  ScheduleGenerationRequest,
  ScheduleGenerationResponse,
  GeneratedSchedule,
  ScheduledActivity,
  ScheduleBreak
} from '../types/scheduleGeneration';

// Mock User Data
export const mockUser: User = {
  id: 'user1',
  email: 'john.doe@example.com',
  name: 'John Doe',
  avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
  createdAt: new Date('2024-01-01T00:00:00Z'),
  updatedAt: new Date('2024-01-15T12:00:00Z')
};

// Mock Activities Data
export const mockActivities: Activity[] = [
  {
    id: '1',
    userId: 'user1',
    title: 'Morning Workout',
    description: 'Cardio and strength training session at the gym',
    category: ActivityCategory.EXERCISE,
    duration: 60,
    startTime: new Date('2024-01-15T07:00:00Z'),
    endTime: new Date('2024-01-15T08:00:00Z'),
    mood: MoodLevel.GOOD,
    energyLevel: EnergyLevel.HIGH,
    productivityScore: 8,
    tags: ['fitness', 'morning', 'cardio', 'strength'],
    createdAt: new Date('2024-01-15T08:00:00Z'),
    updatedAt: new Date('2024-01-15T08:00:00Z')
  },
  {
    id: '2',
    userId: 'user1',
    title: 'Project Planning Meeting',
    description: 'Quarterly planning session with the development team',
    category: ActivityCategory.WORK,
    duration: 90,
    startTime: new Date('2024-01-15T09:00:00Z'),
    endTime: new Date('2024-01-15T10:30:00Z'),
    mood: MoodLevel.NEUTRAL,
    energyLevel: EnergyLevel.MODERATE,
    productivityScore: 7,
    tags: ['meeting', 'planning', 'team', 'quarterly'],
    createdAt: new Date('2024-01-15T10:30:00Z'),
    updatedAt: new Date('2024-01-15T10:30:00Z')
  },
  {
    id: '3',
    userId: 'user1',
    title: 'Lunch with Colleagues',
    description: 'Team lunch at the new Italian restaurant downtown',
    category: ActivityCategory.SOCIAL,
    duration: 45,
    startTime: new Date('2024-01-15T12:00:00Z'),
    endTime: new Date('2024-01-15T12:45:00Z'),
    mood: MoodLevel.GOOD,
    energyLevel: EnergyLevel.MODERATE,
    tags: ['lunch', 'team', 'social', 'italian'],
    createdAt: new Date('2024-01-15T12:45:00Z'),
    updatedAt: new Date('2024-01-15T12:45:00Z')
  },
  {
    id: '4',
    userId: 'user1',
    title: 'Code Review Session',
    description: 'Reviewing pull requests for the new authentication feature',
    category: ActivityCategory.WORK,
    duration: 30,
    startTime: new Date('2024-01-15T14:00:00Z'),
    endTime: new Date('2024-01-15T14:30:00Z'),
    mood: MoodLevel.GOOD,
    energyLevel: EnergyLevel.HIGH,
    productivityScore: 9,
    tags: ['coding', 'review', 'development', 'authentication'],
    createdAt: new Date('2024-01-15T14:30:00Z'),
    updatedAt: new Date('2024-01-15T14:30:00Z')
  },
  {
    id: '5',
    userId: 'user1',
    title: 'React Hooks Deep Dive',
    description: 'Online course on advanced React patterns and custom hooks',
    category: ActivityCategory.LEARNING,
    duration: 120,
    startTime: new Date('2024-01-15T19:00:00Z'),
    endTime: new Date('2024-01-15T21:00:00Z'),
    mood: MoodLevel.EXCELLENT,
    energyLevel: EnergyLevel.HIGH,
    productivityScore: 8,
    tags: ['learning', 'react', 'programming', 'hooks'],
    createdAt: new Date('2024-01-15T21:00:00Z'),
    updatedAt: new Date('2024-01-15T21:00:00Z')
  }
];

// Mock Schedules Data
export const mockSchedules: Schedule[] = [
  {
    id: '1',
    userId: 'user1',
    title: 'Productive Monday',
    description: 'AI-optimized schedule for maximum productivity',
    date: new Date('2024-01-15T00:00:00Z'),
    isGenerated: true,
    tasks: [
      {
        id: '1',
        title: 'Morning Workout',
        description: 'Cardio and strength training',
        startTime: new Date('2024-01-15T07:00:00Z'),
        endTime: new Date('2024-01-15T08:00:00Z'),
        category: ActivityCategory.EXERCISE,
        priority: Priority.HIGH,
        isCompleted: true,
        estimatedDuration: 60,
        actualDuration: 60
      },
      {
        id: '2',
        title: 'Deep Work Session',
        description: 'Focus on the new feature development',
        startTime: new Date('2024-01-15T09:00:00Z'),
        endTime: new Date('2024-01-15T11:00:00Z'),
        category: ActivityCategory.WORK,
        priority: Priority.HIGH,
        isCompleted: true,
        estimatedDuration: 120,
        actualDuration: 115
      },
      {
        id: '3',
        title: 'Team Meeting',
        description: 'Weekly sync with the development team',
        startTime: new Date('2024-01-15T11:30:00Z'),
        endTime: new Date('2024-01-15T12:30:00Z'),
        category: ActivityCategory.WORK,
        priority: Priority.MEDIUM,
        isCompleted: true,
        estimatedDuration: 60,
        actualDuration: 65
      }
    ],
    createdAt: new Date('2024-01-14T20:00:00Z'),
    updatedAt: new Date('2024-01-15T15:00:00Z')
  }
];

// Mock Insights Data
export const mockInsights: Insight[] = [
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
    createdAt: new Date('2024-01-15T10:00:00Z')
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
    createdAt: new Date('2024-01-15T15:30:00Z')
  }
];

// Mock Goals Data
export const mockGoals: Goal[] = [
  {
    id: '1',
    userId: 'user1',
    title: 'Exercise 5 times per week',
    description: 'Maintain a consistent workout routine for better health',
    category: GoalCategory.HEALTH,
    targetValue: 5,
    currentValue: 3,
    unit: 'workouts',
    deadline: new Date('2024-02-01T00:00:00Z'),
    isCompleted: false,
    createdAt: new Date('2024-01-01T00:00:00Z'),
    updatedAt: new Date('2024-01-15T12:00:00Z')
  },
  {
    id: '2',
    userId: 'user1',
    title: 'Complete React Course',
    description: 'Finish the advanced React patterns course',
    category: GoalCategory.LEARNING,
    targetValue: 100,
    currentValue: 65,
    unit: 'percent',
    deadline: new Date('2024-01-31T00:00:00Z'),
    isCompleted: false,
    createdAt: new Date('2024-01-01T00:00:00Z'),
    updatedAt: new Date('2024-01-15T21:00:00Z')
  }
];

// Mock API delay function
export const mockDelay = (ms: number = 500): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Mock error simulation
export const shouldSimulateError = (errorRate: number = 0.1): boolean => {
  return Math.random() < errorRate;
};

// Mock data generators
export const generateMockActivity = (overrides: Partial<Activity> = {}): Activity => {
  const baseActivity: Activity = {
    id: Math.random().toString(36).substr(2, 9),
    userId: 'user1',
    title: 'Sample Activity',
    category: ActivityCategory.WORK,
    duration: 60,
    startTime: new Date(),
    endTime: new Date(Date.now() + 60 * 60 * 1000),
    tags: [],
    createdAt: new Date(),
    updatedAt: new Date()
  };

  return { ...baseActivity, ...overrides };
};

export const generateMockInsight = (overrides: Partial<Insight> = {}): Insight => {
  const baseInsight: Insight = {
    id: Math.random().toString(36).substr(2, 9),
    userId: 'user1',
    type: InsightType.PRODUCTIVITY_PATTERN,
    title: 'Sample Insight',
    description: 'This is a sample insight generated for testing purposes.',
    data: {},
    actionable: true,
    recommendations: ['Sample recommendation'],
    createdAt: new Date()
  };

  return { ...baseInsight, ...overrides };
};

// Mock Schedule Generation
export const generateMockSchedule = async (request: ScheduleGenerationRequest): Promise<ScheduleGenerationResponse> => {
  // Simulate API delay
  await mockDelay(2000);

  // Simulate occasional errors for testing
  if (shouldSimulateError(0.1)) {
    return {
      success: false,
      error: 'Mock API error: Unable to generate schedule at this time'
    };
  }

  // Sort activities by priority (1 = highest priority)
  const sortedActivities = [...request.activities].sort((a, b) => a.priority - b.priority);

  // Parse wake up time
  const [wakeHour, wakeMinute] = request.wakeUpTime.split(':').map(Number);
  const workStartTime = request.constraints.workStartTime ||
    `${String(wakeHour + 1).padStart(2, '0')}:${String(wakeMinute).padStart(2, '0')}`;

  let currentTime = workStartTime;
  const scheduledActivities: ScheduledActivity[] = [];
  const breaks: ScheduleBreak[] = [];
  const unscheduledActivities = [];

  // Helper function to add minutes to time string
  const addMinutes = (timeStr: string, minutes: number): string => {
    const [hours, mins] = timeStr.split(':').map(Number);
    const totalMinutes = hours * 60 + mins + minutes;
    const newHours = Math.floor(totalMinutes / 60);
    const newMins = totalMinutes % 60;
    return `${String(newHours).padStart(2, '0')}:${String(newMins).padStart(2, '0')}`;
  };

  // Helper function to check if time is within window
  const isWithinTimeWindow = (time: string, window?: [string, string]): boolean => {
    if (!window) return true;
    const [timeHour, timeMin] = time.split(':').map(Number);
    const [startHour, startMin] = window[0].split(':').map(Number);
    const [endHour, endMin] = window[1].split(':').map(Number);

    const timeMinutes = timeHour * 60 + timeMin;
    const startMinutes = startHour * 60 + startMin;
    const endMinutes = endHour * 60 + endMin;

    return timeMinutes >= startMinutes && timeMinutes <= endMinutes;
  };

  let consecutiveWorkTime = 0;
  let lunchScheduled = false;

  for (const activity of sortedActivities) {
    // Check if we need a lunch break
    if (request.constraints.lunchBreak && !lunchScheduled) {
      const lunchWindow = request.constraints.lunchBreakTimeWindow || ['12:00', '14:00'];
      if (isWithinTimeWindow(currentTime, lunchWindow)) {
        const lunchDuration = request.constraints.lunchBreakDuration || 60;
        breaks.push({
          type: 'lunch',
          startTime: currentTime,
          endTime: addMinutes(currentTime, lunchDuration),
          durationMinutes: lunchDuration
        });
        currentTime = addMinutes(currentTime, lunchDuration);
        lunchScheduled = true;
        consecutiveWorkTime = 0;
      }
    }

    // Check consecutive work hours limit
    if (consecutiveWorkTime >= request.constraints.maxConsecutiveWorkHours * 60) {
      const breakDuration = 30; // Long break
      breaks.push({
        type: 'long',
        startTime: currentTime,
        endTime: addMinutes(currentTime, breakDuration),
        durationMinutes: breakDuration
      });
      currentTime = addMinutes(currentTime, breakDuration);
      consecutiveWorkTime = 0;
    }

    // Check if activity fits in time window
    if (activity.timeWindow && !isWithinTimeWindow(currentTime, activity.timeWindow)) {
      // Try to schedule at the start of the time window
      if (activity.timeWindow[0] > currentTime) {
        currentTime = activity.timeWindow[0];
      } else {
        // Can't fit in time window, add to unscheduled
        unscheduledActivities.push(activity);
        continue;
      }
    }

    // Schedule the activity
    const endTime = addMinutes(currentTime, activity.durationMinutes);
    scheduledActivities.push({
      name: activity.name,
      startTime: currentTime,
      endTime: endTime,
      durationMinutes: activity.durationMinutes,
      priority: activity.priority,
      category: activity.category,
      description: activity.description
    });

    currentTime = endTime;
    consecutiveWorkTime += activity.durationMinutes;

    // Add short break between activities
    if (request.constraints.breakDuration && request.constraints.breakDuration > 0) {
      const breakDuration = request.constraints.breakDuration;
      breaks.push({
        type: 'short',
        startTime: currentTime,
        endTime: addMinutes(currentTime, breakDuration),
        durationMinutes: breakDuration
      });
      currentTime = addMinutes(currentTime, breakDuration);
    }
  }

  const totalScheduledTime = scheduledActivities.reduce((sum, act) => sum + act.durationMinutes, 0);
  const totalBreakTime = breaks.reduce((sum, br) => sum + br.durationMinutes, 0);

  const generatedSchedule: GeneratedSchedule = {
    date: request.date,
    totalDuration: totalScheduledTime + totalBreakTime,
    scheduledActivities,
    unscheduledActivities,
    breaks,
    summary: {
      totalWorkTime: totalScheduledTime,
      totalBreakTime: totalBreakTime,
      totalFreeTime: Math.max(0, 8 * 60 - totalScheduledTime - totalBreakTime), // Assuming 8-hour workday
      productivityScore: Math.round(85 + Math.random() * 15), // Random score between 85-100
      balanceScore: Math.round(70 + Math.random() * 30) // Random score between 70-100
    }
  };

  return {
    success: true,
    schedule: generatedSchedule,
    warnings: unscheduledActivities.length > 0 ?
      [`${unscheduledActivities.length} activities could not be scheduled due to time constraints`] :
      undefined
  };
};
