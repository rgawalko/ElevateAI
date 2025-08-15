import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  Plus,
  Clock,
  Calendar,
  Save,
  Trash2,
  Copy,
  RotateCcw,
  Grid3X3,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Loader2
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card, Button, Input, Select } from '../components';
import type { ActivityCategory } from '../types';
import { ActivityCategory as ActivityCategoryEnum, Priority, Priority as PriorityEnum } from '../types';
import { getCategoryColor, getCategoryIcon, getPriorityColor } from '../utils';
import { apiClient } from '../services/api';

interface TimeSlot {
  id: string;
  startTime: string;
  endTime: string;
  title: string;
  description?: string;
  category: ActivityCategory;
  priority: Priority;
}

interface DaySchedule {
  day: string;
  date: string;
  timeSlots: TimeSlot[];
}

const DAYS_OF_WEEK = [
  'Sunday',
  'Monday', 
  'Tuesday',
  'Wednesday',
  'Thursday',
  'Friday',
  'Saturday'
];

// Helper functions for data conversion
const calculateDurationMinutes = (startTime: string, endTime: string): number => {
  const [startHour, startMin] = startTime.split(':').map(Number);
  const [endHour, endMin] = endTime.split(':').map(Number);
  const startMinutes = startHour * 60 + startMin;
  const endMinutes = endHour * 60 + endMin;
  return endMinutes - startMinutes;
};

const convertPriorityToNumber = (priority: Priority): number => {
  switch (priority) {
    case PriorityEnum.URGENT: return 1;
    case PriorityEnum.HIGH: return 2;
    case PriorityEnum.MEDIUM: return 3;
    case PriorityEnum.LOW: return 4;
    default: return 3;
  }
};

const convertPriorityFromNumber = (priority: number): Priority => {
  switch (priority) {
    case 1: return PriorityEnum.URGENT;
    case 2: return PriorityEnum.HIGH;
    case 3: return PriorityEnum.MEDIUM;
    case 4: return PriorityEnum.LOW;
    default: return PriorityEnum.MEDIUM;
  }
};

const convertCategoryFromString = (category: string): ActivityCategory => {
  const categoryUpper = category.toUpperCase();
  switch (categoryUpper) {
    case 'WORK': return ActivityCategoryEnum.WORK;
    case 'EXERCISE': return ActivityCategoryEnum.EXERCISE;
    case 'LEARNING': return ActivityCategoryEnum.LEARNING;
    case 'PERSONAL': return ActivityCategoryEnum.PERSONAL;
    case 'BREAK': return ActivityCategoryEnum.PERSONAL; // Map break to personal
    default: return ActivityCategoryEnum.PERSONAL;
  }
};

