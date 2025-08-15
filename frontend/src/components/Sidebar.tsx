import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  BarChart3,
  Calendar,
  Target,
  Activity,
  Brain,
  MessageCircle,
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
  const location = useLocation();
  return (
    <aside className={cn(
      "backdrop-blur-sm transition-all duration-300 ease-in-out shadow-sm",
      "h-full",
      collapsed ? "w-16" : "w-64",
      className
    )} style={{backgroundColor: '#9FEDD7', borderRight: '1px solid rgba(2, 102, 112, 0.3)'}}>
      <div className="flex flex-col h-full">
        {/* Logo and Title Section */}
        <div className="flex items-center justify-between p-4" style={{borderBottom: '1px solid rgba(2, 102, 112, 0.2)'}}>
          {!collapsed && (
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg" style={{backgroundColor: '#026670'}}>
                <span className="text-white font-bold text-sm">EA</span>
              </div>
              <div>
                <h1 className="text-lg font-semibold tracking-tight" style={{fontFamily: 'Montserrat, system-ui, sans-serif', color: '#026670'}}>Elevate AI</h1>
                <p className="text-xs font-medium" style={{color: 'rgba(2, 102, 112, 0.7)'}}>Productivity & Wellness</p>
              </div>
            </div>
          )}

          {collapsed && (
            <div className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg mx-auto" style={{backgroundColor: '#026670'}}>
              <span className="text-white font-bold text-sm">EA</span>
            </div>
          )}

          <button
            onClick={onToggle}
            className="p-2 rounded-xl transition-all duration-200 hover:scale-110"
            style={{color: 'rgba(2, 102, 112, 0.6)'}}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(252, 225, 129, 0.3)'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
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
              active={location.pathname === '/dashboard' || location.pathname === '/'}
              collapsed={collapsed}
            />
            <SidebarItem
              icon={Activity}
              label="Activities"
              href="/activities"
              active={location.pathname === '/activities'}
              collapsed={collapsed}
            />
            <SidebarItem
              icon={Calendar}
              label="Schedule"
              href="/schedule"
              active={location.pathname === '/schedule'}
              collapsed={collapsed}
            />
            <SidebarItem
              icon={Brain}
              label="AI Insights"
              href="/insights"
              active={location.pathname === '/insights'}
              collapsed={collapsed}
            />
            <SidebarItem
              icon={MessageCircle}
              label="AI Assistant"
              href="/chatbot"
              active={location.pathname === '/chatbot'}
              collapsed={collapsed}
            />
            <SidebarItem
              icon={Target}
              label="Goals"
              href="/goals"
              active={location.pathname === '/goals'}
              collapsed={collapsed}
            />
          </div>

          {/* Divider */}
          <div className="my-6 border-t border-secondary-200 dark:border-secondary-600"></div>

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

        {/* Productivity Boost Card */}
        {!collapsed && (
          <div className="p-4 border-t border-secondary-200/50 dark:border-secondary-600/50">
            <div className="bg-gradient-to-r from-accent-50 to-accent-100 dark:from-accent-900/30 dark:to-accent-800/30 rounded-xl p-4 border border-accent-200/50 dark:border-accent-700/50">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-accent-100 dark:bg-accent-800 rounded-lg flex items-center justify-center">
                  <BarChart3 size={16} className="text-accent-600 dark:text-accent-400" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-accent-800 dark:text-accent-200">
                    Productivity Boost
                  </p>
                  <p className="text-xs text-accent-600 dark:text-accent-400">
                    +15% this week
                  </p>
                </div>
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
    <Link
      to={href}
      className={cn(
        "flex items-center space-x-3 px-3 py-3 rounded-xl text-sm font-semibold transition-all duration-200 group relative",
        "hover:scale-105 hover:shadow-sm",
        collapsed && "justify-center"
      )}
      style={{
        backgroundColor: active ? '#026670' : 'transparent',
        color: active ? 'white' : '#026670'
      }}
      onMouseEnter={(e) => {
        if (!active) {
          e.currentTarget.style.backgroundColor = 'rgba(252, 225, 129, 0.3)';
        }
      }}
      onMouseLeave={(e) => {
        if (!active) {
          e.currentTarget.style.backgroundColor = 'transparent';
        }
      }}
      title={collapsed ? label : undefined}
    >
      <Icon
        size={20}
        className="flex-shrink-0 transition-all duration-200"
        style={{
          color: active ? 'white' : '#026670'
        }}
      />
      {!collapsed && (
        <>
          <span className="flex-1">{label}</span>
          {badge && (
            <span className="text-xs px-2.5 py-1 rounded-full font-bold shadow-sm" style={{backgroundColor: '#FCE181', color: '#026670'}}>
              {badge}
            </span>
          )}
        </>
      )}
      {active && (
        <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-6 bg-gradient-to-b from-primary-500 to-primary-600 rounded-r-full"></div>
      )}
    </Link>
  );
};
