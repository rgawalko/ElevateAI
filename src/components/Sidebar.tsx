import React from 'react';
import { 
  BarChart3, 
  Calendar, 
  Target, 
  Activity, 
  Brain, 
  Settings,
  HelpCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { cn } from '../utils';

interface SidebarProps {
  className?: string;
  collapsed?: boolean;
  onToggle?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  className, 
  collapsed = false, 
  onToggle 
}) => {
  return (
    <aside className={cn(
      "bg-white border-r border-secondary-200 transition-all duration-300",
      collapsed ? "w-16" : "w-64",
      className
    )}>
      <div className="flex flex-col h-full">
        {/* Toggle Button */}
        <div className="flex justify-end p-4">
          <button
            onClick={onToggle}
            className="p-1 text-secondary-400 hover:text-secondary-600 hover:bg-secondary-50 rounded transition-colors"
          >
            {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 pb-4">
          <div className="space-y-2">
            <SidebarItem
              icon={BarChart3}
              label="Dashboard"
              href="/dashboard"
              active
              collapsed={collapsed}
            />
            <SidebarItem
              icon={Activity}
              label="Activities"
              href="/activities"
              collapsed={collapsed}
            />
            <SidebarItem
              icon={Calendar}
              label="Schedule"
              href="/schedule"
              collapsed={collapsed}
            />
            <SidebarItem
              icon={Brain}
              label="AI Insights"
              href="/insights"
              collapsed={collapsed}
            />
            <SidebarItem
              icon={Target}
              label="Goals"
              href="/goals"
              collapsed={collapsed}
            />
          </div>

          {/* Divider */}
          <div className="my-6 border-t border-secondary-200"></div>

          {/* Secondary Navigation */}
          <div className="space-y-2">
            <SidebarItem
              icon={Settings}
              label="Settings"
              href="/settings"
              collapsed={collapsed}
            />
            <SidebarItem
              icon={HelpCircle}
              label="Help & Support"
              href="/help"
              collapsed={collapsed}
            />
          </div>
        </nav>

        {/* User Info */}
        {!collapsed && (
          <div className="p-4 border-t border-secondary-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">JD</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-secondary-900 truncate">
                  John Doe
                </p>
                <p className="text-xs text-secondary-500 truncate">
                  john@example.com
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};

interface SidebarItemProps {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  label: string;
  href: string;
  active?: boolean;
  collapsed?: boolean;
  badge?: string | number;
}

const SidebarItem: React.FC<SidebarItemProps> = ({
  icon: Icon,
  label,
  href,
  active,
  collapsed,
  badge
}) => {
  return (
    <a
      href={href}
      className={cn(
        "flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors group",
        active
          ? "bg-primary-50 text-primary-700 border border-primary-200"
          : "text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50",
        collapsed && "justify-center"
      )}
      title={collapsed ? label : undefined}
    >
      <Icon 
        size={20} 
        className={cn(
          "flex-shrink-0",
          active ? "text-primary-600" : "text-secondary-400 group-hover:text-secondary-600"
        )} 
      />
      {!collapsed && (
        <>
          <span className="flex-1">{label}</span>
          {badge && (
            <span className="bg-primary-100 text-primary-700 text-xs px-2 py-1 rounded-full">
              {badge}
            </span>
          )}
        </>
      )}
    </a>
  );
};
