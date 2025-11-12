import React, {useEffect, useState} from 'react'
import axios from 'axios'

export default function Inbox({token}){
  const [msgs, setMsgs] = useState([])

  useEffect(()=>{
    const fetch = async () =>{
      try{
        const r = await axios.get('/api/mail/inbox', {headers:{Authorization:`Bearer ${token}`}})
        setMsgs(r.data)
      }catch(e){
        console.error(e)
      }
    }
    fetch()
  },[token])

  return (
    <div className="bg-white p-4 rounded shadow">
      <h3 className="font-semibold mb-2">Inbox</h3>
      <ul>
        {msgs.map(m=> (
          <li key={m.id} className="border-b py-2">
            <div className="font-medium">{m.subject || '(no subject)'}</div>
            <div className="text-sm text-gray-600">From: {m.sender}</div>
            <div className="text-sm mt-1">{m.body.substring(0,200)}...</div>
          </li>
        ))}
      </ul>
    </div>
  )
}
