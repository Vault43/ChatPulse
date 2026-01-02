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
        <h1 className="text-2xl font-bold text-gray-900">Subscription</h1>
        <p className="text-gray-600">Choose a plan and manage billing.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {(plans || []).map((p) => (
          <div key={p.plan_id} className="card">
            <div className="card-body">
              <h2 className="text-lg font-semibold text-gray-900">{p.name}</h2>
              <p className="text-2xl font-bold text-gray-900 mt-2">${p.price}</p>
              <p className="text-sm text-gray-500">/{p.duration_days} days</p>
              <ul className="mt-3 space-y-1 text-sm text-gray-700">
                {(p.features || []).map((f) => (
                  <li key={f}>- {f}</li>
                ))}
              </ul>
              <p className="mt-4 text-sm text-gray-500">
                Payments are activated once your Flutterwave keys are set in the backend.
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Subscription
