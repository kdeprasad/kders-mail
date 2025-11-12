import React, {useState} from 'react'
import axios from 'axios'

export default function Login({onLogin, onBack}){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  const submit = async (e) =>{
    e.preventDefault()
    try{
      const r = await axios.post('/api/auth/login', {email, password})
      const token = r.data.access_token
      onLogin(token, email)
    }catch(err){
      setError(err?.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="max-w-md mx-auto mt-20 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg transition-colors duration-200">
      <h2 className="text-xl font-semibold mb-4 dark:text-white">Sign in</h2>
      <form onSubmit={submit}>
        <label className="block mb-2 dark:text-gray-200">Email</label>
        <input 
          value={email} 
          onChange={e=>setEmail(e.target.value)} 
          className="w-full p-2 border dark:border-gray-600 rounded mb-3 bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 focus:border-transparent" 
        />
        <label className="block mb-2 dark:text-gray-200">Password</label>
        <input 
          type="password" 
          value={password} 
          onChange={e=>setPassword(e.target.value)} 
          className="w-full p-2 border dark:border-gray-600 rounded mb-3 bg-white dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 focus:border-transparent" 
        />
        <button className="w-full bg-primary-600 hover:bg-primary-700 text-white p-2 rounded transition duration-200">Sign in</button>
        {error && <div className="text-red-600 dark:text-red-400 mt-2">{error}</div>}
      </form>
      <div className="mt-3 text-center">
        <button onClick={onBack} className="text-sm text-primary-500 dark:text-primary-300">Back</button>
      </div>
    </div>
  )
}
