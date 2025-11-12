import React, {useState, useEffect} from 'react'
import axios from 'axios'
import ConversationList from './ConversationList'
import ChatView from './ChatView'
import Sidebar from './Sidebar'
import Chatbot from './Chatbot'

export default function WhatsAppLayout({token, email, isDark, onToggleDark, onLogout}){
  const [selectedConversation, setSelectedConversation] = useState(null)
  const [conversations, setConversations] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [showChatbot, setShowChatbot] = useState(false)

  // Fetch inbox messages
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const response = await axios.get('/api/mail/inbox', {
          headers: {Authorization: `Bearer ${token}`}
        })
        setConversations(response.data)
      } catch (error) {
        console.error('Failed to fetch conversations:', error)
      }
    }
    fetchConversations()
  }, [token, refreshTrigger])

  const handleSendMessage = async (recipient, subject, body) => {
    try {
      await axios.post('/api/mail/compose', 
        {recipient, subject, body}, 
        {headers: {Authorization: `Bearer ${token}`}}
      )
      setRefreshTrigger(prev => prev + 1)
      return true
    } catch (error) {
      console.error('Failed to send message:', error)
      return false
    }
  }

  const filteredConversations = conversations.filter(conv => 
    conv.sender.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (conv.subject && conv.subject.toLowerCase().includes(searchQuery.toLowerCase())) ||
    conv.body.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="h-screen flex flex-col bg-gray-100 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-[#007ACC] dark:bg-gray-800 text-white px-4 py-3 flex items-center justify-between">
        <h1 className="text-xl font-semibold">kders Mail</h1>
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleDark}
            className="p-2 rounded-full hover:bg-white/10 transition-colors"
            title={isDark ? "Switch to light mode" : "Switch to dark mode"}
          >
            {isDark ? "🌞" : "🌙"}
          </button>
          <span className="text-sm">{email}</span>
          <button
            onClick={() => setShowChatbot(!showChatbot)}
            className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm transition-colors flex items-center gap-2"
            title="AI Assistant"
          >
            <span>🤖</span>
            <span>AI Assistant</span>
          </button>
          <button 
            onClick={onLogout} 
            className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white rounded text-sm transition-colors"
          >
            Sign out
          </button>
        </div>
      </header>

      {/* Main content - 3 columns + optional chatbot */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left sidebar - Groups and contacts */}
        <Sidebar token={token} email={email} />

        {/* Middle - Conversation list */}
        <ConversationList 
          conversations={filteredConversations}
          selectedConversation={selectedConversation}
          onSelectConversation={setSelectedConversation}
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          token={token}
        />

        {/* Right - Chat view */}
        <ChatView 
          conversation={selectedConversation}
          onSendMessage={handleSendMessage}
          userEmail={email}
          token={token}
        />

        {/* AI Chatbot Panel (toggleable) */}
        {showChatbot && (
          <div className="w-[350px] border-l border-gray-200 dark:border-gray-700 flex flex-col bg-white dark:bg-gray-800">
            <div className="p-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 dark:text-white">AI Assistant</h3>
              <button
                onClick={() => setShowChatbot(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <Chatbot token={token} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
