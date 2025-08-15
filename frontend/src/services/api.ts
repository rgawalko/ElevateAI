import type {
  User,
  Activity,
  Schedule,
  Insight,
  Goal,
  Analytics,
  ApiResponse,
  PaginatedResponse,
  ActivityFormData,
  ScheduleFormData
} from '../types';
import type { ScheduleGenerationRequest, ScheduleGenerationResponse } from '../types/scheduleGeneration';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const API_TIMEOUT = 10000; // 10 seconds

// API Client Class
class ApiClient {
  private baseURL: string;
  private timeout: number;

  constructor(baseURL: string = API_BASE_URL, timeout: number = API_TIMEOUT) {
    this.baseURL = baseURL;
    this.timeout = timeout;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('elevate_auth_token');
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Generic HTTP methods
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint);
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<ApiResponse<{ user: User; token: string }>> {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(userData: { name: string; email: string; password: string }): Promise<ApiResponse<{ user: User; token: string }>> {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async logout(): Promise<ApiResponse<null>> {
    return this.request('/auth/logout', {
      method: 'POST',
    });
  }

  // User endpoints
  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.request('/users/me');
  }

  async updateUser(userData: Partial<User>): Promise<ApiResponse<User>> {
    return this.request('/users/me', {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  // Activity endpoints
  async getActivities(params?: {
    page?: number;
    limit?: number;
    category?: string;
    startDate?: string;
    endDate?: string;
  }): Promise<ApiResponse<PaginatedResponse<Activity>>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const endpoint = `/activities${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  async getActivity(id: string): Promise<ApiResponse<Activity>> {
    return this.request(`/activities/${id}`);
  }

  async createActivity(activityData: ActivityFormData): Promise<ApiResponse<Activity>> {
    return this.request('/activities', {
      method: 'POST',
      body: JSON.stringify(activityData),
    });
  }

  async updateActivity(id: string, activityData: Partial<ActivityFormData>): Promise<ApiResponse<Activity>> {
    return this.request(`/activities/${id}`, {
      method: 'PUT',
      body: JSON.stringify(activityData),
    });
  }

  async deleteActivity(id: string): Promise<ApiResponse<null>> {
    return this.request(`/activities/${id}`, {
      method: 'DELETE',
    });
  }

  // Schedule endpoints
  async getSchedules(params?: {
    startDate?: string;
    endDate?: string;
  }): Promise<ApiResponse<Schedule[]>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const endpoint = `/schedules${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  async getSchedule(id: string): Promise<ApiResponse<Schedule>> {
    return this.request(`/schedules/${id}`);
  }

  async createSchedule(scheduleData: ScheduleFormData): Promise<ApiResponse<Schedule>> {
    return this.request('/schedules', {
      method: 'POST',
      body: JSON.stringify(scheduleData),
    });
  }

  async generateSchedule(preferences: ScheduleFormData): Promise<ApiResponse<Schedule>> {
    return this.request('/schedules/generate', {
      method: 'POST',
      body: JSON.stringify(preferences),
    });
  }

  async generateAISchedule(request: ScheduleGenerationRequest): Promise<ScheduleGenerationResponse> {
    // Use mock data in development
    if (import.meta.env.VITE_ENABLE_MOCK_DATA === 'true') {
      const { generateMockSchedule } = await import('./mockData');
      return generateMockSchedule(request);
    }

    try {
      const response = await this.request<ScheduleGenerationResponse>('/ai/generate-schedule', {
        method: 'POST',
        body: JSON.stringify(request),
      });
      return response.data || { success: false, error: 'No data received' };
    } catch (error) {
      console.error('AI Schedule generation failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to generate schedule'
      };
    }
  }

  async updateSchedule(id: string, scheduleData: Partial<ScheduleFormData>): Promise<ApiResponse<Schedule>> {
    return this.request(`/schedules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(scheduleData),
    });
  }

  async deleteSchedule(id: string): Promise<ApiResponse<null>> {
    return this.request(`/schedules/${id}`, {
      method: 'DELETE',
    });
  }

  // Insights endpoints
  async getInsights(): Promise<ApiResponse<Insight[]>> {
    return this.request('/insights');
  }

  async generateInsights(): Promise<ApiResponse<Insight[]>> {
    return this.request('/insights/generate', {
      method: 'POST',
    });
  }

  // Goals endpoints
  async getGoals(): Promise<ApiResponse<Goal[]>> {
    return this.request('/goals');
  }

  async createGoal(goalData: Omit<Goal, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<ApiResponse<Goal>> {
    return this.request('/goals', {
      method: 'POST',
      body: JSON.stringify(goalData),
    });
  }

  async updateGoal(id: string, goalData: Partial<Goal>): Promise<ApiResponse<Goal>> {
    return this.request(`/goals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(goalData),
    });
  }

  async deleteGoal(id: string): Promise<ApiResponse<null>> {
    return this.request(`/goals/${id}`, {
      method: 'DELETE',
    });
  }

  // Analytics endpoints
  async getAnalytics(period: string): Promise<ApiResponse<Analytics>> {
    return this.request(`/analytics?period=${period}`);
  }

  // Export/Import endpoints
  async exportData(format: 'json' | 'csv'): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/export?format=${format}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('elevate_auth_token')}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Export failed');
    }
    
    return response.blob();
  }

  async importData(file: File): Promise<ApiResponse<{ imported: number; errors: string[] }>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request('/import', {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData, let browser set it
        Authorization: `Bearer ${localStorage.getItem('elevate_auth_token')}`,
      },
    });
  }
}

// Create and export API client instance
export const apiClient = new ApiClient();

// Export individual service functions for easier use
export const authService = {
  login: apiClient.login.bind(apiClient),
  register: apiClient.register.bind(apiClient),
  logout: apiClient.logout.bind(apiClient),
  getCurrentUser: apiClient.getCurrentUser.bind(apiClient),
};

export const activityService = {
  getActivities: apiClient.getActivities.bind(apiClient),
  getActivity: apiClient.getActivity.bind(apiClient),
  createActivity: apiClient.createActivity.bind(apiClient),
  updateActivity: apiClient.updateActivity.bind(apiClient),
  deleteActivity: apiClient.deleteActivity.bind(apiClient),
};

export const scheduleService = {
  getSchedules: apiClient.getSchedules.bind(apiClient),
  getSchedule: apiClient.getSchedule.bind(apiClient),
  createSchedule: apiClient.createSchedule.bind(apiClient),
  generateSchedule: apiClient.generateSchedule.bind(apiClient),
  generateAISchedule: apiClient.generateAISchedule.bind(apiClient),
  updateSchedule: apiClient.updateSchedule.bind(apiClient),
  deleteSchedule: apiClient.deleteSchedule.bind(apiClient),
};

export const insightService = {
  getInsights: apiClient.getInsights.bind(apiClient),
  generateInsights: apiClient.generateInsights.bind(apiClient),
};

export const goalService = {
  getGoals: apiClient.getGoals.bind(apiClient),
  createGoal: apiClient.createGoal.bind(apiClient),
  updateGoal: apiClient.updateGoal.bind(apiClient),
  deleteGoal: apiClient.deleteGoal.bind(apiClient),
};

export const analyticsService = {
  getAnalytics: apiClient.getAnalytics.bind(apiClient),
};

export const dataService = {
  exportData: apiClient.exportData.bind(apiClient),
  importData: apiClient.importData.bind(apiClient),
};

// Error handling utility
export const handleApiError = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return 'An unexpected error occurred';
};
