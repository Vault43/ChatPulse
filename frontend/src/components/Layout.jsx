import React, { useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { 
  HomeIcon, 
  ChatBubbleLeftRightIcon, 
  CogIcon, 
  ChartBarIcon,
  CreditCardIcon,
  CpuChipIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '../contexts/AuthContext'

const Layout = () => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon, color: 'blue' },
    { name: 'Chat', href: '/chat', icon: ChatBubbleLeftRightIcon, color: 'green' },
    { name: 'AI Rules', href: '/ai-rules', icon: CpuChipIcon, color: 'purple' },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon, color: 'yellow' },
    { name: 'Subscription', href: '/subscription', icon: CreditCardIcon, color: 'pink' },
    { name: 'Settings', href: '/settings', icon: CogIcon, color: 'gray' },
  ]

  const isActive = (href) => location.pathname === href

  const getColorClasses = (color, active) => {
    const colors = {
      blue: active ? 'bg-blue-500 text-white' : 'text-blue-600 hover:bg-blue-50',
      green: active ? 'bg-green-500 text-white' : 'text-green-600 hover:bg-green-50',
      purple: active ? 'bg-purple-500 text-white' : 'text-purple-600 hover:bg-purple-50',
      yellow: active ? 'bg-yellow-500 text-white' : 'text-yellow-600 hover:bg-yellow-50',
      pink: active ? 'bg-pink-500 text-white' : 'text-pink-600 hover:bg-pink-50',
      gray: active ? 'bg-gray-500 text-white' : 'text-gray-600 hover:bg-gray-50',
    }
    return colors[color] || colors.gray
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-100 bg-gradient-to-r from-blue-500 to-purple-600">
            <div className="flex items-center">
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-2 mr-3">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h1 className="text-xl font-bold text-white">ChatPulse</h1>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-white hover:bg-white/20 rounded-lg p-2"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon
              const active = isActive(item.href)
              const colorClasses = getColorClasses(item.color, active)
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200
                    ${active 
                      ? `${colorClasses} shadow-lg transform scale-[1.02]` 
                      : `${colorClasses} hover:transform hover:scale-[1.02]`
                    }
                  `}
                >
                  <Icon className={`w-5 h-5 mr-3 ${active ? 'text-white' : ''}`} />
                  <span className={active ? 'text-white' : ''}>{item.name}</span>
                  {active && (
                    <div className="ml-auto">
                      <div className="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  )}
                </Link>
              )
            })}
          </nav>

          {/* User menu */}
          <div className="p-4 border-t border-gray-100 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center flex-1 min-w-0">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-full p-2 mr-3">
                  <span className="text-white text-sm font-bold">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {user?.username}
                  </p>
                  <p className="text-xs text-gray-500 capitalize">
                    {user?.subscription_plan || 'Free'} Plan
                  </p>
                </div>
              </div>
              <button
                onClick={logout}
                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200"
                title="Logout"
              >
                <ArrowRightOnRectangleIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar for mobile */}
        <div className="lg:hidden bg-white border-b border-gray-200 px-4 py-3">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
            >
              <Bars3Icon className="w-6 h-6" />
            </button>
            <h1 className="text-lg font-semibold text-gray-900">ChatPulse</h1>
            <div className="w-10"></div>
          </div>
        </div>

        {/* Page content */}
        <main className="py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout
