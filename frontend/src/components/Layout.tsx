import React, { useState, useEffect, useRef } from 'react';
import { User, LogOut, ChevronDown, Settings } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { cn } from '../utils';

interface LayoutProps {
  children: React.ReactNode;
  className?: string;
}

export const Layout: React.FC<LayoutProps> = ({ children, className }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const navigate = useNavigate();
  const userMenuRef = useRef<HTMLDivElement>(null);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  // Get user data from localStorage
  const getUserData = () => {
    try {
      const userData = localStorage.getItem('elevate_user');
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  };

  const user = getUserData();

  const handleLogout = () => {
    // Clear all auth data
    localStorage.removeItem('elevate_auth_token');
    localStorage.removeItem('elevate_refresh_token');
    localStorage.removeItem('elevate_user');

    // Navigate to login
    navigate('/login');
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="min-h-screen" style={{background: 'linear-gradient(135deg, #EDEAE5 0%, #9FEDD7 100%)'}}>
      <div className="flex h-screen">
        {/* Sidebar */}
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={toggleSidebar}
        />

        {/* Main Content Area */}
        <div className="flex-1 relative overflow-hidden">
          {/* Floating User Controls - Top Right */}
          <div className="absolute top-4 right-4 z-50 flex items-center space-x-3">
            {/* Settings Button */}
            <button className="p-2 rounded-xl transition-all duration-200 hover:scale-105 shadow-sm backdrop-blur-sm" style={{color: '#026670', backgroundColor: 'rgba(159, 237, 215, 0.8)'}} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(252, 225, 129, 0.8)'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(159, 237, 215, 0.8)'}>
              <Settings size={20} />
            </button>

            {/* User Profile Menu */}
            <div ref={userMenuRef} className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2 p-2 rounded-xl transition-all duration-200 hover:scale-105 shadow-sm backdrop-blur-sm"
                style={{color: '#026670', backgroundColor: 'rgba(159, 237, 215, 0.8)'}}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(252, 225, 129, 0.8)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'rgba(159, 237, 215, 0.8)'}
              >
                {/* Profile Picture */}
                <div className="w-9 h-9 rounded-full flex items-center justify-center shadow-sm border-2" style={{backgroundColor: '#026670', borderColor: '#9FEDD7'}}>
                  <User size={18} style={{color: 'white'}} />
                </div>

                {/* User Name (hidden on mobile) */}
                <span className="hidden sm:block text-sm font-semibold" style={{color: '#026670'}}>
                  {user?.name || 'User'}
                </span>

                {/* Dropdown Arrow (hidden on mobile) */}
                <ChevronDown size={16} className={cn(
                  "hidden sm:block transition-transform duration-200",
                  userMenuOpen && "rotate-180"
                )} />
              </button>

              {/* User Dropdown Menu */}
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-56 rounded-xl shadow-lg py-2 z-50 animate-fade-in" style={{backgroundColor: '#9FEDD7', border: '1px solid rgba(2, 102, 112, 0.3)'}}>
                  {/* User Info Header */}
                  <div className="px-4 py-3" style={{borderBottom: '1px solid rgba(2, 102, 112, 0.2)'}}>
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-full flex items-center justify-center shadow-sm" style={{backgroundColor: '#026670'}}>
                        <User size={20} style={{color: 'white'}} />
                      </div>
                      <div>
                        <p className="text-sm font-semibold" style={{color: '#026670'}}>{user?.name || 'User'}</p>
                        <p className="text-xs" style={{color: 'rgba(2, 102, 112, 0.7)'}}>{user?.email || 'user@example.com'}</p>
                      </div>
                    </div>
                  </div>

                  {/* Menu Items */}
                  <div className="py-1">
                    <button
                      onClick={() => {
                        setUserMenuOpen(false);
                        // Add profile navigation here if needed
                      }}
                      className="w-full text-left px-4 py-2 text-sm flex items-center space-x-3 transition-colors duration-200"
                      style={{color: '#026670'}}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(252, 225, 129, 0.3)'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                      <User size={16} />
                      <span>View Profile</span>
                    </button>

                    <hr className="my-1" style={{borderColor: 'rgba(2, 102, 112, 0.2)'}} />

                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm flex items-center space-x-3 transition-colors duration-200"
                      style={{color: '#dc2626'}}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(220, 38, 38, 0.1)'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                      <LogOut size={16} />
                      <span>Sign out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Main Content */}
          <main className={cn(
            "h-full overflow-hidden",
            className
          )}>
            <div className="h-full overflow-y-auto">
              <div className="p-4 sm:p-6 lg:p-8">
                <div className="max-w-7xl mx-auto">
                  {children}
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
};
