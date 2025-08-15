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

// Home Page Service
export { HomeService } from './homeService';

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
