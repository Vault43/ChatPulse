import React, { useState } from 'react'
import { useQuery } from 'react-query'
import api from '../services/api'
import toast from 'react-hot-toast'

const Chat = () => {
  const [message, setMessage] = useState('')
  const [aiReply, setAiReply] = useState('')

  const { data: sessions, refetch } = useQuery('sessions', async () => {
    const res = await api.get('/chat/sessions')
    return res.data
  })

  const handleGenerate = async () => {
    if (!message.trim()) return
    try {
      const res = await api.post('/ai/generate-response', {
        message,
        provider: 'gemini',
      })
      setAiReply(res.data.response)
    } catch (e) {
      toast.error(e.response?.data?.detail || 'AI request failed')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Chat</h1>
        <p className="text-gray-600">Test AI replies and view your chat sessions.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-medium text-gray-900">AI Test</h2>
          </div>
          <div className="card-body space-y-3">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="input h-28"
              placeholder="Type a customer message..."
            />
            <button className="btn btn-primary" onClick={handleGenerate}>
              Generate reply
            </button>
            {aiReply && (
              <div className="p-3 bg-gray-50 rounded-md border">
                <p className="text-sm text-gray-500 mb-1">AI reply</p>
                <p className="text-gray-900">{aiReply}</p>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="text-lg font-medium text-gray-900">Sessions</h2>
          </div>
          <div className="card-body">
            <div className="space-y-2">
              {(sessions || []).map((s) => (
                <div key={s.session_id} className="p-3 border rounded-md bg-white">
                  <p className="font-medium text-gray-900">{s.customer_name || 'Unknown customer'}</p>
                  <p className="text-sm text-gray-600">Platform: {s.platform}</p>
                  <p className="text-sm text-gray-600">Messages: {s.message_count}</p>
                </div>
              ))}
              {(!sessions || sessions.length === 0) && (
                <p className="text-sm text-gray-500">No sessions yet.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Chat
