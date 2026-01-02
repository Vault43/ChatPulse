import React from 'react'
import { useQuery } from 'react-query'
import api from '../services/api'

const Dashboard = () => {
  const { data: stats, isLoading } = useQuery('userStats', async () => {
    const res = await api.get('/users/stats')
    return res.data
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your ChatPulse account.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-body">
            <p className="text-sm text-gray-500">Chat sessions</p>
            <p className="text-2xl font-semibold text-gray-900">{isLoading ? '—' : stats?.chat_sessions ?? 0}</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <p className="text-sm text-gray-500">Messages</p>
            <p className="text-2xl font-semibold text-gray-900">{isLoading ? '—' : stats?.total_messages ?? 0}</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <p className="text-sm text-gray-500">AI rules</p>
            <p className="text-2xl font-semibold text-gray-900">{isLoading ? '—' : stats?.ai_rules ?? 0}</p>
          </div>
        </div>
        <div className="card">
          <div className="card-body">
            <p className="text-sm text-gray-500">Plan</p>
            <p className="text-2xl font-semibold text-gray-900">{isLoading ? '—' : stats?.subscription_plan ?? 'free'}</p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-medium text-gray-900">Next step</h2>
        </div>
        <div className="card-body">
          <p className="text-gray-700">
            Go to <span className="font-medium">AI Rules</span> to add keywords and reply templates, then test with a chat.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
