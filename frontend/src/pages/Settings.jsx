import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import api from '../services/api'
import toast from 'react-hot-toast'

const Settings = () => {
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    full_name: '',
    company: '',
    email: '',
    username: ''
  })

  const queryClient = useQueryClient()

  const { data, isLoading, refetch } = useQuery('profile', async () => {
    const res = await api.get('/users/profile')
    return res.data
  }, {
    onSuccess: (data) => {
      setFormData({
        full_name: data.full_name || '',
        company: data.company || '',
        email: data.email || '',
        username: data.username || ''
      })
    }
  })

  const updateProfile = useMutation(
    async (profileData) => {
      const res = await api.put('/users/profile', profileData)
      return res.data
    },
    {
      onSuccess: () => {
        toast.success('Profile updated successfully!')
        setIsEditing(false)
        refetch()
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to update profile')
      }
    }
  )

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    // Only send fields that can be updated (exclude email for security)
    const updateData = {
      full_name: formData.full_name,
      company: formData.company,
      username: formData.username
    }
    updateProfile.mutate(updateData)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Account and profile settings.</p>
        </div>
        <div className="card">
          <div className="card-body">
            <p className="text-sm text-gray-500">Loading...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account and profile settings.</p>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Profile Information</h2>
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 text-sm font-medium"
              >
                Edit Profile
              </button>
            ) : (
              <div className="space-x-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors duration-200 text-sm font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={updateProfile.isLoading}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 text-sm font-medium disabled:opacity-50"
                >
                  {updateProfile.isLoading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            )}
          </div>

          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Company</label>
                <input
                  type="text"
                  name="company"
                  value={formData.company}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  disabled
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500"
                />
                <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-700">Full Name</h3>
                <p className="text-gray-900">{data?.full_name || 'Not set'}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700">Username</h3>
                <p className="text-gray-900">{data?.username}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700">Company</h3>
                <p className="text-gray-900">{data?.company || 'Not set'}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700">Email</h3>
                <p className="text-gray-900">{data?.email}</p>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700">Subscription Plan</h3>
                <span className="inline-flex px-3 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                  {data?.subscription_plan || 'Free'}
                </span>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700">Account Status</h3>
                <span className="inline-flex px-3 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                  {data?.is_verified ? 'Verified' : 'Not Verified'}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Settings
