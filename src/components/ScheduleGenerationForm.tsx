import React, { useState } from 'react';
import { Plus, Trash2, Clock, AlertCircle, Brain, X } from 'lucide-react';
import { Button, Input, Select, Card } from './';
import { ScheduleGenerationRequest, ScheduleActivity, ScheduleConstraints } from '../types/scheduleGeneration';
import { cn } from '../utils';

interface ScheduleGenerationFormProps {
  onSubmit: (data: ScheduleGenerationRequest) => void;
  onCancel: () => void;
  isLoading?: boolean;
  initialDate?: Date;
}

export const ScheduleGenerationForm: React.FC<ScheduleGenerationFormProps> = ({
  onSubmit,
  onCancel,
  isLoading = false,
  initialDate = new Date()
}) => {
  const [formData, setFormData] = useState<ScheduleGenerationRequest>({
    date: initialDate.toISOString().split('T')[0],
    wakeUpTime: '07:00',
    activities: [
      { name: 'Email review', durationMinutes: 30, priority: 2 },
      { name: 'Team meeting', durationMinutes: 60, priority: 1, timeWindow: ['09:00', '11:00'] }
    ],
    constraints: {
      lunchBreak: true,
      maxConsecutiveWorkHours: 4,
      lunchBreakDuration: 60,
      lunchBreakTimeWindow: ['12:00', '14:00'],
      workStartTime: '08:00',
      workEndTime: '18:00',
      breakDuration: 15,
      allowOvertime: false
    }
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const priorityOptions = [
    { value: '1', label: '1 - Highest Priority' },
    { value: '2', label: '2 - High Priority' },
    { value: '3', label: '3 - Medium Priority' },
    { value: '4', label: '4 - Low Priority' },
    { value: '5', label: '5 - Lowest Priority' }
  ];

  const addActivity = () => {
    setFormData(prev => ({
      ...prev,
      activities: [
        ...prev.activities,
        { name: '', durationMinutes: 60, priority: 3 }
      ]
    }));
  };

  const removeActivity = (index: number) => {
    setFormData(prev => ({
      ...prev,
      activities: prev.activities.filter((_, i) => i !== index)
    }));
  };

  const updateActivity = (index: number, field: keyof ScheduleActivity, value: any) => {
    setFormData(prev => ({
      ...prev,
      activities: prev.activities.map((activity, i) => 
        i === index ? { ...activity, [field]: value } : activity
      )
    }));
  };

  const updateConstraints = (field: keyof ScheduleConstraints, value: any) => {
    setFormData(prev => ({
      ...prev,
      constraints: { ...prev.constraints, [field]: value }
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    // Validate date
    if (!formData.date) {
      newErrors.date = 'Date is required';
    }

    // Validate wake up time
    if (!formData.wakeUpTime) {
      newErrors.wakeUpTime = 'Wake up time is required';
    }

    // Validate activities
    formData.activities.forEach((activity, index) => {
      if (!activity.name.trim()) {
        newErrors[`activity_${index}_name`] = 'Activity name is required';
      }
      if (activity.durationMinutes <= 0) {
        newErrors[`activity_${index}_duration`] = 'Duration must be greater than 0';
      }
      if (activity.priority < 1 || activity.priority > 5) {
        newErrors[`activity_${index}_priority`] = 'Priority must be between 1 and 5';
      }
    });

    // Validate constraints
    if (formData.constraints.maxConsecutiveWorkHours <= 0) {
      newErrors.maxConsecutiveWorkHours = 'Max consecutive work hours must be greater than 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      // Clean up activities - remove empty time windows
      const cleanedData = {
        ...formData,
        activities: formData.activities.map(activity => {
          const cleaned = { ...activity };
          if (cleaned.timeWindow && (!cleaned.timeWindow[0] || !cleaned.timeWindow[1])) {
            delete cleaned.timeWindow;
          }
          return cleaned;
        })
      };
      
      onSubmit(cleanedData);
    }
  };

  const totalDuration = formData.activities.reduce((sum, activity) => sum + activity.durationMinutes, 0);
  const totalHours = Math.floor(totalDuration / 60);
  const totalMinutes = totalDuration % 60;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-secondary-900">
              Generate AI Schedule
            </h2>
            <p className="text-sm text-secondary-600 mt-1">
              Configure your preferences for AI-powered schedule generation
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onCancel}
            icon={<X size={16} />}
          />
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Settings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input
              label="Date"
              type="date"
              value={formData.date}
              onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
              error={errors.date}
              required
            />
            <Input
              label="Wake Up Time"
              type="time"
              value={formData.wakeUpTime}
              onChange={(e) => setFormData(prev => ({ ...prev, wakeUpTime: e.target.value }))}
              error={errors.wakeUpTime}
              leftIcon={<Clock size={16} />}
              required
            />
          </div>

          {/* Activities Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-secondary-900">Activities</h3>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-secondary-600">
                  Total: {totalHours}h {totalMinutes}m
                </span>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addActivity}
                  icon={<Plus size={16} />}
                >
                  Add Activity
                </Button>
              </div>
            </div>

            <div className="space-y-4">
              {formData.activities.map((activity, index) => (
                <div key={index} className="p-4 border border-secondary-200 rounded-lg space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-secondary-900">Activity {index + 1}</h4>
                    {formData.activities.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeActivity(index)}
                        icon={<Trash2 size={16} />}
                      />
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Input
                      label="Activity Name"
                      value={activity.name}
                      onChange={(e) => updateActivity(index, 'name', e.target.value)}
                      placeholder="e.g., Team meeting"
                      error={errors[`activity_${index}_name`]}
                      required
                    />
                    <Input
                      label="Duration (minutes)"
                      type="number"
                      value={activity.durationMinutes}
                      onChange={(e) => updateActivity(index, 'durationMinutes', parseInt(e.target.value) || 0)}
                      min="1"
                      max="480"
                      error={errors[`activity_${index}_duration`]}
                      required
                    />
                    <Select
                      label="Priority"
                      value={activity.priority.toString()}
                      onChange={(e) => updateActivity(index, 'priority', parseInt(e.target.value))}
                      options={priorityOptions}
                      error={errors[`activity_${index}_priority`]}
                      required
                    />
                  </div>

                  {/* Optional Time Window */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-secondary-700">
                      Time Window (Optional)
                    </label>
                    <div className="grid grid-cols-2 gap-4">
                      <Input
                        type="time"
                        value={activity.timeWindow?.[0] || ''}
                        onChange={(e) => {
                          const newTimeWindow: [string, string] = [
                            e.target.value,
                            activity.timeWindow?.[1] || ''
                          ];
                          updateActivity(index, 'timeWindow', newTimeWindow);
                        }}
                        placeholder="Start time"
                      />
                      <Input
                        type="time"
                        value={activity.timeWindow?.[1] || ''}
                        onChange={(e) => {
                          const newTimeWindow: [string, string] = [
                            activity.timeWindow?.[0] || '',
                            e.target.value
                          ];
                          updateActivity(index, 'timeWindow', newTimeWindow);
                        }}
                        placeholder="End time"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Constraints Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-secondary-900">Constraints</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="lunchBreak"
                    checked={formData.constraints.lunchBreak}
                    onChange={(e) => updateConstraints('lunchBreak', e.target.checked)}
                    className="w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
                  />
                  <label htmlFor="lunchBreak" className="text-sm font-medium text-secondary-700">
                    Include lunch break
                  </label>
                </div>

                <Input
                  label="Max Consecutive Work Hours"
                  type="number"
                  value={formData.constraints.maxConsecutiveWorkHours}
                  onChange={(e) => updateConstraints('maxConsecutiveWorkHours', parseInt(e.target.value) || 0)}
                  min="1"
                  max="8"
                  error={errors.maxConsecutiveWorkHours}
                  required
                />

                <Input
                  label="Work Start Time"
                  type="time"
                  value={formData.constraints.workStartTime || ''}
                  onChange={(e) => updateConstraints('workStartTime', e.target.value)}
                />

                <Input
                  label="Work End Time"
                  type="time"
                  value={formData.constraints.workEndTime || ''}
                  onChange={(e) => updateConstraints('workEndTime', e.target.value)}
                />
              </div>

              <div className="space-y-4">
                {formData.constraints.lunchBreak && (
                  <>
                    <Input
                      label="Lunch Break Duration (minutes)"
                      type="number"
                      value={formData.constraints.lunchBreakDuration || 60}
                      onChange={(e) => updateConstraints('lunchBreakDuration', parseInt(e.target.value) || 60)}
                      min="30"
                      max="120"
                    />
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-secondary-700">
                        Lunch Break Time Window
                      </label>
                      <div className="grid grid-cols-2 gap-4">
                        <Input
                          type="time"
                          value={formData.constraints.lunchBreakTimeWindow?.[0] || '12:00'}
                          onChange={(e) => {
                            const newWindow: [string, string] = [
                              e.target.value,
                              formData.constraints.lunchBreakTimeWindow?.[1] || '14:00'
                            ];
                            updateConstraints('lunchBreakTimeWindow', newWindow);
                          }}
                          placeholder="Start"
                        />
                        <Input
                          type="time"
                          value={formData.constraints.lunchBreakTimeWindow?.[1] || '14:00'}
                          onChange={(e) => {
                            const newWindow: [string, string] = [
                              formData.constraints.lunchBreakTimeWindow?.[0] || '12:00',
                              e.target.value
                            ];
                            updateConstraints('lunchBreakTimeWindow', newWindow);
                          }}
                          placeholder="End"
                        />
                      </div>
                    </div>
                  </>
                )}

                <Input
                  label="Break Duration Between Activities (minutes)"
                  type="number"
                  value={formData.constraints.breakDuration || 15}
                  onChange={(e) => updateConstraints('breakDuration', parseInt(e.target.value) || 15)}
                  min="0"
                  max="60"
                />

                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="allowOvertime"
                    checked={formData.constraints.allowOvertime || false}
                    onChange={(e) => updateConstraints('allowOvertime', e.target.checked)}
                    className="w-4 h-4 text-primary-600 border-secondary-300 rounded focus:ring-primary-500"
                  />
                  <label htmlFor="allowOvertime" className="text-sm font-medium text-secondary-700">
                    Allow scheduling beyond work hours
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Preview */}
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900">Schedule Preview</h4>
                <p className="text-sm text-blue-700 mt-1">
                  {formData.activities.length} activities totaling {totalHours}h {totalMinutes}m will be scheduled for {formData.date}
                </p>
              </div>
            </div>
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
              disabled={isLoading || formData.activities.length === 0}
              icon={<Brain size={16} />}
            >
              Generate Schedule
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};
