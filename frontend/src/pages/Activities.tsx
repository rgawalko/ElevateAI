import React, { useState } from 'react';
import { Plus, Download, Upload, BarChart3 } from 'lucide-react';
import { Button, Card } from '../components';
import { ActivityForm } from '../components/ActivityForm';
import { ActivityList } from '../components/ActivityList';
import type { Activity, ActivityFormData } from '../types';
import { ActivityCategory, MoodLevel, EnergyLevel } from '../types';
import { generateId } from '../utils';

export const Activities: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [editingActivity, setEditingActivity] = useState<Activity | null>(null);
  const [activities, setActivities] = useState<Activity[]>([
    // Mock data - in a real app, this would come from API/state management
    {
      id: '1',
      userId: 'user1',
      title: 'Morning Workout',
      description: 'Cardio and strength training session',
      category: ActivityCategory.EXERCISE,
      duration: 60,
      startTime: new Date('2024-01-15T07:00:00'),
      endTime: new Date('2024-01-15T08:00:00'),
      mood: MoodLevel.GOOD,
      energyLevel: EnergyLevel.HIGH,
      productivityScore: 8,
      tags: ['fitness', 'morning', 'cardio'],
      createdAt: new Date('2024-01-15T08:00:00'),
      updatedAt: new Date('2024-01-15T08:00:00')
    },
    {
      id: '2',
      userId: 'user1',
      title: 'Project Planning Meeting',
      description: 'Quarterly planning session with the team',
      category: ActivityCategory.WORK,
      duration: 90,
      startTime: new Date('2024-01-15T09:00:00'),
      endTime: new Date('2024-01-15T10:30:00'),
      mood: MoodLevel.NEUTRAL,
      energyLevel: EnergyLevel.MODERATE,
      productivityScore: 7,
      tags: ['meeting', 'planning', 'team'],
      createdAt: new Date('2024-01-15T10:30:00'),
      updatedAt: new Date('2024-01-15T10:30:00')
    },
    {
      id: '3',
      userId: 'user1',
      title: 'Lunch with Colleagues',
      description: 'Team lunch at the new restaurant downtown',
      category: ActivityCategory.SOCIAL,
      duration: 45,
      startTime: new Date('2024-01-15T12:00:00'),
      endTime: new Date('2024-01-15T12:45:00'),
      mood: MoodLevel.GOOD,
      energyLevel: EnergyLevel.MODERATE,
      tags: ['lunch', 'team', 'social'],
      createdAt: new Date('2024-01-15T12:45:00'),
      updatedAt: new Date('2024-01-15T12:45:00')
    },
    {
      id: '4',
      userId: 'user1',
      title: 'Code Review',
      description: 'Reviewing pull requests for the new feature',
      category: ActivityCategory.WORK,
      duration: 30,
      startTime: new Date('2024-01-15T14:00:00'),
      endTime: new Date('2024-01-15T14:30:00'),
      mood: MoodLevel.GOOD,
      energyLevel: EnergyLevel.HIGH,
      productivityScore: 9,
      tags: ['coding', 'review', 'development'],
      createdAt: new Date('2024-01-15T14:30:00'),
      updatedAt: new Date('2024-01-15T14:30:00')
    },
    {
      id: '5',
      userId: 'user1',
      title: 'Learning React Hooks',
      description: 'Online course on advanced React patterns',
      category: ActivityCategory.LEARNING,
      duration: 120,
      startTime: new Date('2024-01-15T19:00:00'),
      endTime: new Date('2024-01-15T21:00:00'),
      mood: MoodLevel.EXCELLENT,
      energyLevel: EnergyLevel.HIGH,
      productivityScore: 8,
      tags: ['learning', 'react', 'programming'],
      createdAt: new Date('2024-01-15T21:00:00'),
      updatedAt: new Date('2024-01-15T21:00:00')
    }
  ]);

  const handleCreateActivity = (formData: ActivityFormData) => {
    const newActivity: Activity = {
      id: generateId(),
      userId: 'user1', // In a real app, this would come from auth context
      title: formData.title,
      description: formData.description,
      category: formData.category,
      duration: formData.duration,
      startTime: formData.startTime,
      endTime: new Date(formData.startTime.getTime() + formData.duration * 60000),
      mood: formData.mood,
      energyLevel: formData.energyLevel,
      tags: formData.tags,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    setActivities(prev => [newActivity, ...prev]);
    setShowForm(false);
  };

  const handleUpdateActivity = (formData: ActivityFormData) => {
    if (!editingActivity) return;

    const updatedActivity: Activity = {
      ...editingActivity,
      title: formData.title,
      description: formData.description,
      category: formData.category,
      duration: formData.duration,
      startTime: formData.startTime,
      endTime: new Date(formData.startTime.getTime() + formData.duration * 60000),
      mood: formData.mood,
      energyLevel: formData.energyLevel,
      tags: formData.tags,
      updatedAt: new Date()
    };

    setActivities(prev => 
      prev.map(activity => 
        activity.id === editingActivity.id ? updatedActivity : activity
      )
    );
    setEditingActivity(null);
  };

  const handleEditActivity = (activity: Activity) => {
    setEditingActivity(activity);
  };

  const handleDeleteActivity = (activityId: string) => {
    if (window.confirm('Are you sure you want to delete this activity?')) {
      setActivities(prev => prev.filter(activity => activity.id !== activityId));
    }
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingActivity(null);
  };

  const totalActivities = activities.length;
  const totalTime = activities.reduce((sum, activity) => sum + activity.duration, 0);
  const averageProductivity = activities
    .filter(a => a.productivityScore)
    .reduce((sum, a) => sum + (a.productivityScore || 0), 0) / 
    activities.filter(a => a.productivityScore).length || 0;

  if (showForm || editingActivity) {
    return (
      <div className="space-y-6">
        <ActivityForm
          onSubmit={editingActivity ? handleUpdateActivity : handleCreateActivity}
          onCancel={handleCancelForm}
          initialData={editingActivity ? {
            title: editingActivity.title,
            description: editingActivity.description,
            category: editingActivity.category,
            duration: editingActivity.duration,
            startTime: editingActivity.startTime,
            mood: editingActivity.mood,
            energyLevel: editingActivity.energyLevel,
            tags: editingActivity.tags
          } : undefined}
        />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-primary-900 tracking-tight">Activities</h1>
          <p className="text-warm-neutral-900 mt-2 text-lg font-medium">
            Track and manage your daily activities
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" icon={<Download size={18} />} size="lg">
            Export
          </Button>
          <Button variant="outline" icon={<Upload size={18} />} size="lg">
            Import
          </Button>
          <Button onClick={() => setShowForm(true)} icon={<Plus size={18} />} size="lg">
            Log Activity
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card hover className="group">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="p-3 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-sm group-hover:shadow-md transition-all duration-200">
                <BarChart3 className="w-6 h-6 text-blue-600 transition-transform duration-200 group-hover:scale-110" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-semibold text-warm-neutral-800 uppercase tracking-wide">Total Activities</p>
                <p className="text-2xl font-bold text-primary-900 mt-1">{totalActivities}</p>
              </div>
            </div>
            <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <div className="w-2 h-8 bg-gradient-to-b from-blue-400 to-blue-600 rounded-full"></div>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-2 bg-green-50 rounded-lg">
              <BarChart3 className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-warm-neutral-800">Total Time</p>
              <p className="text-2xl font-bold text-primary-900">
                {Math.floor(totalTime / 60)}h {totalTime % 60}m
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center">
            <div className="p-2 bg-purple-50 rounded-lg">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-warm-neutral-800">Avg Productivity</p>
              <p className="text-2xl font-bold text-primary-900">
                {averageProductivity.toFixed(1)}/10
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Activities List */}
      <ActivityList
        activities={activities}
        onEdit={handleEditActivity}
        onDelete={handleDeleteActivity}
      />
    </div>
  );
};
