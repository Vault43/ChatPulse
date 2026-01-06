import React, { useState } from 'react'
import { useQuery, useQueryClient, useMutation } from 'react-query'
import api from '../services/api'
import toast from 'react-hot-toast'

const AIRules = () => {
  const qc = useQueryClient()
  const [isCreating, setIsCreating] = useState(false)
  const [name, setName] = useState('')
  const [keywords, setKeywords] = useState('')
  const [template, setTemplate] = useState('')
  const [priority, setPriority] = useState(1)
  const [isActive, setIsActive] = useState(true)

  const { data: rules, isLoading } = useQuery('aiRules', async () => {
    const res = await api.get('/ai/rules')
    return res.data
  })

  const createRule = useMutation(
    async (ruleData) => {
      const res = await api.post('/ai/rules', ruleData)
      return res.data
    },
    {
      onSuccess: () => {
        toast.success('Rule created successfully! 🎉')
        setName('')
        setKeywords('')
        setTemplate('')
        setPriority(1)
        setIsActive(true)
        setIsCreating(false)
        qc.invalidateQueries('aiRules')
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to create rule')
      }
    }
  )

  const deleteRule = useMutation(
    async (id) => {
      await api.delete(`/ai/rules/${id}`)
    },
    {
      onSuccess: () => {
        toast.success('Rule deleted successfully')
        qc.invalidateQueries('aiRules')
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to delete rule')
      }
    }
  )

  const toggleRuleStatus = useMutation(
    async ({ id, is_active }) => {
      await api.put(`/ai/rules/${id}`, { is_active })
    },
    {
      onSuccess: () => {
        toast.success('Rule status updated')
        qc.invalidateQueries('aiRules')
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to update rule')
      }
    }
  )

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!name.trim() || !keywords.trim() || !template.trim()) {
      toast.error('Please fill all required fields')
      return
    }

    createRule.mutate({
      name,
      trigger_keywords: keywords
        .split(',')
        .map((k) => k.trim())
        .filter(Boolean),
      response_template: template,
      priority,
      is_active: isActive,
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Rules</h1>
        <p className="text-gray-600">Create intelligent rules to automate customer responses.</p>
      </div>

      {/* Create Rule Section */}
      <div className="card">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">Create New Rule</h2>
            <button
              onClick={() => setIsCreating(!isCreating)}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm"
            >
              {isCreating ? 'Cancel' : '+ Add Rule'}
            </button>
          </div>
        </div>
        
        {isCreating && (
          <div className="card-body">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Rule Name *
                  </label>
                  <input
                    className="input"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g., Pricing Questions"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    className="input"
                    value={priority}
                    onChange={(e) => setPriority(Number(e.target.value))}
                  >
                    <option value={1}>High</option>
                    <option value={2}>Medium</option>
                    <option value={3}>Low</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Trigger Keywords *
                </label>
                <input
                  className="input"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  placeholder="e.g., pricing, cost, price, how much"
                />
                <p className="text-xs text-gray-500 mt-1">Separate keywords with commas</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Response Template *
                </label>
                <textarea
                  className="input h-24"
                  value={template}
                  onChange={(e) => setTemplate(e.target.value)}
                  placeholder="e.g., Our pricing plans start at $29/month. You can view all plans on our subscription page. Use {message} to include the original message."
                />
                <p className="text-xs text-gray-500 mt-1">Use {'{message}'} to include the customer's original message</p>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="isActive"
                  checked={isActive}
                  onChange={(e) => setIsActive(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="isActive" className="ml-2 text-sm text-gray-700">
                  Enable this rule immediately
                </label>
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={createRule.isLoading}
                  className="btn btn-primary"
                >
                  {createRule.isLoading ? 'Creating...' : 'Create Rule'}
                </button>
                <button
                  type="button"
                  onClick={() => setIsCreating(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Rules List */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-medium text-gray-900">Your Rules ({rules?.length || 0})</h2>
        </div>
        <div className="card-body">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-sm text-gray-500 mt-2">Loading rules...</p>
            </div>
          ) : (
            <div className="space-y-4">
              {(rules || []).map((r) => (
                <div key={r.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-semibold text-gray-900">{r.name}</h3>
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          r.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          {r.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                          Priority {r.priority}
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {(r.trigger_keywords || []).map((keyword, index) => (
                          <span
                            key={index}
                            className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => toggleRuleStatus.mutate({ id: r.id, is_active: !r.is_active })}
                        className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title={r.is_active ? 'Deactivate' : 'Activate'}
                      >
                        {r.is_active ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                          </svg>
                        )}
                      </button>
                      <button
                        onClick={() => {
                          if (window.confirm('Are you sure you want to delete this rule?')) {
                            deleteRule.mutate(r.id)
                          }
                        }}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete rule"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3">
                    <p className="text-sm text-gray-600 mb-1">Response Template:</p>
                    <p className="text-gray-800">{r.response_template}</p>
                  </div>
                </div>
              ))}
              
              {(!rules || rules.length === 0) && (
                <div className="text-center py-12">
                  <div className="bg-gray-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No rules yet</h3>
                  <p className="text-gray-500 text-sm mb-4">
                    Create your first AI rule to start automating customer responses.
                  </p>
                  <button
                    onClick={() => setIsCreating(true)}
                    className="btn btn-primary"
                  >
                    Create Your First Rule
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <svg className="w-5 h-5 text-blue-600 mr-3 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
          <div>
            <h3 className="text-sm font-medium text-blue-900">Pro Tips</h3>
            <ul className="text-sm text-blue-700 mt-1 space-y-1">
              <li>• Use specific keywords like "pricing", "features", "support" for better matching</li>
              <li>• Higher priority rules are checked first</li>
              <li>• Use {'{message}'} in templates to include the customer's original question</li>
              <li>• Test your rules in the Chat section to see how they work</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AIRules
