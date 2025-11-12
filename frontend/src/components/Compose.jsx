import React, {useState} from 'react'
import axios from 'axios'

export default function Compose({token}){
  const [to, setTo] = useState('')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')

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
        <input value={to} onChange={e=>setTo(e.target.value)} placeholder="To" className="w-full p-2 border rounded mb-2" />
        <input value={subject} onChange={e=>setSubject(e.target.value)} placeholder="Subject" className="w-full p-2 border rounded mb-2" />
        <textarea value={body} onChange={e=>setBody(e.target.value)} rows={6} className="w-full p-2 border rounded mb-2" />
        <button className="bg-green-600 text-white p-2 rounded">Send</button>
      </form>
    </div>
  )
}
