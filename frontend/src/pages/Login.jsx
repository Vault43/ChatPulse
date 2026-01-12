import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useAuth } from '../contexts/AuthContext'
import Logo from '../assets/logo.svg'

const Login = () => {
  const [loading, setLoading] = useState(false)
  const [showForgotPassword, setShowForgotPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [forgotPasswordEmail, setForgotPasswordEmail] = useState('')
  const { login, loginWithGoogle, forgotPassword } = useAuth()
  const navigate = useNavigate()
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      rememberMe: false
    }
  })

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const result = await login(data.email, data.password, data.rememberMe)
      if (result.success) {
        toast.success('Welcome back to ChatPulse! 🎉')
        navigate('/dashboard')
      } else {
        toast.error(result.error)
      }
    } catch (error) {
      toast.error('Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignIn = async () => {
    setLoading(true)
    try {
      const result = await loginWithGoogle()
      if (!result.success) {
        toast.error(result.error)
      }
    } catch (error) {
      toast.error('Google sign-in failed')
    } finally {
      setLoading(false)
    }
  }

  const handleForgotPassword = async (email) => {
    setLoading(true)
    try {
      const result = await forgotPassword(email)
      if (result.success) {
        toast.success(result.message)
        setShowForgotPassword(false)
      } else {
        toast.error(result.error)
      }
    } catch (error) {
      toast.error('Failed to send reset email')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-black py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        {/* Logo/Brand Section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 mb-4">
            <img src={Logo} alt="ChatPulse" className="w-full h-full" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">
            Welcome back
          </h2>
          <p className="text-gray-400">
            Sign in to your ChatPulse account
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-gray-900 shadow-2xl rounded-2xl p-8 border border-gray-800">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email address
              </label>
              <input
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address',
                  },
                })}
                type="email"
                autoComplete="email"
                className="block w-full px-4 py-3 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-gray-800 text-white placeholder-gray-500 transition-all duration-200"
                placeholder="you@example.com"
              />
              {errors.email && (
                <p className="mt-2 text-sm text-red-400 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {errors.email.message}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                {...register('password', {
                  required: 'Password is required',
                })}
                type="password"
                autoComplete="current-password"
                className="block w-full px-4 py-3 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-gray-800 text-white placeholder-gray-500 transition-all duration-200"
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-2 text-sm text-red-400 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {errors.password.message}
                </p>
              )}
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  {...register('rememberMe')}
                  type="checkbox"
                  className="h-4 w-4 text-purple-600 focus:ring-purple-500 border-gray-600 rounded bg-gray-800"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-300">
                  Remember me
                </label>
              </div>

              <div className="text-sm">
                <button
                  type="button"
                  onClick={() => setShowForgotPassword(true)}
                  className="font-medium text-purple-400 hover:text-purple-300 transition-colors duration-200"
                >
                  Forgot your password?
                </button>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-[1.02]"
              >
                {loading ? (
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  'Sign in'
                )}
              </button>
            </div>

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-700" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-900 text-gray-500">Or continue with</span>
              </div>
            </div>

            {/* Google Sign-In */}
            <div>
              <button
                type="button"
                onClick={handleGoogleSignIn}
                disabled={loading}
                className="w-full flex items-center justify-center px-4 py-3 border border-gray-700 rounded-lg shadow-sm text-sm font-medium text-gray-300 bg-gray-800 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continue with Google
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-700" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-gray-900 text-gray-500">New to ChatPulse?</span>
              </div>
            </div>

            <div className="mt-6 text-center">
              <Link
                to="/register"
                className="font-medium text-purple-400 hover:text-purple-300 transition-colors duration-200"
              >
                Create your free account →
              </Link>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-sm text-gray-500">
          © 2024 ChatPulse. All rights reserved.
        </p>
      </div>

      {/* Forgot Password Modal */}
      {showForgotPassword && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-2xl p-8 max-w-md w-full border border-gray-800">
            <h3 className="text-2xl font-bold text-white mb-4">
              Reset your password
            </h3>
            <p className="text-gray-400 mb-6">
              Enter your email address and we'll send you a link to reset your password.
            </p>
            
            <form onSubmit={handleSubmit((data) => {
              const email = forgotPasswordEmail || data.email
              if (email) {
                handleForgotPassword(email)
              }
            })} className="space-y-6">
              <div className="mb-6">
                <label htmlFor="reset-email" className="block text-sm font-medium text-gray-300 mb-2">
                  Email address
                </label>
                <input
                  type="email"
                  id="reset-email"
                  value={forgotPasswordEmail}
                  onChange={(e) => setForgotPasswordEmail(e.target.value)}
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address',
                    },
                  })}
                  autoComplete="email"
                  className="block w-full px-4 py-3 border border-gray-700 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-gray-800 text-white placeholder-gray-500 transition-all duration-200"
                  placeholder="you@example.com"
                />
                {errors.email && (
                  <p className="mt-2 text-sm text-red-400 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    {errors.email.message}
                  </p>
                )}
              </div>

              <div className="flex space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowForgotPassword(false)
                    setForgotPasswordEmail('')
                  }}
                  className="flex-1 px-4 py-3 border border-gray-700 text-sm font-medium rounded-lg text-gray-300 bg-gray-800 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all duration-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-3 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {loading ? (
                    <svg className="animate-spin h-5 w-5 text-white mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    'Send Reset Link'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Login
