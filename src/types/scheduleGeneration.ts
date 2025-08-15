// Schedule Generation Types
export interface ScheduleGenerationRequest {
  date: string; // YYYY-MM-DD format
  wakeUpTime: string; // HH:MM format
  activities: ScheduleActivity[];
  constraints: ScheduleConstraints;
}

export interface ScheduleActivity {
  name: string;
  durationMinutes: number;
  priority: number; // 1 = highest priority, higher numbers = lower priority
  timeWindow?: [string, string]; // Optional time window [start, end] in HH:MM format
  category?: string; // Optional category
  description?: string; // Optional description
}

export interface ScheduleConstraints {
  lunchBreak: boolean;
  maxConsecutiveWorkHours: number;
  lunchBreakDuration?: number; // Optional, defaults to 60 minutes
  lunchBreakTimeWindow?: [string, string]; // Optional, defaults to ["12:00", "14:00"]
  workStartTime?: string; // Optional, defaults to wake up time + 1 hour
  workEndTime?: string; // Optional, defaults to "18:00"
  breakDuration?: number; // Optional break duration between activities
  allowOvertime?: boolean; // Optional, allow scheduling beyond work hours
}

export interface ScheduleGenerationResponse {
  success: boolean;
  schedule?: GeneratedSchedule;
  error?: string;
  warnings?: string[];
}

export interface GeneratedSchedule {
  date: string;
  totalDuration: number;
  scheduledActivities: ScheduledActivity[];
  unscheduledActivities: ScheduleActivity[];
  breaks: ScheduleBreak[];
  summary: ScheduleSummary;
}

export interface ScheduledActivity {
  name: string;
  startTime: string; // HH:MM format
  endTime: string; // HH:MM format
  durationMinutes: number;
  priority: number;
  category?: string;
  description?: string;
}

export interface ScheduleBreak {
  type: 'lunch' | 'short' | 'long';
  startTime: string;
  endTime: string;
  durationMinutes: number;
}

export interface ScheduleSummary {
  totalWorkTime: number;
  totalBreakTime: number;
  totalFreeTime: number;
  productivityScore: number;
  balanceScore: number;
}
