import React, { useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { 
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  ChartBarIcon,
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon,
  SparklesIcon,
  ChartPieIcon,
  CreditCardIcon
} from '@heroicons/react/24/outline'
import { useAuth } from '../contexts/AuthContext'

const Layout = () => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: ChartBarIcon, color: 'blue' },
    { name: 'Chat', href: '/chat', icon: ChatBubbleLeftRightIcon, color: 'green' },
    { name: 'AI Rules', href: '/ai-rules', icon: SparklesIcon, color: 'purple' },
    { name: 'Analytics', href: '/analytics', icon: ChartPieIcon, color: 'yellow' },
    { name: 'Subscription', href: '/subscription', icon: CreditCardIcon, color: 'pink' },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon, color: 'gray' },
  ]

  const isActive = (href) => location.pathname === href

  const getColorClasses = (color, active) => {
    const colors = {
      blue: active ? 'text-purple-400' : 'text-gray-400',
      green: active ? 'text-purple-400' : 'text-gray-400',
      purple: active ? 'text-purple-400' : 'text-gray-400',
      yellow: active ? 'text-purple-400' : 'text-gray-400',
      pink: active ? 'text-purple-400' : 'text-gray-400',
      gray: active ? 'text-purple-400' : 'text-gray-400',
    }
    return colors[color] || colors.gray
  }

  return (
    <div className="min-h-screen">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 sidebar transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-800">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl p-3 mr-3 float-animation">
                <ChatBubbleLeftRightIcon className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gradient">ChatPulse</h1>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-gray-400 hover:bg-gray-800 rounded-lg p-2"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const active = isActive(item.href)
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    nav-item flex items-center
                    ${active ? 'nav-item-active' : ''}
                  `}
                >
                  <item.icon className={`w-5 h-5 mr-3 ${active ? 'text-purple-400' : 'text-gray-500'}`} />
                  <span className="text-gray-300">{item.name}</span>
                  {active && (
                    <div className="ml-auto">
                      <div className="w-2 h-2 bg-purple-500 rounded-full pulse-animation"></div>
                    </div>
                  )}
                </Link>
              )
            })}
          </nav>

          {/* User menu */}
          <div className="p-4 border-t border-gray-800">
            <div className="flex items-center justify-between">
              <div className="flex items-center flex-1 min-w-0">
                <div className="bg-gradient-to-r from-purple-500 to-pink-600 rounded-full p-3 mr-3 shadow-lg">
                  <span className="text-white text-sm font-bold">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-semibold text-white truncate">
                    {user?.username}
                  </p>
                  <p className="text-xs text-gray-400 capitalize">
                    {user?.subscription_plan || 'Free'} Plan
                  </p>
                </div>
              </div>
              <button
                onClick={logout}
                className="p-3 text-gray-400 hover:text-red-400 hover:bg-gray-800 rounded-xl transition-all duration-200"
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
        <div className="lg:hidden bg-gray-900/80 backdrop-blur-lg border-b border-gray-800 px-4 py-3">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-xl"
            >
              <Bars3Icon className="w-6 h-6" />
            </button>
            <h1 className="text-lg font-semibold text-gradient">ChatPulse</h1>
            <div className="w-10"></div>
          </div>
        </div>

        {/* Page content */}
        <main className="px-4 py-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout
