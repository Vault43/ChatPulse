import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import { useAuth } from '../contexts/AuthContext'

const Register = () => {
  const [loading, setLoading] = useState(false)
  const { register: registerUser } = useAuth()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const result = await registerUser({
        email: data.email,
        username: data.username,
        password: data.password,
        full_name: data.fullName || undefined,
        company: data.company || undefined,
      })

      if (result.success) {
        toast.success('Account created. Please log in.')
        navigate('/login')
      } else {
        toast.error(result.error)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your ChatPulse account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
              sign in
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-4" onSubmit={handleSubmit(onSubmit)}>
          <div>
            <input
              {...register('email', { required: 'Email is required' })}
              type="email"
              className="input"
              placeholder="Email"
            />
            {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
          </div>

          <div>
            <input
              {...register('username', { required: 'Username is required' })}
              type="text"
              className="input"
              placeholder="Username"
            />
            {errors.username && <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>}
          </div>

          <div>
            <input {...register('fullName')} type="text" className="input" placeholder="Full name (optional)" />
          </div>

          <div>
            <input {...register('company')} type="text" className="input" placeholder="Company (optional)" />
          </div>

          <div>
            <input
              {...register('password', { required: 'Password is required' })}
              type="password"
              className="input"
              placeholder="Password"
            />
            {errors.password && <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create account'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Register
