// API Services
export {
  apiClient,
  authService,
  activityService,
  scheduleService,
  insightService,
  goalService,
  analyticsService,
  dataService,
  handleApiError
} from './api';

// Mock Data
export {
  mockUser,
  mockActivities,
  mockSchedules,
  mockInsights,
  mockGoals,
  mockDelay,
  shouldSimulateError,
  generateMockActivity,
  generateMockInsight,
  generateMockSchedule
} from './mockData';
