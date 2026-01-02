import React, { useState } from 'react'
import { useQuery, useQueryClient } from 'react-query'
import api from '../services/api'
import toast from 'react-hot-toast'

const AIRules = () => {
  const qc = useQueryClient()
  const [name, setName] = useState('')
  const [keywords, setKeywords] = useState('')
  const [template, setTemplate] = useState('')

  const { data: rules, isLoading } = useQuery('aiRules', async () => {
    const res = await api.get('/ai/rules')
    return res.data
  })

  const createRule = async () => {
    try {
      await api.post('/ai/rules', {
        name,
        trigger_keywords: keywords
          .split(',')
          .map((k) => k.trim())
          .filter(Boolean),
        response_template: template,
        priority: 1,
        is_active: true,
      })
      toast.success('Rule created')
      setName('')
      setKeywords('')
      setTemplate('')
      qc.invalidateQueries('aiRules')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to create rule')
    }
  }

  const deleteRule = async (id) => {
    try {
      await api.delete(`/ai/rules/${id}`)
      toast.success('Rule deleted')
      qc.invalidateQueries('aiRules')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to delete rule')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Rules</h1>
        <p className="text-gray-600">Define keyword triggers and reply templates.</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-medium text-gray-900">Create rule</h2>
        </div>
        <div className="card-body space-y-3">
          <input className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Rule name" />
          <input
            className="input"
            value={keywords}
            onChange={(e) => setKeywords(e.target.value)}
            placeholder="Keywords (comma separated)"
          />
          <textarea
            className="input h-28"
            value={template}
            onChange={(e) => setTemplate(e.target.value)}
            placeholder="Response template. You can use {message}"
          />
          <button className="btn btn-primary" onClick={createRule}>
            Save rule
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-medium text-gray-900">Your rules</h2>
        </div>
        <div className="card-body">
          {isLoading ? (
            <p className="text-sm text-gray-500">Loading...</p>
          ) : (
            <div className="space-y-3">
              {(rules || []).map((r) => (
                <div key={r.id} className="border rounded-md p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{r.name}</p>
                      <p className="text-sm text-gray-600">Keywords: {(r.trigger_keywords || []).join(', ')}</p>
                    </div>
                    <button className="btn btn-danger" onClick={() => deleteRule(r.id)}>
                      Delete
                    </button>
                  </div>
                  <p className="mt-2 text-gray-800">{r.response_template}</p>
                </div>
              ))}
              {(!rules || rules.length === 0) && <p className="text-sm text-gray-500">No rules yet.</p>}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AIRules
