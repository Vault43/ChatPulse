import React from 'react'
import { useQuery } from 'react-query'
import api from '../services/api'

const Subscription = () => {
  const { data: plans } = useQuery('plans', async () => {
    const res = await api.get('/subscriptions/plans')
    return res.data
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Subscription Plans</h1>
        <p className="text-gray-600">Choose the perfect plan for your needs and unlock advanced features.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {(plans || []).map((p) => (
          <div key={p.plan_id} className="card hover:shadow-lg transition-shadow duration-200">
            <div className="card-body">
              <h2 className="text-lg font-semibold text-gray-900">{p.name}</h2>
              <p className="text-2xl font-bold text-gray-900 mt-2">${p.price}</p>
              <p className="text-sm text-gray-500">/{p.duration_days} days</p>
              <ul className="mt-3 space-y-1 text-sm text-gray-700">
                {(p.features || []).map((f) => (
                  <li key={f} className="flex items-start">
                    <svg className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              <div className="mt-6 space-y-2">
                <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium">
                  Choose Plan
                </button>
                <p className="text-xs text-gray-500 text-center">
                  Full access to all features included
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h3 className="text-sm font-medium text-blue-900">Premium Features</h3>
            <p className="text-sm text-blue-700 mt-1">
              Upgrade to unlock advanced AI capabilities, unlimited conversations, priority support, and custom integrations tailored to your business needs.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Subscription
