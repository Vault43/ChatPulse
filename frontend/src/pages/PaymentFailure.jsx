import React from 'react'
import { useNavigate } from 'react-router-dom'
import { ExclamationTriangleIcon, ArrowRightIcon, CreditCardIcon } from '@heroicons/react/24/outline'

const PaymentFailure = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="card text-center slide-in">
          <div className="card-body">
            {/* Error Icon */}
            <div className="inline-flex p-4 rounded-full bg-red-100 text-red-600 mb-6">
              <ExclamationTriangleIcon className="w-12 h-12" />
            </div>

            {/* Error Message */}
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Payment Failed</h1>
            <p className="text-lg text-gray-600 mb-6">
              We couldn't process your payment. Please try again or contact support.
            </p>

            {/* Possible Reasons */}
            <div className="bg-red-50 rounded-xl p-6 mb-8">
              <h3 className="font-semibold text-red-900 mb-3">Possible Reasons:</h3>
              <ul className="space-y-2 text-left text-sm text-red-700">
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-red-400 rounded-full mr-3 mt-1.5 flex-shrink-0"></span>
                  Insufficient funds
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-red-400 rounded-full mr-3 mt-1.5 flex-shrink-0"></span>
                  Invalid card details
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-red-400 rounded-full mr-3 mt-1.5 flex-shrink-0"></span>
                  Card declined by bank
                </li>
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-red-400 rounded-full mr-3 mt-1.5 flex-shrink-0"></span>
                  Network timeout
                </li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="space-y-3">
              <button
                onClick={() => navigate('/subscription')}
                className="w-full btn btn-primary"
              >
                <div className="flex items-center justify-center">
                  <CreditCardIcon className="w-4 h-4 mr-2" />
                  <span>Try Again</span>
                </div>
              </button>
              
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full btn btn-secondary"
              >
                <div className="flex items-center justify-center">
                  <span>Back to Dashboard</span>
                  <ArrowRightIcon className="w-4 h-4 ml-2" />
                </div>
              </button>
            </div>

            {/* Support Info */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="text-left">
                <h3 className="font-semibold text-gray-900 mb-2">Need Help?</h3>
                <p className="text-sm text-gray-600 mb-3">
                  If you continue to experience issues, please contact our support team:
                </p>
                <div className="space-y-2">
                  <a href="mailto:support@chatpulse.com" className="flex items-center text-sm text-purple-600 hover:text-purple-700">
                    <span>Email: support@chatpulse.com</span>
                  </a>
                  <a href="tel:+1234567890" className="flex items-center text-sm text-purple-600 hover:text-purple-700">
                    <span>Phone: +1 (234) 567-890</span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PaymentFailure
