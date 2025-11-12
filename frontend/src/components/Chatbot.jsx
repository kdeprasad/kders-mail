import React, {useState} from 'react'
import axios from 'axios'

export default function Chatbot({token}){
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)

  const ask = async (e) =>{
    e.preventDefault()
    if (!query.trim()) return
    
    setLoading(true)
    try{
      const r = await axios.post('/api/ai/query', {query}, {headers:{Authorization:`Bearer ${token}`}})
      setAnswer(r.data.answer)
      setQuery('')
    }catch(e){
      console.error(e)
      setAnswer('Sorry, I encountered an error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-800">
      {/* Query Input */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <form onSubmit={ask} className="space-y-3">
          <textarea
            value={query}
            onChange={e=>setQuery(e.target.value)}
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:border-[#007ACC] dark:focus:border-[#0098FF] resize-none text-sm"
            placeholder="Ask about your emails..."
            rows={3}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="w-full px-4 py-2 bg-[#007ACC] hover:bg-[#005A9E] disabled:bg-gray-400 text-white rounded-lg font-semibold transition-colors text-sm"
          >
            {loading ? 'Thinking...' : 'Ask AI'}
          </button>
        </form>
      </div>

      {/* Answer Display */}
      <div className="flex-1 overflow-y-auto p-4">
        {answer ? (
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 shadow-sm">
            <div className="flex items-start gap-2 mb-2">
              <span className="text-2xl">🤖</span>
              <span className="font-semibold text-gray-900 dark:text-white">AI Assistant</span>
            </div>
            <div className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap text-sm leading-relaxed">
              {answer}
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-8">
            <div className="text-4xl mb-3">🤖</div>
            <p className="text-sm">Ask me anything about your emails!</p>
            <p className="text-xs mt-2">Examples:</p>
            <ul className="text-xs mt-1 space-y-1">
              <li>• "Summarize latest emails"</li>
              <li>• "Find emails from John"</li>
              <li>• "What are my recent messages about?"</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
