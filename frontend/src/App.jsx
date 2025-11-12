import React, {useState, useEffect} from 'react'
import Login from './components/Login'
import Register from './components/Register'
import WhatsAppLayout from './components/WhatsAppLayout'

export default function App(){
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [email, setEmail] = useState(localStorage.getItem('email'))
  const [isDark, setIsDark] = useState(localStorage.getItem('theme') === 'dark')
  const [view, setView] = useState('home')
  const [registerAsTeacher, setRegisterAsTeacher] = useState(false)

  // initialize view from URL when not authenticated
  useEffect(() => {
    if (localStorage.getItem('token')) return
    const path = window.location.pathname || '/'
    const search = new URLSearchParams(window.location.search)
    if (path.startsWith('/auth/login')) {
      setView('login')
    } else if (path.startsWith('/auth/register')) {
      setRegisterAsTeacher(search.get('teacher') === '1' || search.get('role') === 'teacher')
      setView('register')
    } else {
      setView('home')
    }
  }, [])

  // keep browser URL in sync with view
  useEffect(() => {
    if (view === 'home') window.history.replaceState({}, '', '/')
    if (view === 'login') window.history.replaceState({}, '', '/auth/login')
    if (view === 'register') window.history.replaceState({}, '', `/auth/register${registerAsTeacher ? '?teacher=1' : ''}`)
  }, [view, registerAsTeacher])

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [isDark])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('email')
    setToken(null)
    setEmail(null)
    setView('home')
  }

  if(!token){
    if(view === 'login'){
      return (
        <div className="dark:bg-gray-900 min-h-screen">
          <Login onLogin={(t,e)=>{setToken(t); setEmail(e); localStorage.setItem('token', t); localStorage.setItem('email', e)}} onBack={()=>setView('home')} />
        </div>
      )
    }

    if(view === 'register'){
      return (
        <div className="dark:bg-gray-900 min-h-screen">
          <Register onLogin={(t,e)=>{setToken(t); setEmail(e); localStorage.setItem('token', t); localStorage.setItem('email', e)}} isTeacher={registerAsTeacher} onBack={()=>setView('home')} />
        </div>
      )
    }

    // home view
    return (
      <div className="dark:bg-gray-900 min-h-screen flex items-center justify-center">
        <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md text-center">
          <h2 className="text-2xl font-bold mb-4 dark:text-white">Welcome to kders Mail</h2>
          <p className="mb-6 dark:text-gray-200">Choose an action to continue</p>
          <div className="flex flex-col gap-3">
            <button onClick={()=>setView('login')} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded">Sign in</button>
            <button onClick={()=>{setRegisterAsTeacher(false); setView('register')}} className="px-4 py-2 bg-gray-200 dark:bg-gray-700 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600 rounded">Sign up as Student</button>
            <button onClick={()=>{setRegisterAsTeacher(true); setView('register')}} className="px-4 py-2 bg-gray-200 dark:bg-gray-700 dark:text-white hover:bg-gray-300 dark:hover:bg-gray-600 rounded">Sign up as Teacher</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <WhatsAppLayout 
      token={token} 
      email={email} 
      isDark={isDark} 
      onToggleDark={() => setIsDark(!isDark)}
      onLogout={handleLogout}
    />
  )
}
