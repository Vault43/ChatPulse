import React, { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import toast from 'react-hot-toast'

const GoogleCallback = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { handleGoogleCallback } = useAuth()

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const state = searchParams.get('state')
      
      if (code) {
        try {
          const result = await handleGoogleCallback(code, state)
          if (result.success) {
            toast.success(
              result.is_new_user 
                ? 'Welcome to ChatPulse! 🎉' 
                : 'Welcome back! 🎉'
            )
            navigate('/dashboard')
          } else {
            toast.error(result.error)
            navigate('/login')
          }
        } catch (error) {
          toast.error('Authentication failed')
          navigate('/login')
        }
      } else {
        toast.error('Authorization failed')
        navigate('/login')
      }
    }

    handleCallback()
  }, [searchParams, navigate, handleGoogleCallback])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mb-4">
          <svg className="w-8 h-8 text-white animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Authenticating...
        </h2>
        <p className="text-gray-600">
          Please wait while we complete your sign in.
        </p>
      </div>
    </div>
  )
}

export default GoogleCallback
