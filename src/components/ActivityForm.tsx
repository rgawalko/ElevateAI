import React, { useState } from 'react';
import { X, Clock, Tag, Smile, Zap } from 'lucide-react';
import { Button, Input, Textarea, Select, Card } from './';
import { ActivityCategory, MoodLevel, EnergyLevel, ActivityFormData } from '../types';
import { cn, getCategoryIcon } from '../utils';

interface ActivityFormProps {
  onSubmit: (data: ActivityFormData) => void;
  onCancel: () => void;
  initialData?: Partial<ActivityFormData>;
  isLoading?: boolean;
}

export const ActivityForm: React.FC<ActivityFormProps> = ({
  onSubmit,
  onCancel,
  initialData,
  isLoading = false
}) => {
  const [formData, setFormData] = useState<ActivityFormData>({
    title: initialData?.title || '',
    description: initialData?.description || '',
    category: initialData?.category || ActivityCategory.WORK,
    duration: initialData?.duration || 30,
    startTime: initialData?.startTime || new Date(),
    mood: initialData?.mood,
    energyLevel: initialData?.energyLevel,
    tags: initialData?.tags || []
  });

  const [newTag, setNewTag] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const categoryOptions = Object.values(ActivityCategory).map(category => ({
    value: category,
    label: `${getCategoryIcon(category)} ${category.charAt(0).toUpperCase() + category.slice(1)}`
  }));

  const moodOptions = [
    { value: '', label: 'Select mood (optional)' },
    { value: MoodLevel.VERY_LOW.toString(), label: '😢 Very Low' },
    { value: MoodLevel.LOW.toString(), label: '😕 Low' },
    { value: MoodLevel.NEUTRAL.toString(), label: '😐 Neutral' },
    { value: MoodLevel.GOOD.toString(), label: '😊 Good' },
    { value: MoodLevel.EXCELLENT.toString(), label: '😄 Excellent' }
  ];

  const energyOptions = [
    { value: '', label: 'Select energy level (optional)' },
    { value: EnergyLevel.VERY_LOW.toString(), label: '🔋 Very Low' },
    { value: EnergyLevel.LOW.toString(), label: '🔋 Low' },
    { value: EnergyLevel.MODERATE.toString(), label: '🔋 Moderate' },
    { value: EnergyLevel.HIGH.toString(), label: '🔋 High' },
    { value: EnergyLevel.VERY_HIGH.toString(), label: '⚡ Very High' }
  ];

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Activity title is required';
    }

    if (formData.duration <= 0) {
      newErrors.duration = 'Duration must be greater than 0';
    }

    if (formData.duration > 1440) {
      newErrors.duration = 'Duration cannot exceed 24 hours (1440 minutes)';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleAddTag = () => {
    if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const formatDateTime = (date: Date): string => {
    return date.toISOString().slice(0, 16);
  };

  return (
    <Card className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-primary-900">
          {initialData ? 'Edit Activity' : 'Log New Activity'}
        </h2>
        <Button
          variant="ghost"
          size="sm"
          onClick={onCancel}
          icon={<X size={16} />}
        />
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
        <Input
          label="Activity Title"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          placeholder="e.g., Morning workout, Team meeting, Code review"
          error={errors.title}
          required
        />

        {/* Description */}
        <Textarea
          label="Description (Optional)"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          placeholder="Add any additional details about this activity..."
          rows={3}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Category */}
          <Select
            label="Category"
            value={formData.category}
            onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as ActivityCategory }))}
            options={categoryOptions}
            required
          />

          {/* Duration */}
          <Input
            label="Duration (minutes)"
            type="number"
            value={formData.duration}
            onChange={(e) => setFormData(prev => ({ ...prev, duration: parseInt(e.target.value) || 0 }))}
            min="1"
            max="1440"
            error={errors.duration}
            leftIcon={<Clock size={16} />}
            required
          />
        </div>

        {/* Start Time */}
        <Input
          label="Start Time"
          type="datetime-local"
          value={formatDateTime(formData.startTime)}
          onChange={(e) => setFormData(prev => ({ ...prev, startTime: new Date(e.target.value) }))}
          required
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Mood */}
          <Select
            label="Mood"
            value={formData.mood?.toString() || ''}
            onChange={(e) => setFormData(prev => ({ 
              ...prev, 
              mood: e.target.value ? parseInt(e.target.value) as MoodLevel : undefined 
            }))}
            options={moodOptions}
            leftIcon={<Smile size={16} />}
          />

          {/* Energy Level */}
          <Select
            label="Energy Level"
            value={formData.energyLevel?.toString() || ''}
            onChange={(e) => setFormData(prev => ({ 
              ...prev, 
              energyLevel: e.target.value ? parseInt(e.target.value) as EnergyLevel : undefined 
            }))}
            options={energyOptions}
            leftIcon={<Zap size={16} />}
          />
        </div>

        {/* Tags */}
        <div className="space-y-3">
          <label className="text-sm font-medium text-primary-800">
            Tags (Optional)
          </label>
          
          <div className="flex space-x-2">
            <Input
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              placeholder="Add a tag..."
              leftIcon={<Tag size={16} />}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleAddTag();
                }
              }}
            />
            <Button
              type="button"
              variant="outline"
              onClick={handleAddTag}
              disabled={!newTag.trim()}
            >
              Add
            </Button>
          </div>

          {formData.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {formData.tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-800"
                >
                  {tag}
                  <button
                    type="button"
                    onClick={() => handleRemoveTag(tag)}
                    className="ml-2 text-primary-600 hover:text-primary-800"
                  >
                    <X size={14} />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Form Actions */}
        <div className="flex justify-end space-x-3 pt-6 border-t border-secondary-200">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            loading={isLoading}
            disabled={isLoading}
          >
            {initialData ? 'Update Activity' : 'Log Activity'}
          </Button>
        </div>
      </form>
    </Card>
  );
};
