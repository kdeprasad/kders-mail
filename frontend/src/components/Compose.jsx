import React, {useState, useEffect} from 'react'
import axios from 'axios'

export default function Compose({token}){
  const [to, setTo] = useState('')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(false)

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
    try{
      await axios.post('/api/mail/compose', {recipient: to, subject, body}, {headers:{Authorization:`Bearer ${token}`}})
      setTo(''); setSubject(''); setBody('')
      alert('Sent')
    }catch(e){
      console.error(e)
      alert('Send failed')
    }
  }

  return (
    <div className="bg-white p-4 rounded shadow mb-4">
      <h3 className="font-semibold mb-2">Compose</h3>
      <form onSubmit={send}>
        <div className="relative mb-2">
          <input 
            value={to} 
            onChange={e=>setTo(e.target.value)} 
            placeholder="To (start typing to see suggestions)" 
            className="w-full p-2 border rounded"
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
          />
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-b shadow-lg max-h-48 overflow-y-auto">
              {suggestions.map((user, idx) => (
                <div
                  key={idx}
                  onClick={() => selectSuggestion(user.email)}
                  className="p-2 hover:bg-blue-50 cursor-pointer border-b last:border-b-0"
                >
                  <div className="font-medium">{user.email}</div>
                  {user.full_name && <div className="text-sm text-gray-600">{user.full_name}</div>}
                </div>
              ))}
            </div>
          )}
        </div>
        <input value={subject} onChange={e=>setSubject(e.target.value)} placeholder="Subject" className="w-full p-2 border rounded mb-2" />
        <textarea value={body} onChange={e=>setBody(e.target.value)} rows={6} className="w-full p-2 border rounded mb-2" />
        <button className="bg-green-600 text-white p-2 rounded">Send</button>
      </form>
    </div>
  )
}
