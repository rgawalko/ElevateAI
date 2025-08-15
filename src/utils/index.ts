import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { ActivityCategory, MoodLevel, EnergyLevel, Priority } from '../types';

// Utility function for combining Tailwind classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Date utilities
export const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(date);
};

export const formatTime = (date: Date): string => {
  // Handle invalid dates
  if (!date || isNaN(date.getTime())) {
    console.error('Invalid date passed to formatTime:', date);
    return 'Invalid Time';
  }

  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }).format(date);
};

export const formatDateTime = (date: Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  }).format(date);
};

export const formatDuration = (minutes: number): string => {
  // Handle invalid or missing duration values
  if (!minutes || isNaN(minutes) || minutes < 0) {
    return '0m';
  }

  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;

  if (hours === 0) {
    return `${mins}m`;
  } else if (mins === 0) {
    return `${hours}h`;
  } else {
    return `${hours}h ${mins}m`;
  }
};

export const getRelativeTime = (date: Date): string => {
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) {
    return 'just now';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  } else {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  }
};

// Activity utilities
export const getCategoryColor = (category: ActivityCategory): string => {
  const colors: Record<ActivityCategory, string> = {
    [ActivityCategory.WORK]: 'bg-blue-100 text-blue-800',
    [ActivityCategory.EXERCISE]: 'bg-green-100 text-green-800',
    [ActivityCategory.LEARNING]: 'bg-purple-100 text-purple-800',
    [ActivityCategory.SOCIAL]: 'bg-pink-100 text-pink-800',
    [ActivityCategory.PERSONAL]: 'bg-yellow-100 text-yellow-800',
    [ActivityCategory.HEALTH]: 'bg-red-100 text-red-800',
    [ActivityCategory.ENTERTAINMENT]: 'bg-indigo-100 text-indigo-800',
    [ActivityCategory.COMMUTE]: 'bg-gray-100 text-gray-800',
    [ActivityCategory.SLEEP]: 'bg-slate-100 text-slate-800',
    [ActivityCategory.MEALS]: 'bg-orange-100 text-orange-800',
  };
  return colors[category] || 'bg-gray-100 text-gray-800';
};

export const getCategoryIcon = (category: ActivityCategory): string => {
  const icons: Record<ActivityCategory, string> = {
    [ActivityCategory.WORK]: '💼',
    [ActivityCategory.EXERCISE]: '🏃‍♂️',
    [ActivityCategory.LEARNING]: '📚',
    [ActivityCategory.SOCIAL]: '👥',
    [ActivityCategory.PERSONAL]: '🏠',
    [ActivityCategory.HEALTH]: '🏥',
    [ActivityCategory.ENTERTAINMENT]: '🎬',
    [ActivityCategory.COMMUTE]: '🚗',
    [ActivityCategory.SLEEP]: '😴',
    [ActivityCategory.MEALS]: '🍽️',
  };
  return icons[category] || '📝';
};

export const getMoodEmoji = (mood: MoodLevel): string => {
  const emojis: Record<MoodLevel, string> = {
    [MoodLevel.VERY_LOW]: '😢',
    [MoodLevel.LOW]: '😕',
    [MoodLevel.NEUTRAL]: '😐',
    [MoodLevel.GOOD]: '😊',
    [MoodLevel.EXCELLENT]: '😄',
  };
  return emojis[mood] || '😐';
};

export const getEnergyEmoji = (energy: EnergyLevel): string => {
  const emojis: Record<EnergyLevel, string> = {
    [EnergyLevel.VERY_LOW]: '🔋',
    [EnergyLevel.LOW]: '🔋',
    [EnergyLevel.MODERATE]: '🔋',
    [EnergyLevel.HIGH]: '🔋',
    [EnergyLevel.VERY_HIGH]: '⚡',
  };
  return emojis[energy] || '🔋';
};

export const getPriorityColor = (priority: Priority): string => {
  const colors: Record<Priority, string> = {
    [Priority.LOW]: 'bg-gray-100 text-gray-800',
    [Priority.MEDIUM]: 'bg-yellow-100 text-yellow-800',
    [Priority.HIGH]: 'bg-orange-100 text-orange-800',
    [Priority.URGENT]: 'bg-red-100 text-red-800',
  };
  return colors[priority] || 'bg-gray-100 text-gray-800';
};

// Validation utilities
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPassword = (password: string): boolean => {
  return password.length >= 8;
};

// Local storage utilities
export const getFromStorage = <T>(key: string): T | null => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  } catch (error) {
    console.error(`Error getting ${key} from localStorage:`, error);
    return null;
  }
};

export const setToStorage = <T>(key: string, value: T): void => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error(`Error setting ${key} to localStorage:`, error);
  }
};

export const removeFromStorage = (key: string): void => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Error removing ${key} from localStorage:`, error);
  }
};

// Array utilities
export const groupBy = <T, K extends keyof any>(
  array: T[],
  key: (item: T) => K
): Record<K, T[]> => {
  return array.reduce((groups, item) => {
    const group = key(item);
    groups[group] = groups[group] || [];
    groups[group].push(item);
    return groups;
  }, {} as Record<K, T[]>);
};

// Number utilities
export const roundToDecimal = (num: number, decimals: number = 2): number => {
  return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
};

export const clamp = (value: number, min: number, max: number): number => {
  return Math.min(Math.max(value, min), max);
};

// Random utilities
export const generateId = (): string => {
  return Math.random().toString(36).substr(2, 9);
};

export const getRandomColor = (): string => {
  const colors = [
    'bg-red-100 text-red-800',
    'bg-blue-100 text-blue-800',
    'bg-green-100 text-green-800',
    'bg-yellow-100 text-yellow-800',
    'bg-purple-100 text-purple-800',
    'bg-pink-100 text-pink-800',
    'bg-indigo-100 text-indigo-800',
  ];
  return colors[Math.floor(Math.random() * colors.length)];
};
