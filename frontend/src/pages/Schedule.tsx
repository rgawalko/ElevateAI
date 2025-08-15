import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Plus,
  Calendar,
  Clock,
  Brain,
  Settings,
  ChevronLeft,
  ChevronRight,
  Download,
  Trash2
} from 'lucide-react';
import { Card, Button, IconButton } from '../components';
import { ScheduleGenerationForm } from '../components/ScheduleGenerationForm';
import type { Schedule as ScheduleType, ScheduleTask } from '../types';
import { ActivityCategory, Priority } from '../types';
import type { ScheduleGenerationRequest } from '../types/scheduleGeneration';
import { scheduleService } from '../services';
import { 
  formatDate, 
  formatTime, 
  formatDuration, 
  getCategoryColor, 
  getCategoryIcon,
  getPriorityColor
} from '../utils';

export const Schedule: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<'day' | 'week'>('day');
  const [showGenerator, setShowGenerator] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [schedules, setSchedules] = useState<ScheduleType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isLoadingSchedules, setIsLoadingSchedules] = useState(false);

  // Load schedules from API
  const loadSchedules = async () => {
    // Prevent multiple simultaneous API calls
    if (isLoadingSchedules) {
      console.log('Already loading schedules, skipping...');
      return;
    }

    try {
      setIsLoadingSchedules(true);
      setIsLoading(true);
      setError(null);

      // Get schedules for a range around the current date (e.g., current month)
      const startDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const endDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

      console.log('Loading schedules for date range:', {
        startDate: startDate.toISOString().split('T')[0],
        endDate: endDate.toISOString().split('T')[0]
      });

      // Check if we have a valid token before making the request
      const token = localStorage.getItem('elevate_auth_token');
      if (!token) {
        console.error('No authentication token found');
        setError('Please log in to view your schedules');
        return;
      }

      console.log('Making API request with token:', token ? 'present' : 'missing');

      const response = await scheduleService.getSchedules({
        startDate: startDate.toISOString().split('T')[0],
        endDate: endDate.toISOString().split('T')[0]
      });

      console.log('Schedule API response:', response);

      // The API returns the schedules array directly, not wrapped in success/data
      if (Array.isArray(response)) {
        console.log('Successfully loaded schedules:', response);

        // Convert date strings back to Date objects

        const schedulesWithDates = response.map(schedule => ({
          ...schedule,
          date: new Date(schedule.date),
          tasks: Array.isArray(schedule.tasks) ? schedule.tasks.map((task, index) => {
            // Helper function to parse time strings safely
            const parseTime = (timeStr: string | Date) => {
              if (!timeStr) return new Date();
              if (timeStr instanceof Date) return timeStr;

              // Convert to string if it's not already
              const timeString = String(timeStr);

              // Handle local datetime format (without Z suffix)
              if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(timeString)) {
                // This is a local datetime string like "2025-08-04T09:00:00"
                // Parse it as a local time, not UTC
                const parsed = new Date(timeString);
                if (!isNaN(parsed.getTime())) {
                  return parsed;
                }
              }

              // Handle UTC datetime format (with Z suffix)
              if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$/.test(timeString)) {
                // This is a UTC datetime string like "2025-08-04T09:00:00.000Z"
                // Parse it as UTC and convert to local time
                const parsed = new Date(timeString);
                if (!isNaN(parsed.getTime())) {
                  return parsed;
                }
              }

              // Try parsing as ISO string (fallback)
              const parsed = new Date(timeString);
              if (!isNaN(parsed.getTime())) {
                return parsed;
              }

              // If that fails, try to handle other formats
              // Check if it's just a time like "09:00"
              if (/^\d{2}:\d{2}$/.test(timeString)) {
                const today = new Date().toISOString().split('T')[0];
                const fullDateTime = `${today}T${timeString}:00`;
                const reparsed = new Date(fullDateTime);
                if (!isNaN(reparsed.getTime())) {
                  return reparsed;
                }
              }

              // If that fails, return current time as fallback
              return new Date();
            };

            const startTimeValue = task.start_time || task.startTime;
            const endTimeValue = task.end_time || task.endTime;

            const parsedStartTime = parseTime(startTimeValue);
            const parsedEndTime = parseTime(endTimeValue);

            return {
              ...task,
              id: task.id || `task-${index}`, // Ensure each task has an id
              startTime: parsedStartTime,
              endTime: parsedEndTime,
              // Map snake_case fields from database to camelCase for frontend
              estimatedDuration: task.estimated_duration || task.estimatedDuration,
              actualDuration: task.actual_duration || task.actualDuration,
              isCompleted: task.is_completed || task.isCompleted || false
            };
          }) : []
        }));


        setSchedules(schedulesWithDates);
      } else if (response && typeof response === 'object' && 'success' in response) {
        // Handle wrapped response format (if API changes)
        if (response.success && response.data) {
          console.log('Successfully loaded schedules (wrapped):', response.data);

          if (!Array.isArray(response.data)) {
            console.warn('Response data is not an array:', response.data);
            setSchedules([]);
            return;
          }

          const schedulesWithDates = response.data.map(schedule => ({
            ...schedule,
            date: new Date(schedule.date),
            tasks: Array.isArray(schedule.tasks) ? schedule.tasks.map(task => ({
              ...task,
              startTime: new Date(task.startTime),
              endTime: new Date(task.endTime)
            })) : []
          }));

          setSchedules(schedulesWithDates);
        } else {
          setError(response.error || 'Failed to load schedules from server');
        }
      } else {
        console.error('Unexpected response format:', response);
        setError('Unexpected response format from server');
      }
    } catch (error) {
      console.error('Error loading schedules:', error);

      // Handle specific error types
      if (error instanceof Error) {
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
          console.error('Authentication error - token may be expired');
          setError('Authentication expired. Please refresh the page and log in again.');

          // Optionally clear the invalid token
          localStorage.removeItem('elevate_auth_token');
        } else if (error.message.includes('403') || error.message.includes('Forbidden')) {
          setError('Access denied. You may not have permission to view schedules.');
        } else if (error.message.includes('404')) {
          setError('Schedule service not found. Please try again later.');
        } else if (error.message.includes('500')) {
          setError('Server error. Please try again later.');
        } else {
          setError(`Failed to load schedules: ${error.message}`);
        }
      } else {
        setError('Failed to load schedules. Please try again.');
      }
    } finally {
      setIsLoading(false);
      setIsLoadingSchedules(false);
    }
  };

  // Load schedules when component mounts or date changes
  useEffect(() => {
    loadSchedules();
  }, [currentDate]);

  // Delete schedule function
  const deleteSchedule = async (scheduleId: string) => {
    if (!confirm('Are you sure you want to delete this schedule? This action cannot be undone.')) {
      return;
    }

    try {
      setIsDeleting(true);

      const response = await scheduleService.deleteSchedule(scheduleId);

      console.log('Delete response:', response);

      // The delete API returns {message: "Schedule deleted successfully"} directly
      if (response && (response.message || response.success)) {
        // Remove the deleted schedule from local state
        setSchedules(prevSchedules =>
          prevSchedules.filter(schedule => schedule.id !== scheduleId)
        );

        // Show success message
        alert('Schedule deleted successfully!');
      } else {
        console.error('Failed to delete schedule:', response);
        alert(`Failed to delete schedule: ${response?.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error deleting schedule:', error);
      if (error instanceof Error) {
        alert(`Failed to delete schedule: ${error.message}`);
      } else {
        alert('Failed to delete schedule. Please try again.');
      }
    } finally {
      setIsDeleting(false);
    }
  };

  // Mock schedule data for fallback (remove this once API is working)
  const mockSchedules: ScheduleType[] = [
    {
      id: '1',
      userId: 'user1',
      title: 'Productive Monday',
      description: 'AI-optimized schedule for maximum productivity',
      date: new Date('2024-01-15'),
      isGenerated: true,
      tasks: [
        {
          id: '1',
          title: 'Morning Workout',
          description: 'Cardio and strength training',
          startTime: new Date('2024-01-15T07:00:00'),
          endTime: new Date('2024-01-15T08:00:00'),
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
          startTime: new Date('2024-01-15T09:00:00'),
          endTime: new Date('2024-01-15T11:00:00'),
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
          startTime: new Date('2024-01-15T11:30:00'),
          endTime: new Date('2024-01-15T12:30:00'),
          category: ActivityCategory.WORK,
          priority: Priority.MEDIUM,
          isCompleted: true,
          estimatedDuration: 60,
          actualDuration: 65
        },
        {
          id: '4',
          title: 'Lunch Break',
          description: 'Healthy meal and short walk',
          startTime: new Date('2024-01-15T12:30:00'),
          endTime: new Date('2024-01-15T13:30:00'),
          category: ActivityCategory.PERSONAL,
          priority: Priority.MEDIUM,
          isCompleted: true,
          estimatedDuration: 60,
          actualDuration: 60
        },
        {
          id: '5',
          title: 'Code Review',
          description: 'Review pull requests from team members',
          startTime: new Date('2024-01-15T14:00:00'),
          endTime: new Date('2024-01-15T15:00:00'),
          category: ActivityCategory.WORK,
          priority: Priority.MEDIUM,
          isCompleted: false,
          estimatedDuration: 60
        },
        {
          id: '6',
          title: 'Learning Session',
          description: 'React advanced patterns course',
          startTime: new Date('2024-01-15T19:00:00'),
          endTime: new Date('2024-01-15T20:30:00'),
          category: ActivityCategory.LEARNING,
          priority: Priority.LOW,
          isCompleted: false,
          estimatedDuration: 90
        }
      ],
      createdAt: new Date('2024-01-14T20:00:00'),
      updatedAt: new Date('2024-01-15T15:00:00')
    }
  ];

  const todaySchedule = schedules.find(s => 
    s.date.toDateString() === currentDate.toDateString()
  );

  const navigateDate = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    if (viewMode === 'day') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 1 : -1));
    } else {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
    }
    setCurrentDate(newDate);
  };

  const completedTasks = todaySchedule?.tasks.filter(t => t.isCompleted).length || 0;
  const totalTasks = todaySchedule?.tasks.length || 0;
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  // Handle task completion toggle
  const handleTaskToggle = async (taskId: string) => {
    try {
      // Find the task in the current schedule
      const scheduleIndex = schedules.findIndex(s =>
        s.date.toDateString() === currentDate.toDateString()
      );

      if (scheduleIndex === -1) return;

      const taskIndex = schedules[scheduleIndex].tasks.findIndex(t => t.id === taskId);
      if (taskIndex === -1) return;

      // Toggle the completion status locally
      const updatedSchedules = [...schedules];
      const currentTask = updatedSchedules[scheduleIndex].tasks[taskIndex];
      updatedSchedules[scheduleIndex].tasks[taskIndex] = {
        ...currentTask,
        isCompleted: !currentTask.isCompleted
      };

      setSchedules(updatedSchedules);

      // TODO: Update the backend with the new completion status
      // This would typically call an API endpoint to update the task
      console.log(`Task ${taskId} completion toggled to: ${!currentTask.isCompleted}`);

    } catch (error) {
      console.error('Error toggling task completion:', error);
      // Optionally show an error message to the user
    }
  };

  const handleGenerateSchedule = async (request: ScheduleGenerationRequest) => {
    setIsGenerating(true);
    try {
      console.log('Sending schedule generation request:', JSON.stringify(request, null, 2));

      const response = await scheduleService.generateAISchedule(request);

      if (response.success && response.schedule) {
        console.log('Schedule generated successfully:', response.schedule);
        // Here you would typically update your schedules state with the new schedule
        // For now, we'll just show an alert
        alert('Schedule generated successfully! Check the console for details.');
        setShowGenerator(false);
      } else {
        console.error('Schedule generation failed:', response.error);
        alert(`Failed to generate schedule: ${response.error}`);
      }
    } catch (error) {
      console.error('Error generating schedule:', error);
      alert('An error occurred while generating the schedule. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-black">Schedule</h1>
          <p className="text-black mt-1">
            Manage your daily schedule and tasks
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" icon={<Download size={16} />}>
            Export
          </Button>
          <Button variant="outline" icon={<Settings size={16} />}>
            Preferences
          </Button>
          <Link to="/schedule/create">
            <Button variant="outline" icon={<Plus size={16} />}>
              Create Schedule
            </Button>
          </Link>
          <Button onClick={() => setShowGenerator(true)} icon={<Brain size={16} />}>
            Generate with AI
          </Button>
        </div>
      </div>

      {/* Date Navigation */}
      <Card>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <IconButton
                variant="outline"
                size="sm"
                icon={<ChevronLeft size={16} />}
                onClick={() => navigateDate('prev')}
              />
              <h2 className="text-lg font-semibold text-primary-800 min-w-[200px] text-center">
                {formatDate(currentDate)}
              </h2>
              <IconButton
                variant="outline"
                size="sm"
                icon={<ChevronRight size={16} />}
                onClick={() => navigateDate('next')}
              />
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentDate(new Date())}
            >
              Today
            </Button>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant={viewMode === 'day' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setViewMode('day')}
            >
              Day
            </Button>
            <Button
              variant={viewMode === 'week' ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setViewMode('week')}
            >
              Week
            </Button>
          </div>
        </div>
      </Card>

      {/* Schedule Overview */}
      {todaySchedule && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-blue-50 rounded-lg">
                <Calendar className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-800">Total Tasks</p>
                <p className="text-2xl font-bold text-gray-900">{totalTasks}</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-green-50 rounded-lg">
                <Clock className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-800">Completed</p>
                <p className="text-2xl font-bold text-gray-900">{completedTasks}</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center">
              <div className="p-2 bg-purple-50 rounded-lg">
                <Brain className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-800">Completion Rate</p>
                <p className="text-2xl font-bold text-gray-900">{completionRate}%</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Schedule Content */}
      {isLoading ? (
        <Card>
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-primary-700">Loading schedule...</p>
          </div>
        </Card>
      ) : error ? (
        <Card>
          <div className="text-center py-12">
            <div className="mx-auto h-12 w-12 text-red-400 mb-4">⚠️</div>
            <h3 className="text-lg font-medium text-red-600 mb-2">
              Error Loading Schedule
            </h3>
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={loadSchedules} variant="outline">
              Try Again
            </Button>
          </div>
        </Card>
      ) : todaySchedule ? (
        <Card
          title={todaySchedule.title}
          subtitle={todaySchedule.description}
          action={
            <div className="flex items-center space-x-3">
              {todaySchedule.isGenerated && (
                <div className="flex items-center space-x-2 text-sm text-primary-600">
                  <Brain size={14} />
                  <span>AI Generated</span>
                </div>
              )}
              <Button
                variant="outline"
                size="sm"
                icon={<Trash2 size={14} />}
                onClick={() => deleteSchedule(todaySchedule.id)}
                disabled={isDeleting}
                className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
              >
                {isDeleting ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          }
        >
          <div className="space-y-4">
            {todaySchedule.tasks.map((task) => (
              <TaskCard key={task.id} task={task} onToggleComplete={handleTaskToggle} />
            ))}
          </div>
        </Card>
      ) : (
        <Card>
          <div className="text-center py-12">
            <Calendar className="mx-auto h-12 w-12 text-secondary-400 mb-4" />
            <h3 className="text-lg font-medium text-primary-800 mb-2">
              No schedule for this day
            </h3>
            <p className="text-black mb-4">
              Create a new schedule or generate one with AI
            </p>
            <div className="flex justify-center space-x-3">
              <Link to="/schedule/create">
                <Button variant="outline" icon={<Plus size={16} />}>
                  Create Schedule
                </Button>
              </Link>
              <Button onClick={() => setShowGenerator(true)} icon={<Brain size={16} />}>
                Generate with AI
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Schedule Generator Form */}
      {showGenerator && (
        <ScheduleGenerationForm
          onSubmit={handleGenerateSchedule}
          onCancel={() => setShowGenerator(false)}
          isLoading={isGenerating}
          initialDate={currentDate}
        />
      )}
    </div>
  );
};

interface TaskCardProps {
  task: ScheduleTask;
  onToggleComplete: (taskId: string) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onToggleComplete }) => {
  return (
    <div className={`flex items-center space-x-4 p-4 rounded-lg border transition-colors ${
      task.isCompleted 
        ? 'bg-green-50 border-green-200' 
        : 'bg-white border-secondary-200 hover:bg-secondary-50'
    }`}>
      {/* Completion Checkbox */}
      <div className="flex-shrink-0">
        <button
          onClick={() => onToggleComplete(task.id)}
          className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1 ${
            task.isCompleted
              ? 'bg-green-600 border-green-600 hover:bg-green-700 hover:border-green-700'
              : 'border-gray-600 hover:border-gray-800 hover:bg-gray-50'
          }`}
          title={task.isCompleted ? 'Mark as incomplete' : 'Mark as complete'}
        >
          {task.isCompleted && (
            <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          )}
        </button>
      </div>

      {/* Task Details */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h4 className={`text-sm font-medium ${
              task.isCompleted ? 'text-green-800 line-through' : 'text-primary-800'
            }`}>
              {task.title}
            </h4>
            {task.description && (
              <p className={`text-sm mt-1 ${
                task.isCompleted ? 'text-green-600' : 'text-primary-700'
              }`}>
                {task.description}
              </p>
            )}
            <div className="flex items-center space-x-3 mt-2">
              <span className="text-sm text-gray-800">
                {formatTime(task.startTime)} - {formatTime(task.endTime)}
              </span>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(task.category)}`}>
                {getCategoryIcon(task.category)} {task.category}
              </span>
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                {task.priority}
              </span>
            </div>
          </div>
          <div className="text-right text-sm text-gray-800">
            <p>{formatDuration(task.estimatedDuration)}</p>
            {task.actualDuration && (
              <p className="text-xs">
                Actual: {formatDuration(task.actualDuration)}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
