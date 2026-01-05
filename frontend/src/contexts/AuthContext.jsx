import React, { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      const { access_token } = response.data
      
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      await fetchUser()
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      }
    }
  }

  const loginWithGoogle = async () => {
    try {
      // Redirect to Google OAuth
      window.location.href = `${api.defaults.baseURL}/auth/google/google`
    } catch (error) {
      return { 
        success: false, 
        error: 'Google login failed' 
      }
    }
  }

  const handleGoogleCallback = async (code, state) => {
    try {
      const response = await api.get('/auth/google/google/callback', {
        params: { code, state }
      })
      
      const { access_token, user, is_new_user } = response.data
      
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      setUser(user)
      
      return { 
        success: true, 
        user, 
        is_new_user 
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Google authentication failed' 
      }
    }
  }

  const register = async (userData) => {
    try {
      await api.post('/auth/register', userData)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      }
    }
  }

  const sendVerificationCode = async (email) => {
    try {
      const response = await api.post('/auth/send-verification', { email })
      return { 
        success: true, 
        message: response.data.message,
        email_sent: response.data.email_sent
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to send verification code' 
      }
    }
  }

  const verifyCode = async (email, code) => {
    try {
      const response = await api.post('/auth/verify-code', { email, code })
      return { 
        success: true, 
        message: response.data.message,
        verified: response.data.verified
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Invalid verification code' 
      }
    }
  }

  const signupWithVerification = async (userData) => {
    try {
      const response = await api.post('/auth/signup-with-verification', userData)
      return { 
        success: true, 
        message: response.data.message,
        user: response.data.user
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Signup failed' 
      }
    }
  }

  const forgotPassword = async (email) => {
    try {
      const response = await api.post('/auth/forgot-password', { email })
      return { 
        success: true, 
        message: response.data.message,
        email_sent: response.data.email_sent
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to send reset email' 
      }
    }
  }

  const resetPassword = async (token, newPassword) => {
    try {
      const response = await api.post('/auth/reset-password', { token, new_password: newPassword })
      return { 
        success: true, 
        message: response.data.message
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to reset password' 
      }
    }
  }

  const verifyResetToken = async (token) => {
    try {
      const response = await api.get(`/auth/verify-reset-token/${token}`)
      return { 
        success: true, 
        valid: response.data.valid,
        email: response.data.email
      }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Invalid token' 
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }

  const value = {
    user,
    login,
    loginWithGoogle,
    handleGoogleCallback,
    register,
    sendVerificationCode,
    verifyCode,
    signupWithVerification,
    forgotPassword,
    resetPassword,
    verifyResetToken,
    logout,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
