import React from 'react'
import { useQuery } from 'react-query'
import api from '../services/api'

const Analytics = () => {
  const { data, isLoading } = useQuery('analytics', async () => {
    const res = await api.get('/chat/analytics')
    return res.data
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600">Basic chat analytics (last 30 days by default).</p>
      </div>

      <div className="card">
        <div className="card-body">
          {isLoading ? (
            <p className="text-sm text-gray-500">Loading...</p>
          ) : (
            <pre className="text-sm bg-gray-50 p-3 rounded-md overflow-auto">{JSON.stringify(data, null, 2)}</pre>
          )}
        </div>
      </div>
    </div>
  )
}

export default Analytics