export const ScheduleCreator: React.FC = () => {
  const [scheduleName, setScheduleName] = useState('');
  const [viewMode, setViewMode] = useState<'day' | 'week' | 'month'>('day');
  const [selectedWeek, setSelectedWeek] = useState(getWeekDates());
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [activeDay, setActiveDay] = useState(0); // Sunday = 0
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<{
    show: boolean;
    summary?: {
      productivityScore?: number;
      balanceScore?: number;
      totalWorkTime?: number;
      totalBreakTime?: number;
      recommendations?: string[];
    };
    optimizations?: string[];
  }>({ show: false });
  const [schedules, setSchedules] = useState<DaySchedule[]>(
    DAYS_OF_WEEK.map((day, index) => ({
      day,
      date: selectedWeek[index],
      timeSlots: []
    }))
  );

  // Update schedule dates when selectedWeek changes
  useEffect(() => {
    setSchedules(prev => prev.map((schedule, index) => ({
      ...schedule,
      date: selectedWeek[index]
    })));
  }, [selectedWeek]);

  function getWeekDates(): string[] {
    const today = new Date();
    const sunday = new Date(today.setDate(today.getDate() - today.getDay()));
    const week = [];

    for (let i = 0; i < 7; i++) {
      const date = new Date(sunday);
      date.setDate(sunday.getDate() + i);
      week.push(date.toISOString().split('T')[0]);
    }

    return week;
  }

  function getMonthDates(date: Date): Date[] {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - startDate.getDay()); // Start from Sunday

    const dates = [];
    const current = new Date(startDate);

    // Generate 6 weeks (42 days) to cover the entire month view
    for (let i = 0; i < 42; i++) {
      dates.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }

    return dates;
  }

  function navigateWeek(direction: 'prev' | 'next') {
    const newWeek = [...selectedWeek];
    const firstDate = new Date(newWeek[0]);
    firstDate.setDate(firstDate.getDate() + (direction === 'next' ? 7 : -7));

    const updatedWeek = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(firstDate);
      date.setDate(firstDate.getDate() + i);
      updatedWeek.push(date.toISOString().split('T')[0]);
    }

    setSelectedWeek(updatedWeek);
  }

  function navigateMonth(direction: 'prev' | 'next') {
    const newMonth = new Date(currentMonth);
    newMonth.setMonth(newMonth.getMonth() + (direction === 'next' ? 1 : -1));
    setCurrentMonth(newMonth);
  }

  const addTimeSlot = (dayIndex: number) => {
    const newSlot: TimeSlot = {
      id: `slot-${Date.now()}`,
      startTime: '09:00',
      endTime: '10:00',
      title: '',
      description: '',
      category: ActivityCategoryEnum.WORK,
      priority: PriorityEnum.MEDIUM
    };

    setSchedules(prev => prev.map((schedule, index) => 
      index === dayIndex 
        ? { ...schedule, timeSlots: [...schedule.timeSlots, newSlot] }
        : schedule
    ));
  };

  const updateTimeSlot = (dayIndex: number, slotId: string, updates: Partial<TimeSlot>) => {
    setSchedules(prev => prev.map((schedule, index) => 
      index === dayIndex 
        ? {
            ...schedule,
            timeSlots: schedule.timeSlots.map(slot => 
              slot.id === slotId ? { ...slot, ...updates } : slot
            )
          }
        : schedule
    ));
  };

  const removeTimeSlot = (dayIndex: number, slotId: string) => {
    setSchedules(prev => prev.map((schedule, index) => 
      index === dayIndex 
        ? {
            ...schedule,
            timeSlots: schedule.timeSlots.filter(slot => slot.id !== slotId)
          }
        : schedule
    ));
  };

  const copyDay = (fromIndex: number, toIndex: number) => {
    const sourceDay = schedules[fromIndex];
    const copiedSlots = sourceDay.timeSlots.map(slot => ({
      ...slot,
      id: `slot-${Date.now()}-${Math.random()}`
    }));

    setSchedules(prev => prev.map((schedule, index) => 
      index === toIndex 
        ? { ...schedule, timeSlots: copiedSlots }
        : schedule
    ));
  };

  const clearDay = (dayIndex: number) => {
    setSchedules(prev => prev.map((schedule, index) =>
      index === dayIndex
        ? { ...schedule, timeSlots: [] }
        : schedule
    ));
  };

  const autofillMondayForTesting = () => {
    const mondayIndex = 1; // Monday is index 1 in DAYS_OF_WEEK array

    const testActivities: TimeSlot[] = [
      {
        id: `slot-${Date.now()}-1`,
        startTime: '07:30',
        endTime: '08:00',
        title: '☕ Morning Coffee & Email Check',
        description: 'Quick coffee and check urgent emails (Test Activity)',
        category: ActivityCategoryEnum.PERSONAL,
        priority: PriorityEnum.MEDIUM
      },
      {
        id: `slot-${Date.now()}-2`,
        startTime: '11:30',
        endTime: '12:30',
        title: '👥 Team Standup Meeting',
        description: 'Daily team sync and project updates (Test Activity)',
        category: ActivityCategoryEnum.WORK,
        priority: PriorityEnum.HIGH
      },
      {
        id: `slot-${Date.now()}-3`,
        startTime: '08:30',
        endTime: '11:00',
        title: '💻 Deep Work - Feature Development',
        description: 'Focus time for coding new features (Test Activity)',
        category: ActivityCategoryEnum.WORK,
        priority: PriorityEnum.HIGH
      },
      {
        id: `slot-${Date.now()}-4`,
        startTime: '15:00',
        endTime: '16:00',
        title: '📊 Client Presentation',
        description: 'Present quarterly results to client (Test Activity)',
        category: ActivityCategoryEnum.WORK,
        priority: PriorityEnum.URGENT
      },
      {
        id: `slot-${Date.now()}-5`,
        startTime: '14:00',
        endTime: '14:30',
        title: '🍽️ Quick Lunch',
        description: 'Grab a quick bite (Test Activity)',
        category: ActivityCategoryEnum.PERSONAL,
        priority: PriorityEnum.MEDIUM
      },
      {
        id: `slot-${Date.now()}-6`,
        startTime: '16:30',
        endTime: '17:30',
        title: '🔍 Code Review Session',
        description: 'Review team member pull requests (Test Activity)',
        category: ActivityCategoryEnum.WORK,
        priority: PriorityEnum.MEDIUM
      },
      {
        id: `slot-${Date.now()}-7`,
        startTime: '18:00',
        endTime: '19:00',
        title: '💪 Gym Workout',
        description: 'Cardio and strength training (Test Activity)',
        category: ActivityCategoryEnum.EXERCISE,
        priority: PriorityEnum.LOW
      },
      {
        id: `slot-${Date.now()}-8`,
        startTime: '13:00',
        endTime: '14:00',
        title: '📚 Learning Session - React Patterns',
        description: 'Study advanced React design patterns (Test Activity)',
        category: ActivityCategoryEnum.LEARNING,
        priority: PriorityEnum.LOW
      },
      {
        id: `slot-${Date.now()}-9`,
        startTime: '20:00',
        endTime: '20:30',
        title: '🛒 Grocery Shopping',
        description: 'Weekly grocery run (Test Activity)',
        category: ActivityCategoryEnum.PERSONAL,
        priority: PriorityEnum.MEDIUM
      },
      {
        id: `slot-${Date.now()}-10`,
        startTime: '09:00',
        endTime: '09:30',
        title: '📧 Email Processing',
        description: 'Process and respond to emails (Test Activity)',
        category: ActivityCategoryEnum.WORK,
        priority: PriorityEnum.LOW
      }
    ];

    setSchedules(prev => prev.map((schedule, index) =>
      index === mondayIndex
        ? { ...schedule, timeSlots: testActivities }
        : schedule
    ));
  };

  const optimizeSchedule = async (dayIndex: number) => {
    const currentDay = schedules[dayIndex];

    if (currentDay.timeSlots.length === 0) {
      alert('No activities to optimize. Please add some activities first.');
      return;
    }

    if (!currentDay.date) {
      alert('Invalid date. Please refresh the page and try again.');
      return;
    }

    setIsOptimizing(true);

    try {
      // Convert TimeSlots to the format expected by the AI service
      const activities = currentDay.timeSlots.map(slot => ({
        name: slot.title || 'Untitled Activity',
        durationMinutes: calculateDurationMinutes(slot.startTime, slot.endTime),
        priority: convertPriorityToNumber(slot.priority),
        category: slot.category.toLowerCase(),
        description: slot.description || '',
        timeWindow: slot.startTime && slot.endTime ? [slot.startTime, slot.endTime] : undefined
      }));

      // Prepare the request payload
      const requestPayload = {
        date: currentDay.date,
        wakeUpTime: "07:00", // Default wake up time
        activities: activities,
        constraints: {
          lunchBreak: true,
          lunchBreakDuration: 45,
          maxConsecutiveWorkHours: 2.5,
          shortBreakDuration: 15,
          workStartTime: "08:30",
          workEndTime: "17:30"
        }
      };

      console.log('Sending optimization request:', requestPayload);
      console.log('Current day date:', currentDay.date);
      console.log('Selected week:', selectedWeek);

      // Send request to backend AI service (using test endpoint temporarily)
      const response = await fetch('/api/test/ai-schedule-optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Note: In a real app, you'd include authentication headers here
          // 'Authorization': `Bearer ${userToken}`
        },
        body: JSON.stringify(requestPayload)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('AI optimization result:', result);

      if (result.success && result.schedule) {
        console.log('📊 Scheduled activities received:', result.schedule.scheduledActivities.length);
        console.log('📋 Activities data:', result.schedule.scheduledActivities);

        // Convert the AI response back to TimeSlots
        const optimizedTimeSlots: TimeSlot[] = result.schedule.scheduledActivities.map((activity: any, index: number) => ({
          id: `optimized-${Date.now()}-${index}`,
          startTime: activity.startTime,
          endTime: activity.endTime,
          title: activity.name,
          description: activity.description || `Optimized by AI - ${activity.category}`,
          category: convertCategoryFromString(activity.category),
          priority: convertPriorityFromNumber(activity.priority)
        }));

        console.log('🔄 Converted time slots:', optimizedTimeSlots.length);
        console.log('📝 Time slots data:', optimizedTimeSlots);

        // Add breaks as time slots too
        if (result.schedule.breaks) {
          result.schedule.breaks.forEach((breakItem: any, index: number) => {
            optimizedTimeSlots.push({
              id: `break-${Date.now()}-${index}`,
              startTime: breakItem.startTime,
              endTime: breakItem.endTime,
              title: breakItem.name || 'Break',
              description: 'AI-scheduled break',
              category: ActivityCategoryEnum.PERSONAL,
              priority: PriorityEnum.MEDIUM
            });
          });
        }

        // Update the schedule with optimized activities
        setSchedules(prev => {
          const newSchedules = prev.map((schedule, index) =>
            index === dayIndex
              ? { ...schedule, timeSlots: optimizedTimeSlots }
              : schedule
          );
          console.log('📅 Updated schedules state:', newSchedules[dayIndex].timeSlots.length);
          console.log('🎯 Final time slots for day:', newSchedules[dayIndex].timeSlots);
          return newSchedules;
        });

        // Prepare optimization details
        const summary = result.schedule.summary || {};
        const optimizations = [];

        // Add optimization insights based on the result
        if (summary.productivityScore && summary.productivityScore > 80) {
          optimizations.push("🎯 High-priority tasks scheduled during peak productivity hours");
        }
        if (summary.balanceScore && summary.balanceScore > 75) {
          optimizations.push("⚖️ Optimal work-life balance achieved with proper break distribution");
        }
        if (summary.totalBreakTime && summary.totalBreakTime > 0) {
          optimizations.push(`⏰ ${Math.round(summary.totalBreakTime / 60)} hours of breaks strategically placed`);
        }
        if (result.schedule.scheduledActivities?.length > 0) {
          optimizations.push(`📋 ${result.schedule.scheduledActivities.length} activities optimally scheduled`);
        }

        // Add recommendations from AI
        if (summary.recommendations && summary.recommendations.length > 0) {
          optimizations.push(...summary.recommendations.map((rec: string) => `💡 ${rec}`));
        }

        // Add optimization details if available
        if (result.schedule.optimizationDetails) {
          const details = result.schedule.optimizationDetails;
          if (details.priorityOptimization) {
            optimizations.push(`🎯 ${details.priorityOptimization}`);
          }
          if (details.breakOptimization) {
            optimizations.push(`⏸️ ${details.breakOptimization}`);
          }
          if (details.timeWindowRespected) {
            optimizations.push(`⏰ ${details.timeWindowRespected}`);
          }
          if (details.workLifeBalance) {
            optimizations.push(`⚖️ ${details.workLifeBalance}`);
          }
        }

        // Show optimization result
        setOptimizationResult({
          show: true,
          summary,
          optimizations
        });
      } else {
        throw new Error(result.error || 'Failed to optimize schedule');
      }

    } catch (error) {
      console.error('Error optimizing schedule:', error);
      alert(`Failed to optimize schedule: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsOptimizing(false);
    }
  };

  const [isSaving, setIsSaving] = useState(false);

  const saveSchedule = async () => {
    if (isSaving) return; // Prevent double-clicking

    try {
      setIsSaving(true);

      // Validate schedule name
      if (!scheduleName.trim()) {
        alert('Please enter a schedule name');
        return;
      }

      // Get the current day's schedule
      const currentDaySchedule = schedules[activeDay];

      if (!currentDaySchedule.timeSlots.length) {
        alert('Please add at least one time slot before saving');
        return;
      }

      // Convert TimeSlot data to the format expected by the backend
      const tasks = currentDaySchedule.timeSlots.map(slot => ({
        title: slot.title,
        description: slot.description || '',
        start_time: `${currentDaySchedule.date}T${slot.startTime}:00`,
        end_time: `${currentDaySchedule.date}T${slot.endTime}:00`,
        category: slot.category,
        priority: getPriorityNumber(slot.priority),
        estimated_duration: calculateDuration(slot.startTime, slot.endTime),
        is_completed: false
      }));

      // Prepare schedule data in the format expected by the backend
      const scheduleData = {
        user_id: "00000000-0000-0000-0000-000000000000", // Placeholder - gets overwritten by backend
        date: currentDaySchedule.date, // Send as YYYY-MM-DD, let backend parse it
        tasks: tasks,
        generated_by_ai: false
      };

      console.log('Saving schedule:', scheduleData);
      console.log('Sample task:', tasks[0]);
      console.log('Date format:', currentDaySchedule.date);
      console.log('Full date:', `${currentDaySchedule.date}T00:00:00.000Z`);

      // Use the API client for proper authentication handling
      try {
        const result = await apiClient.post('/schedules', scheduleData);

        console.log('Schedule saved successfully:', result);
        alert('Schedule saved successfully!');

        // Redirect to the schedule page to show the saved schedule
        window.location.href = '/schedule';
      } catch (error) {
        console.error('Detailed save error:', error);

        // Try to get more details about the validation error
        if (error instanceof Error && error.message.includes('422')) {
          // For 422 errors, try to get the validation details
          try {
            const response = await fetch('/api/schedules', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('elevate_auth_token')}`
              },
              body: JSON.stringify(scheduleData)
            });

            if (!response.ok) {
              const errorDetails = await response.json();
              console.error('Validation error details:', errorDetails);
              alert(`Validation error: ${JSON.stringify(errorDetails, null, 2)}`);
            }
          } catch (detailError) {
            console.error('Could not get error details:', detailError);
          }
        }

        throw error; // Re-throw to be caught by outer try-catch
      }
    } catch (error) {
      console.error('Error saving schedule:', error);
      if (error instanceof Error) {
        alert(`Failed to save schedule: ${error.message}`);
      } else {
        alert('Failed to save schedule. Please try again.');
      }
    } finally {
      setIsSaving(false);
    }
  };

  // Helper function to calculate duration in minutes
  const calculateDuration = (startTime: string, endTime: string): number => {
    const start = new Date(`2000-01-01T${startTime}:00`);
    const end = new Date(`2000-01-01T${endTime}:00`);
    return Math.round((end.getTime() - start.getTime()) / (1000 * 60));
  };

  // Helper function to convert Priority enum to number
  const getPriorityNumber = (priority: Priority): number => {
    switch (priority) {
      case Priority.URGENT: return 1;
      case Priority.HIGH: return 2;
      case Priority.MEDIUM: return 3;
      case Priority.LOW: return 4;
      default: return 3;
    }
  };

  const categoryOptions = Object.values(ActivityCategoryEnum).map(category => ({
    value: category,
    label: `${getCategoryIcon(category)} ${category.charAt(0).toUpperCase() + category.slice(1)}`
  }));

  const priorityOptions = Object.values(PriorityEnum).map(priority => ({
    value: priority,
    label: priority.charAt(0).toUpperCase() + priority.slice(1)
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/schedule">
            <Button variant="outline" icon={<ArrowLeft size={18} />}>
              Back to Schedule
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-primary-800 tracking-tight">Create Schedule</h1>
            <p className="text-primary-800 mt-2 text-lg font-medium">
              Plan your schedule with multiple view modes
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {/* View Mode Selector */}
          <div className="flex bg-secondary-100 rounded-xl p-1">
            <button
              onClick={() => setViewMode('day')}
              className={`px-3 py-2 rounded-lg font-semibold text-sm transition-all duration-200 ${
                viewMode === 'day'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-primary-700 hover:text-primary-800'
              }`}
            >
              <Calendar className="w-4 h-4 inline mr-1" />
              Day
            </button>
            <button
              onClick={() => setViewMode('week')}
              className={`px-3 py-2 rounded-lg font-semibold text-sm transition-all duration-200 ${
                viewMode === 'week'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-primary-700 hover:text-primary-800'
              }`}
            >
              <CalendarDays className="w-4 h-4 inline mr-1" />
              Week
            </button>
            <button
              onClick={() => setViewMode('month')}
              className={`px-3 py-2 rounded-lg font-semibold text-sm transition-all duration-200 ${
                viewMode === 'month'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-primary-700 hover:text-primary-800'
              }`}
            >
              <Grid3X3 className="w-4 h-4 inline mr-1" />
              Month
            </button>
          </div>

          <Button variant="outline" icon={<RotateCcw size={18} />}>
            Reset All
          </Button>
          <Button
            onClick={saveSchedule}
            icon={<Save size={18} />}
            size="lg"
            disabled={isSaving}
          >
            {isSaving ? 'Saving...' : 'Save Schedule'}
          </Button>
        </div>
      </div>

      {/* Schedule Name */}
      <Card>
        <div className="space-y-4">
          <h3 className="text-lg font-bold text-primary-800">Schedule Details</h3>
          <Input
            label="Schedule Name"
            value={scheduleName}
            onChange={(e) => setScheduleName(e.target.value)}
            placeholder="Enter a name for your schedule..."
          />
        </div>
      </Card>

      {/* Navigation based on view mode */}
      {viewMode === 'day' && (
        <div className="flex items-center justify-center space-x-2 bg-white rounded-xl p-2 border border-secondary-200">
          {DAYS_OF_WEEK.map((day, index) => (
            <button
              key={day}
              onClick={() => setActiveDay(index)}
              className={`px-4 py-2 rounded-lg font-semibold transition-all duration-200 ${
                activeDay === index
                  ? 'bg-primary-500 text-white shadow-md'
                  : 'text-primary-700 hover:bg-secondary-50 hover:text-primary-800'
              }`}
            >
              <div className="text-center">
                <div className="text-sm">{day}</div>
                <div className="text-xs opacity-75">{selectedWeek[index]}</div>
              </div>
            </button>
          ))}
        </div>
      )}

      {viewMode === 'week' && (
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-secondary-200">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigateWeek('prev')}
            icon={<ChevronLeft size={16} />}
          >
            Previous Week
          </Button>
          <div className="text-center">
            <h3 className="text-lg font-bold text-primary-800">
              Week of {new Date(selectedWeek[0]).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
            </h3>
            <p className="text-sm text-primary-700">
              {selectedWeek[0]} to {selectedWeek[6]}
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigateWeek('next')}
            icon={<ChevronRight size={16} />}
          >
            Next Week
          </Button>
        </div>
      )}

      {viewMode === 'month' && (
        <div className="flex items-center justify-between bg-white rounded-xl p-4 border border-secondary-200">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigateMonth('prev')}
            icon={<ChevronLeft size={16} />}
          >
            Previous Month
          </Button>
          <div className="text-center">
            <h3 className="text-lg font-bold text-primary-800">
              {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h3>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigateMonth('next')}
            icon={<ChevronRight size={16} />}
          >
            Next Month
          </Button>
        </div>
      )}

      {/* Optimization Result Modal */}
      {optimizationResult.show && (
        <div
          className="fixed inset-0 bg-transparent backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={() => setOptimizationResult({ show: false })}
        >
          <div
            className="bg-white rounded-lg p-6 max-w-lg w-full max-h-[80vh] overflow-y-auto shadow-2xl border border-gray-200"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-primary-800">
                ✨ Schedule Optimized Successfully!
              </h3>
              <button
                onClick={() => setOptimizationResult({ show: false })}
                className="text-secondary-400 hover:text-secondary-600 text-xl font-bold w-8 h-8 flex items-center justify-center rounded-full hover:bg-secondary-100"
              >
                ✕
              </button>
            </div>

            {/* Scores */}
            {optimizationResult.summary && (
              <div className="grid grid-cols-2 gap-4 mb-4">
                {optimizationResult.summary.productivityScore !== undefined && (
                  <div className="bg-blue-50 p-3 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {optimizationResult.summary.productivityScore}%
                    </div>
                    <div className="text-sm text-blue-800 font-medium">Productivity Score</div>
                  </div>
                )}
                {optimizationResult.summary.balanceScore !== undefined && (
                  <div className="bg-green-50 p-3 rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-600">
                      {optimizationResult.summary.balanceScore}%
                    </div>
                    <div className="text-sm text-green-800 font-medium">Balance Score</div>
                  </div>
                )}
              </div>
            )}

            {/* Optimizations */}
            {optimizationResult.optimizations && optimizationResult.optimizations.length > 0 && (
              <div className="mb-4">
                <h4 className="font-medium text-gray-800 mb-2">What was optimized:</h4>
                <ul className="space-y-2">
                  {optimizationResult.optimizations.map((optimization, index) => (
                    <li key={index} className="text-sm text-gray-800 flex items-start">
                      <span className="mr-2">•</span>
                      <span>{optimization}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex justify-end">
              <Button
                onClick={() => setOptimizationResult({ show: false })}
                variant="primary"
              >
                Got it!
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Schedule Views */}
      {viewMode === 'day' && (
        <DayView
          activeDay={activeDay}
          schedules={schedules}
          addTimeSlot={addTimeSlot}
          updateTimeSlot={updateTimeSlot}
          removeTimeSlot={removeTimeSlot}
          copyDay={copyDay}
          clearDay={clearDay}
          autofillMondayForTesting={autofillMondayForTesting}
          optimizeSchedule={optimizeSchedule}
          isOptimizing={isOptimizing}
          categoryOptions={categoryOptions}
          priorityOptions={priorityOptions}
        />
      )}

      {viewMode === 'week' && (
        <WeekView
          schedules={schedules}
          addTimeSlot={addTimeSlot}
          updateTimeSlot={updateTimeSlot}
          removeTimeSlot={removeTimeSlot}
          categoryOptions={categoryOptions}
          priorityOptions={priorityOptions}
        />
      )}

      {viewMode === 'month' && (
        <MonthView
          currentMonth={currentMonth}
          schedules={schedules}
          addTimeSlot={addTimeSlot}
          updateTimeSlot={updateTimeSlot}
          removeTimeSlot={removeTimeSlot}
          categoryOptions={categoryOptions}
          priorityOptions={priorityOptions}
        />
      )}
    </div>
  );
};

// Day View Component
interface DayViewProps {
  activeDay: number;
  schedules: DaySchedule[];
  addTimeSlot: (dayIndex: number) => void;
  updateTimeSlot: (dayIndex: number, slotId: string, updates: Partial<TimeSlot>) => void;
  removeTimeSlot: (dayIndex: number, slotId: string) => void;
  copyDay: (fromIndex: number, toIndex: number) => void;
  clearDay: (dayIndex: number) => void;
  autofillMondayForTesting: () => void;
  optimizeSchedule: (dayIndex: number) => Promise<void>;
  isOptimizing: boolean;
  categoryOptions: Array<{ value: string; label: string }>;
  priorityOptions: Array<{ value: string; label: string }>;
}

const DayView: React.FC<DayViewProps> = ({
  activeDay,
  schedules,
  addTimeSlot,
  updateTimeSlot,
  removeTimeSlot,
  copyDay,
  clearDay,
  autofillMondayForTesting,
  optimizeSchedule,
  isOptimizing,
  categoryOptions,
  priorityOptions
}) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Day Overview */}
      <div className="lg:col-span-1">
        <Card title={`${DAYS_OF_WEEK[activeDay]} Overview`}>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-primary-800">
                Total Time Slots: {schedules[activeDay].timeSlots.length}
              </span>
              <Button
                size="sm"
                onClick={() => addTimeSlot(activeDay)}
                icon={<Plus size={16} />}
              >
                Add Slot
              </Button>
            </div>

            {/* AI Optimization Button */}
            {schedules[activeDay].timeSlots.length > 0 && (
              <div className="mt-4 p-3 bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-semibold text-purple-900 mb-1">
                      ✨ AI Schedule Optimization
                    </h4>
                    <p className="text-xs text-purple-700">
                      Let AI reorganize your activities for optimal productivity
                    </p>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => optimizeSchedule(activeDay)}
                    disabled={isOptimizing}
                    icon={isOptimizing ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700"
                  >
                    {isOptimizing ? 'Optimizing...' : 'Optimize Schedule'}
                  </Button>
                </div>
              </div>
            )}

            {/* Monday Testing Autofill Button */}
            {activeDay === 1 && ( // Monday is index 1
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-semibold text-blue-900 mb-1">
                      🧪 Testing Mode
                    </h4>
                    <p className="text-xs text-blue-700">
                      Autofill Monday with sample unorganized activities
                    </p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={autofillMondayForTesting}
                    className="bg-blue-100 border-blue-300 text-blue-700 hover:bg-blue-200"
                  >
                    Autofill Monday
                  </Button>
                </div>
              </div>
            )}

            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-primary-800">Copy from:</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                {DAYS_OF_WEEK.map((day, index) => (
                  <Button
                    key={day}
                    size="sm"
                    variant="outline"
                    disabled={index === activeDay || schedules[index].timeSlots.length === 0}
                    onClick={() => copyDay(index, activeDay)}
                    icon={<Copy size={14} />}
                  >
                    {day.slice(0, 3)}
                  </Button>
                ))}
              </div>
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => clearDay(activeDay)}
              disabled={schedules[activeDay].timeSlots.length === 0}
              icon={<Trash2 size={16} />}
              className="w-full"
            >
              Clear Day
            </Button>
          </div>
        </Card>
      </div>

      {/* Time Slots */}
      <div className="lg:col-span-2">
        <Card
          title={`${DAYS_OF_WEEK[activeDay]} Schedule`}
          action={
            schedules[activeDay].timeSlots.length > 0 && (
              <Button
                size="sm"
                onClick={() => optimizeSchedule(activeDay)}
                disabled={isOptimizing}
                icon={isOptimizing ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                className="bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700"
              >
                {isOptimizing ? 'Optimizing...' : 'Optimize with AI'}
              </Button>
            )
          }
        >
          {schedules[activeDay].timeSlots.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="mx-auto h-12 w-12 text-secondary-400 mb-4" />
              <h3 className="text-lg font-medium text-primary-800 mb-2">
                No time slots yet
              </h3>
              <p className="text-primary-700 mb-4">
                Add your first time slot to start planning your day
              </p>
              <div className="space-y-3">
                <Button onClick={() => addTimeSlot(activeDay)} icon={<Plus size={16} />}>
                  Add Time Slot
                </Button>
                {activeDay === 1 && ( // Monday is index 1
                  <div className="text-center">
                    <p className="text-sm text-blue-600 mb-2">
                      🧪 Or try the testing autofill for Monday
                    </p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={autofillMondayForTesting}
                      className="bg-blue-50 border-blue-300 text-blue-700 hover:bg-blue-100"
                    >
                      Autofill Sample Activities
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {(() => {
                const timeSlots = schedules[activeDay].timeSlots.sort((a, b) => a.startTime.localeCompare(b.startTime));
                console.log(`🎨 Rendering ${timeSlots.length} time slots for day ${activeDay}`);
                console.log('🎨 Time slots to render:', timeSlots);
                return timeSlots.map((slot) => (
                  <TimeSlotEditor
                    key={slot.id}
                    slot={slot}
                    onUpdate={(updates) => updateTimeSlot(activeDay, slot.id, updates)}
                    onRemove={() => removeTimeSlot(activeDay, slot.id)}
                    categoryOptions={categoryOptions}
                    priorityOptions={priorityOptions}
                  />
                ));
              })()}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

interface TimeSlotEditorProps {
  slot: TimeSlot;
  onUpdate: (updates: Partial<TimeSlot>) => void;
  onRemove: () => void;
  categoryOptions: Array<{ value: string; label: string }>;
  priorityOptions: Array<{ value: string; label: string }>;
}

const TimeSlotEditor: React.FC<TimeSlotEditorProps> = ({
  slot,
  onUpdate,
  onRemove,
  categoryOptions,
  priorityOptions
}) => {
  return (
    <div className="p-4 border border-secondary-200 rounded-xl bg-gradient-to-r from-secondary-50 to-white hover:shadow-md transition-all duration-200">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-semibold text-primary-800">Start Time</label>
          <Input
            type="time"
            value={slot.startTime}
            onChange={(e) => onUpdate({ startTime: e.target.value })}
          />
        </div>
        
        <div className="space-y-2">
          <label className="text-sm font-semibold text-primary-800">End Time</label>
          <Input
            type="time"
            value={slot.endTime}
            onChange={(e) => onUpdate({ endTime: e.target.value })}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-primary-800">Category</label>
          <Select
            value={slot.category}
            onChange={(value) => onUpdate({ category: value as ActivityCategory })}
            options={categoryOptions}
          />
        </div>

        <div className="space-y-2">
          <label className="text-sm font-semibold text-primary-800">Priority</label>
          <Select
            value={slot.priority}
            onChange={(value) => onUpdate({ priority: value as Priority })}
            options={priorityOptions}
          />
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <Input
          label="Title"
          value={slot.title}
          onChange={(e) => onUpdate({ title: e.target.value })}
          placeholder="What will you be doing?"
        />
        
        <Input
          label="Description (Optional)"
          value={slot.description || ''}
          onChange={(e) => onUpdate({ description: e.target.value })}
          placeholder="Add more details..."
        />
      </div>

      <div className="mt-4 flex justify-end">
        <Button
          variant="outline"
          size="sm"
          onClick={onRemove}
          icon={<Trash2 size={16} />}
        >
          Remove
        </Button>
      </div>
    </div>
  );
};

// Week View Component
interface WeekViewProps {
  schedules: DaySchedule[];
  addTimeSlot: (dayIndex: number) => void;
  updateTimeSlot: (dayIndex: number, slotId: string, updates: Partial<TimeSlot>) => void;
  removeTimeSlot: (dayIndex: number, slotId: string) => void;
  categoryOptions: Array<{ value: string; label: string }>;
  priorityOptions: Array<{ value: string; label: string }>;
}

const WeekView: React.FC<WeekViewProps> = ({
  schedules,
  addTimeSlot,
  updateTimeSlot,
  removeTimeSlot,
  categoryOptions,
  priorityOptions
}) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-7 gap-4">
      {DAYS_OF_WEEK.map((day, dayIndex) => (
        <Card key={day} title={day} className="min-h-96">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs text-primary-700">
                {schedules[dayIndex].timeSlots.length} slots
              </span>
              <Button
                size="sm"
                variant="outline"
                onClick={() => addTimeSlot(dayIndex)}
                icon={<Plus size={14} />}
              >
                Add
              </Button>
            </div>

            <div className="space-y-2">
              {schedules[dayIndex].timeSlots
                .sort((a, b) => a.startTime.localeCompare(b.startTime))
                .map((slot) => (
                  <div
                    key={slot.id}
                    className="p-2 bg-gradient-to-r from-secondary-50 to-white rounded-lg border border-secondary-200 hover:shadow-sm transition-all duration-200"
                  >
                    <div className="text-xs font-semibold text-primary-800 mb-1">
                      {slot.startTime} - {slot.endTime}
                    </div>
                    <div className="text-xs text-primary-800 mb-1 truncate">
                      {slot.title || 'Untitled'}
                    </div>
                    <div className="flex items-center justify-between">
                      <span className={`text-xs px-2 py-1 rounded-full ${getCategoryColor(slot.category)}`}>
                        {slot.category}
                      </span>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => removeTimeSlot(dayIndex, slot.id)}
                        icon={<Trash2 size={12} />}
                      />
                    </div>
                  </div>
                ))}

              {schedules[dayIndex].timeSlots.length === 0 && (
                <div className="text-center py-8">
                  <Calendar className="mx-auto h-8 w-8 text-secondary-400 mb-2" />
                  <p className="text-xs text-primary-700">No events</p>
                </div>
              )}
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};

// Month View Component
interface MonthViewProps {
  currentMonth: Date;
  schedules: DaySchedule[];
  addTimeSlot: (dayIndex: number) => void;
  updateTimeSlot: (dayIndex: number, slotId: string, updates: Partial<TimeSlot>) => void;
  removeTimeSlot: (dayIndex: number, slotId: string) => void;
  categoryOptions: Array<{ value: string; label: string }>;
  priorityOptions: Array<{ value: string; label: string }>;
}

const MonthView: React.FC<MonthViewProps> = ({
  currentMonth,
  schedules,
  addTimeSlot,
  updateTimeSlot,
  removeTimeSlot,
  categoryOptions,
  priorityOptions
}) => {
  function getMonthDates(date: Date): Date[] {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - startDate.getDay());

    const dates = [];
    const current = new Date(startDate);

    for (let i = 0; i < 42; i++) {
      dates.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }

    return dates;
  }

  const monthDates = getMonthDates(currentMonth);
  const isCurrentMonth = (date: Date) => date.getMonth() === currentMonth.getMonth();
  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  return (
    <Card title="Month View">
      <div className="grid grid-cols-7 gap-1">
        {/* Day headers */}
        {DAYS_OF_WEEK.map((day) => (
          <div key={day} className="p-2 text-center font-semibold text-secondary-700 text-sm">
            {day.slice(0, 3)}
          </div>
        ))}

        {/* Calendar dates */}
        {monthDates.map((date, index) => {
          const dayOfWeek = date.getDay();
          const daySchedule = schedules[dayOfWeek];

          return (
            <div
              key={index}
              className={`min-h-24 p-1 border border-secondary-200 rounded-lg ${
                isCurrentMonth(date)
                  ? 'bg-white hover:bg-secondary-50'
                  : 'bg-secondary-100 text-secondary-400'
              } ${
                isToday(date) ? 'ring-2 ring-primary-500' : ''
              } transition-all duration-200 cursor-pointer`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className={`text-xs font-semibold ${
                  isCurrentMonth(date) ? 'text-primary-800' : 'text-secondary-400'
                }`}>
                  {date.getDate()}
                </span>
                {isCurrentMonth(date) && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => addTimeSlot(dayOfWeek)}
                    icon={<Plus size={10} />}
                    className="h-5 w-5 p-0"
                  />
                )}
              </div>

              <div className="space-y-1">
                {daySchedule.timeSlots.slice(0, 2).map((slot) => (
                  <div
                    key={slot.id}
                    className="text-xs p-1 bg-primary-100 text-primary-800 rounded truncate"
                    title={`${slot.startTime} - ${slot.title}`}
                  >
                    {slot.startTime} {slot.title}
                  </div>
                ))}
                {daySchedule.timeSlots.length > 2 && (
                  <div className="text-xs text-primary-700">
                    +{daySchedule.timeSlots.length - 2} more
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};
