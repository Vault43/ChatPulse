import React from 'react'
import { useQuery } from 'react-query'
import api from '../services/api'

const Settings = () => {
  const { data, isLoading } = useQuery('profile', async () => {
    const res = await api.get('/users/profile')
    return res.data
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Account and profile settings.</p>
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

export default Settings
