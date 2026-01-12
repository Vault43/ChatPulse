import React from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { CheckCircleIcon, ArrowRightIcon, HomeIcon } from '@heroicons/react/24/outline'

const PaymentSuccess = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  
  const planName = searchParams.get('plan') || 'Professional'
  const amount = searchParams.get('amount') || '29.99'

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="card text-center slide-in">
          <div className="card-body">
            {/* Success Icon */}
            <div className="inline-flex p-4 rounded-full bg-green-100 text-green-600 mb-6">
              <CheckCircleIcon className="w-12 h-12" />
            </div>

            {/* Success Message */}
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Payment Successful!</h1>
            <p className="text-lg text-gray-600 mb-6">
              Welcome to <span className="font-semibold text-purple-600">{planName}</span> plan!
            </p>

            {/* Payment Details */}
            <div className="bg-gray-50 rounded-xl p-6 mb-8">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Plan:</span>
                  <span className="font-semibold text-gray-900">{planName}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Amount:</span>
                  <span className="font-semibold text-gray-900">${amount}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Status:</span>
                  <span className="badge badge-success">Active</span>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full btn btn-primary"
              >
                <div className="flex items-center justify-center">
                  <span>Go to Dashboard</span>
                  <ArrowRightIcon className="w-4 h-4 ml-2" />
                </div>
              </button>
              
              <button
                onClick={() => navigate('/chat')}
                className="w-full btn btn-secondary"
              >
                Start Using ChatPulse
              </button>
            </div>

            {/* Additional Info */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="flex items-start">
                <HomeIcon className="w-5 h-5 text-gray-400 mr-3 mt-0.5" />
                <div className="text-left">
                  <p className="text-sm text-gray-600">
                    A confirmation email has been sent to your registered email address with your subscription details.
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    You can manage your subscription anytime from the Settings page.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PaymentSuccess
