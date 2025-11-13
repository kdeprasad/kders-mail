import React, {useState, useEffect} from 'react'
import axios from 'axios'
import Toast from './Toast'

export default function Compose({token}){
  const [to, setTo] = useState('')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [sending, setSending] = useState(false)
  const [toast, setToast] = useState(null)

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
  }

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (to.length >= 2) {
        try {
          const response = await axios.get(`/api/users/search?q=${encodeURIComponent(to)}`, {
            headers: {Authorization: `Bearer ${token}`}
          })
          setSuggestions(response.data || [])
          setShowSuggestions(true)
        } catch (e) {
          console.error('Failed to fetch suggestions:', e)
          setSuggestions([])
        }
      } else {
        setSuggestions([])
        setShowSuggestions(false)
      }
    }

    const timer = setTimeout(fetchSuggestions, 300)
    return () => clearTimeout(timer)
  }, [to, token])

  const selectSuggestion = (email) => {
    setTo(email)
    setShowSuggestions(false)
    setSuggestions([])
  }

  const send = async (e) =>{
    e.preventDefault()
    if (!to || !subject || !body) {
      showToast('Please fill all fields', 'warning')
      return
    }

    setSending(true)
    try{
      await axios.post('/api/mail/compose', {recipient: to, subject, body}, {headers:{Authorization:`Bearer ${token}`}})
      setTo(''); setSubject(''); setBody('')
      showToast('Email sent successfully!', 'success')
    }catch(e){
      console.error(e)
      showToast(e.response?.data?.detail || 'Failed to send email', 'error')
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md mb-4">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Compose Email</h3>
      <form onSubmit={send} className="space-y-4">
        <div className="relative">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            To
          </label>
          <input 
            value={to} 
            onChange={e=>setTo(e.target.value)} 
            placeholder="recipient@example.com" 
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#007ACC] dark:bg-gray-700 dark:text-white transition-all"
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            required
          />
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute z-10 w-full bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto mt-1">
              {suggestions.map((user, idx) => (
                <div
                  key={idx}
                  onClick={() => selectSuggestion(user.email)}
                  className="p-3 hover:bg-blue-50 dark:hover:bg-gray-600 cursor-pointer border-b dark:border-gray-600 last:border-b-0 transition-colors"
                >
                  <div className="font-medium text-gray-900 dark:text-white">{user.email}</div>
                  {user.full_name && <div className="text-sm text-gray-600 dark:text-gray-400">{user.full_name}</div>}
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Subject
          </label>
          <input 
            value={subject} 
            onChange={e=>setSubject(e.target.value)} 
            placeholder="Email subject" 
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#007ACC] dark:bg-gray-700 dark:text-white transition-all"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Message
          </label>
          <textarea 
            value={body} 
            onChange={e=>setBody(e.target.value)} 
            rows={8} 
            placeholder="Write your message here..."
            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#007ACC] dark:bg-gray-700 dark:text-white transition-all resize-none"
            required
          />
        </div>

        <button 
          type="submit"
          disabled={sending}
          className={`w-full bg-[#007ACC] text-white p-3 rounded-lg font-semibold transition-all ${
            sending ? 'opacity-50 cursor-not-allowed' : 'hover:bg-[#005a9e] active:scale-[0.98]'
          }`}
        >
          {sending ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Sending...
            </span>
          ) : (
            '✉️ Send Email'
          )}
        </button>
      </form>

      {toast && (
        <Toast 
          message={toast.message} 
          type={toast.type} 
          onClose={() => setToast(null)}
        />
      )}
    </div>
  )
}
