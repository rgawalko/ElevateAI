import React from 'react';
import { User, Bell, Settings, LogOut } from 'lucide-react';
import { cn } from '../utils';

interface HeaderProps {
  className?: string;
}

export const Header: React.FC<HeaderProps> = ({ className }) => {
  return (
    <header className={cn(
      "bg-white border-b border-secondary-200 px-6 py-4",
      className
    )}>
      <div className="flex items-center justify-between">
        {/* Logo and Title */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">EA</span>
          </div>
          <div>
            <h1 className="text-xl font-semibold text-secondary-900">Elevate AI</h1>
            <p className="text-xs text-secondary-500">Productivity & Wellness</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="hidden md:flex items-center space-x-8">
          <NavLink href="/dashboard" active>Dashboard</NavLink>
          <NavLink href="/activities">Activities</NavLink>
          <NavLink href="/schedule">Schedule</NavLink>
          <NavLink href="/insights">Insights</NavLink>
          <NavLink href="/goals">Goals</NavLink>
        </nav>

        {/* User Actions */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="relative p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50 rounded-lg transition-colors">
            <Bell size={20} />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-danger-500 rounded-full"></span>
          </button>

          {/* Settings */}
          <button className="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50 rounded-lg transition-colors">
            <Settings size={20} />
          </button>

          {/* User Menu */}
          <div className="relative">
            <button className="flex items-center space-x-2 p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-50 rounded-lg transition-colors">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <User size={16} className="text-primary-600" />
              </div>
              <span className="hidden md:block text-sm font-medium">John Doe</span>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <nav className="md:hidden mt-4 flex items-center space-x-6 overflow-x-auto">
        <NavLink href="/dashboard" active mobile>Dashboard</NavLink>
        <NavLink href="/activities" mobile>Activities</NavLink>
        <NavLink href="/schedule" mobile>Schedule</NavLink>
        <NavLink href="/insights" mobile>Insights</NavLink>
        <NavLink href="/goals" mobile>Goals</NavLink>
      </nav>
    </header>
  );
};

interface NavLinkProps {
  href: string;
  children: React.ReactNode;
  active?: boolean;
  mobile?: boolean;
}

const NavLink: React.FC<NavLinkProps> = ({ href, children, active, mobile }) => {
  return (
    <a
      href={href}
      className={cn(
        "font-medium transition-colors whitespace-nowrap",
        mobile ? "text-sm py-2" : "text-sm",
        active
          ? "text-primary-600 border-b-2 border-primary-600"
          : "text-secondary-600 hover:text-secondary-900"
      )}
    >
      {children}
    </a>
  );
};
