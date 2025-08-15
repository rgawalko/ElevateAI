/**
 * Goals Service - API client for goals management
 */

import { apiClient } from './api';
import type { Goal } from '../types';

export interface GoalCreateData {
  title: string;
  description?: string;
  category: string;
  targetValue: number;
  unit: string;
  deadline?: Date;
}

export interface GoalUpdateData {
  title?: string;
  description?: string;
  category?: string;
  targetValue?: number;
  currentValue?: number;
  unit?: string;
  deadline?: Date;
  isCompleted?: boolean;
  isActive?: boolean;
}

export interface GoalProgressData {
  value: number;
  notes?: string;
}

export interface GoalsResponse {
  goals: Goal[];
  pagination: {
    total: number;
    page: number;
    per_page: number;
    pages: number;
  };
}

export interface GoalStatsResponse {
  total_goals: number;
  completed_goals: number;
  active_goals: number;
  completion_rate: number;
  categories: Record<string, number>;
  recent_progress_count: number;
  average_progress: number;
}

class GoalService {
  /**
   * Get user's goals with optional filtering
   */
  async getGoals(params?: {
    category?: string;
    activeOnly?: boolean;
    page?: number;
    perPage?: number;
  }): Promise<GoalsResponse> {
    try {
      console.log('🎯 GoalService: Fetching user goals...');
      
      const queryParams = new URLSearchParams();
      if (params?.category) queryParams.append('category', params.category);
      if (params?.activeOnly !== undefined) queryParams.append('active_only', params.activeOnly.toString());
      if (params?.page) queryParams.append('page', params.page.toString());
      if (params?.perPage) queryParams.append('per_page', params.perPage.toString());
      
      const url = `/goals${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
      const response = await apiClient.request(url);
      
      if (response.success && response.data) {
        console.log('✅ GoalService: Successfully fetched goals:', response.data);
        
        // Transform backend data to frontend format
        const transformedGoals = response.data.goals.map((goal: any) => ({
          id: goal.id,
          userId: goal.user_id,
          title: goal.title,
          description: goal.description,
          category: goal.category,
          targetValue: goal.target_value,
          currentValue: goal.current_value,
          unit: goal.unit,
          deadline: goal.deadline ? new Date(goal.deadline) : undefined,
          targetDate: goal.deadline ? new Date(goal.deadline) : undefined, // Alias for compatibility
          isCompleted: goal.is_completed,
          progress: Math.round(goal.progress_percentage || ((goal.current_value / goal.target_value) * 100) || 0),
          status: goal.is_completed ? 'completed' : (goal.current_value > 0 ? 'in_progress' : 'not_started'),
          priority: 'medium', // Default priority since backend doesn't have this
          createdAt: new Date(goal.created_at),
          updatedAt: new Date(goal.updated_at)
        }));
        
        return {
          goals: transformedGoals,
          pagination: response.data.pagination
        };
      } else {
        throw new Error(response.error || 'Failed to fetch goals');
      }
    } catch (error) {
      console.error('❌ GoalService: Error fetching goals:', error);
      throw error;
    }
  }

  /**
   * Create a new goal
   */
  async createGoal(goalData: GoalCreateData): Promise<Goal> {
    try {
      console.log('🎯 GoalService: Creating new goal:', goalData);
      
      // Transform frontend data to backend format
      const backendData = {
        title: goalData.title,
        description: goalData.description,
        category: goalData.category,
        target_value: goalData.targetValue,
        unit: goalData.unit,
        deadline: goalData.deadline?.toISOString()
      };
      
      const response = await apiClient.request('/goals', {
        method: 'POST',
        body: JSON.stringify(backendData)
      });
      
      if (response.success && response.data) {
        console.log('✅ GoalService: Successfully created goal:', response.data);
        
        // Transform backend response to frontend format
        const goal = response.data;
        return {
          id: goal.id,
          userId: goal.user_id,
          title: goal.title,
          description: goal.description,
          category: goal.category,
          targetValue: goal.target_value,
          currentValue: goal.current_value,
          unit: goal.unit,
          deadline: goal.deadline ? new Date(goal.deadline) : undefined,
          isCompleted: goal.is_completed,
          progress: Math.round(goal.progress_percentage || 0),
          status: goal.is_completed ? 'completed' : 'in_progress',
          priority: 'medium', // Default priority
          createdAt: new Date(goal.created_at),
          updatedAt: new Date(goal.updated_at)
        };
      } else {
        throw new Error(response.error || 'Failed to create goal');
      }
    } catch (error) {
      console.error('❌ GoalService: Error creating goal:', error);
      throw error;
    }
  }

  /**
   * Update a goal
   */
  async updateGoal(goalId: string, goalData: GoalUpdateData): Promise<Goal> {
    try {
      console.log('🎯 GoalService: Updating goal:', goalId, goalData);
      
      // Transform frontend data to backend format
      const backendData: any = {};
      if (goalData.title !== undefined) backendData.title = goalData.title;
      if (goalData.description !== undefined) backendData.description = goalData.description;
      if (goalData.category !== undefined) backendData.category = goalData.category;
      if (goalData.targetValue !== undefined) backendData.target_value = goalData.targetValue;
      if (goalData.currentValue !== undefined) backendData.current_value = goalData.currentValue;
      if (goalData.unit !== undefined) backendData.unit = goalData.unit;
      if (goalData.deadline !== undefined) backendData.deadline = goalData.deadline?.toISOString();
      if (goalData.isCompleted !== undefined) backendData.is_completed = goalData.isCompleted;
      if (goalData.isActive !== undefined) backendData.is_active = goalData.isActive;
      
      const response = await apiClient.request(`/goals/${goalId}`, {
        method: 'PUT',
        body: JSON.stringify(backendData)
      });
      
      if (response.success && response.data) {
        console.log('✅ GoalService: Successfully updated goal:', response.data);
        
        // Transform backend response to frontend format
        const goal = response.data;
        return {
          id: goal.id,
          userId: goal.user_id,
          title: goal.title,
          description: goal.description,
          category: goal.category,
          targetValue: goal.target_value,
          currentValue: goal.current_value,
          unit: goal.unit,
          deadline: goal.deadline ? new Date(goal.deadline) : undefined,
          isCompleted: goal.is_completed,
          progress: Math.round(goal.progress_percentage || 0),
          status: goal.is_completed ? 'completed' : 'in_progress',
          priority: 'medium', // Default priority
          createdAt: new Date(goal.created_at),
          updatedAt: new Date(goal.updated_at)
        };
      } else {
        throw new Error(response.error || 'Failed to update goal');
      }
    } catch (error) {
      console.error('❌ GoalService: Error updating goal:', error);
      throw error;
    }
  }

  /**
   * Delete a goal
   */
  async deleteGoal(goalId: string): Promise<void> {
    try {
      console.log('🎯 GoalService: Deleting goal:', goalId);
      
      const response = await apiClient.request(`/goals/${goalId}`, {
        method: 'DELETE'
      });
      
      if (response.success) {
        console.log('✅ GoalService: Successfully deleted goal:', goalId);
      } else {
        throw new Error(response.error || 'Failed to delete goal');
      }
    } catch (error) {
      console.error('❌ GoalService: Error deleting goal:', error);
      throw error;
    }
  }

  /**
   * Add progress to a goal
   */
  async addGoalProgress(goalId: string, progressData: GoalProgressData): Promise<void> {
    try {
      console.log('🎯 GoalService: Adding progress to goal:', goalId, progressData);
      
      const response = await apiClient.request(`/goals/${goalId}/progress`, {
        method: 'POST',
        body: JSON.stringify(progressData)
      });
      
      if (response.success) {
        console.log('✅ GoalService: Successfully added progress to goal:', goalId);
      } else {
        throw new Error(response.error || 'Failed to add progress');
      }
    } catch (error) {
      console.error('❌ GoalService: Error adding progress:', error);
      throw error;
    }
  }

  /**
   * Get goal statistics
   */
  async getGoalStats(): Promise<GoalStatsResponse> {
    try {
      console.log('🎯 GoalService: Fetching goal statistics...');
      
      const response = await apiClient.request('/goals/stats/summary');
      
      if (response.success && response.data) {
        console.log('✅ GoalService: Successfully fetched goal stats:', response.data);
        return response.data;
      } else {
        throw new Error(response.error || 'Failed to fetch goal statistics');
      }
    } catch (error) {
      console.error('❌ GoalService: Error fetching goal stats:', error);
      throw error;
    }
  }
}

export const goalService = new GoalService();
