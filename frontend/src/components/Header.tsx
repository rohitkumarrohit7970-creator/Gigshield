import { Shield, Bell, User, LogOut, Menu, UserCircle, LayoutDashboard } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface HeaderProps {
  userName?: string;
  userRole: 'worker' | 'admin';
  onLogout: () => void;
  showNotifications?: boolean;
}

export default function Header({ userName = 'User', userRole, onLogout, showNotifications = true }: HeaderProps) {
  const [showMenu, setShowMenu] = useState(false);
  const navigate = useNavigate();

  return (
    <header className="bg-white/80 backdrop-blur-md shadow-lg sticky top-0 z-40 border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-xl">
              <Shield className="h-7 w-7 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                GigShield
              </span>
              {userRole === 'admin' && (
                <span className="ml-2 px-2 py-0.5 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
                  Admin
                </span>
              )}
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-4">
            {showNotifications && (
              <button className="p-2 hover:bg-gray-100 rounded-xl transition-colors relative">
                <Bell className="h-5 w-5 text-gray-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </button>
            )}
            
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="flex items-center space-x-2 p-2 hover:bg-gray-100 rounded-xl transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-700">{userName}</span>
              </button>

              {showMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-100 py-2 animate-fade-in z-50">
                  <div className="px-4 py-2 border-b border-gray-100">
                    <p className="text-sm font-medium text-gray-800">{userName}</p>
                    <p className="text-xs text-gray-500 capitalize">{userRole}</p>
                  </div>
                  
                  {userRole === 'worker' && (
                    <>
                      <button
                        onClick={() => { navigate('/dashboard'); setShowMenu(false); }}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                      >
                        <LayoutDashboard className="h-4 w-4" />
                        <span>Dashboard</span>
                      </button>
                      <button
                        onClick={() => { navigate('/profile'); setShowMenu(false); }}
                        className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2"
                      >
                        <UserCircle className="h-4 w-4" />
                        <span>My Profile</span>
                      </button>
                    </>
                  )}
                  
                  <button
                    onClick={onLogout}
                    className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Sign Out</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          <button 
            className="md:hidden p-2 hover:bg-gray-100 rounded-xl"
            onClick={() => setShowMenu(!showMenu)}
          >
            <Menu className="h-5 w-5 text-gray-600" />
          </button>
        </div>
        
        {showMenu && (
          <div className="md:hidden py-2 border-t border-gray-100 space-y-1">
            {userRole === 'worker' && (
              <>
                <button
                  onClick={() => { navigate('/dashboard'); setShowMenu(false); }}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  Dashboard
                </button>
                <button
                  onClick={() => { navigate('/profile'); setShowMenu(false); }}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  My Profile
                </button>
              </>
            )}
            <button
              onClick={onLogout}
              className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
            >
              Sign Out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}