import React, { useState } from 'react';
import { 
  Edit, 
  Trash2, 
  Filter, 
  Search, 
  Calendar,
  Clock,
  MoreVertical
} from 'lucide-react';
import { Card, Button, IconButton, Input, Select } from './';
import type { Activity } from '../types';
import { ActivityCategory } from '../types';
import { 
  formatDate, 
  formatTime, 
  formatDuration, 
  getCategoryColor, 
  getCategoryIcon,
  getMoodEmoji,
  getEnergyEmoji
} from '../utils';

interface ActivityListProps {
  activities: Activity[];
  onEdit?: (activity: Activity) => void;
  onDelete?: (activityId: string) => void;
  loading?: boolean;
}

export const ActivityList: React.FC<ActivityListProps> = ({
  activities,
  onEdit,
  onDelete,
  loading = false
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date' | 'duration' | 'category'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Filter and sort activities
  const filteredAndSortedActivities = React.useMemo(() => {
    let filtered = activities.filter(activity => {
      const matchesSearch = activity.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           activity.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           activity.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesCategory = filterCategory === 'all' || activity.category === filterCategory;
      
      return matchesSearch && matchesCategory;
    });

    // Sort activities
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'date':
          comparison = new Date(a.startTime).getTime() - new Date(b.startTime).getTime();
          break;
        case 'duration':
          comparison = a.duration - b.duration;
          break;
        case 'category':
          comparison = a.category.localeCompare(b.category);
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [activities, searchTerm, filterCategory, sortBy, sortOrder]);

  const categoryOptions = [
    { value: 'all', label: 'All Categories' },
    ...Object.values(ActivityCategory).map(category => ({
      value: category,
      label: `${getCategoryIcon(category)} ${category.charAt(0).toUpperCase() + category.slice(1)}`
    }))
  ];

  const sortOptions = [
    { value: 'date', label: 'Date' },
    { value: 'duration', label: 'Duration' },
    { value: 'category', label: 'Category' }
  ];

  if (loading) {
    return (
      <Card>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters and Search */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search activities..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              leftIcon={<Search size={16} />}
            />
          </div>
          
          <div className="flex gap-3">
            <Select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              options={categoryOptions}
            />
            
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'duration' | 'category')}
              options={sortOptions}
            />
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </Button>
          </div>
        </div>
      </Card>

      {/* Activities List */}
      {filteredAndSortedActivities.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <Calendar className="mx-auto h-12 w-12 text-warm-neutral-700 mb-4" />
            <h3 className="text-lg font-medium text-primary-900 mb-2">
              {searchTerm || filterCategory !== 'all' ? 'No matching activities' : 'No activities yet'}
            </h3>
            <p className="text-warm-neutral-800">
              {searchTerm || filterCategory !== 'all'
                ? 'Try adjusting your search or filters'
                : 'Start by logging your first activity'
              }
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredAndSortedActivities.map((activity) => (
            <ActivityCard
              key={activity.id}
              activity={activity}
              onEdit={onEdit}
              onDelete={onDelete}
            />
          ))}
        </div>
      )}

      {/* Summary */}
      {filteredAndSortedActivities.length > 0 && (
        <Card>
          <div className="flex items-center justify-between text-sm text-warm-neutral-800">
            <span>
              Showing {filteredAndSortedActivities.length} of {activities.length} activities
            </span>
            <span>
              Total time: {formatDuration(
                filteredAndSortedActivities.reduce((sum, activity) => sum + activity.duration, 0)
              )}
            </span>
          </div>
        </Card>
      )}
    </div>
  );
};

interface ActivityCardProps {
  activity: Activity;
  onEdit?: (activity: Activity) => void;
  onDelete?: (activityId: string) => void;
}

const ActivityCard: React.FC<ActivityCardProps> = ({ activity, onEdit, onDelete }) => {
  const [showMenu, setShowMenu] = useState(false);

  return (
    <Card hover className="relative">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4 flex-1">
          {/* Category Icon */}
          <div className="flex-shrink-0 mt-1">
            <span className="text-2xl">{getCategoryIcon(activity.category)}</span>
          </div>

          {/* Activity Details */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-medium text-primary-900 mb-1">
                  {activity.title}
                </h3>

                {activity.description && (
                  <p className="text-sm text-warm-neutral-800 mb-3">
                    {activity.description}
                  </p>
                )}

                <div className="flex items-center space-x-4 text-sm text-primary-800">
                  <span className="flex items-center">
                    <Calendar size={14} className="mr-1" />
                    {formatDate(activity.startTime)}
                  </span>
                  <span className="flex items-center">
                    <Clock size={14} className="mr-1" />
                    {formatTime(activity.startTime)} • {formatDuration(activity.duration)}
                  </span>
                </div>

                <div className="flex items-center space-x-3 mt-3">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(activity.category)}`}>
                    {activity.category}
                  </span>
                  
                  {activity.mood && (
                    <span className="flex items-center text-sm">
                      {getMoodEmoji(activity.mood)}
                      <span className="ml-1 text-warm-neutral-800">Mood</span>
                    </span>
                  )}
                  
                  {activity.energyLevel && (
                    <span className="flex items-center text-sm">
                      {getEnergyEmoji(activity.energyLevel)}
                      <span className="ml-1 text-warm-neutral-800">Energy</span>
                    </span>
                  )}
                </div>

                {activity.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {activity.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-2 py-1 rounded text-xs bg-secondary-100 text-primary-800"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Actions Menu */}
        {(onEdit || onDelete) && (
          <div className="relative">
            <IconButton
              variant="ghost"
              size="sm"
              icon={<MoreVertical size={16} />}
              onClick={() => setShowMenu(!showMenu)}
            />
            
            {showMenu && (
              <div className="absolute right-0 top-8 w-48 bg-white rounded-md shadow-lg border border-secondary-200 py-1 z-10">
                {onEdit && (
                  <button
                    onClick={() => {
                      onEdit(activity);
                      setShowMenu(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-primary-800 hover:bg-secondary-50"
                  >
                    <Edit size={14} className="mr-2" />
                    Edit Activity
                  </button>
                )}
                {onDelete && (
                  <button
                    onClick={() => {
                      onDelete(activity.id);
                      setShowMenu(false);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-danger-700 hover:bg-danger-50"
                  >
                    <Trash2 size={14} className="mr-2" />
                    Delete Activity
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
