import { ActivityCategory, MoodLevel, EnergyLevel } from './index';

// Form-specific types
export interface ActivityFormData {
  title: string;
  description?: string;
  category: ActivityCategory;
  duration: number;
  startTime: Date;
  mood?: MoodLevel;
  energyLevel?: EnergyLevel;
  tags: string[];
}
