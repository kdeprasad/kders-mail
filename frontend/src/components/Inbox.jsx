import React, {useEffect, useState} from 'react'
import axios from 'axios'
import Toast from './Toast'

export default function Inbox({token}){
  const [msgs, setMsgs] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState(null)

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
  }

  const fetchInbox = async () => {
    setLoading(true)
    try{
      const r = await axios.get('/api/mail/inbox', {headers:{Authorization:`Bearer ${token}`}})
      setMsgs(r.data)
    }catch(e){
      console.error(e)
      showToast('Failed to load inbox', 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(()=>{
    fetchInbox()
  },[token])

  const handleSearch = async (query) => {
    setSearchQuery(query)
    if (!query || query.length < 2) {
      fetchInbox()
      return
    }
    
    setLoading(true)
    try {
      const r = await axios.get(`/api/mail/search?q=${encodeURIComponent(query)}`, {
        headers:{Authorization:`Bearer ${token}`}
      })
      setMsgs(r.data)
    } catch(e) {
      console.error(e)
      showToast('Search failed', 'error')
    } finally {
      setLoading(false)
    }
  }

  const toggleRead = async (msgId, currentStatus) => {
    try {
      await axios.patch(`/api/mail/${msgId}/read`, 
        {is_read: !currentStatus}, 
        {headers:{Authorization:`Bearer ${token}`}}
      )
      setMsgs(msgs.map(m => m.id === msgId ? {...m, is_read: !currentStatus} : m))
      showToast(!currentStatus ? 'Marked as read' : 'Marked as unread', 'success')
    } catch(e) {
      console.error(e)
      showToast('Failed to update', 'error')
    }
  }

  const togglePin = async (msgId, currentStatus) => {
    try {
      await axios.patch(`/api/mail/${msgId}/pin`, 
        {is_pinned: !currentStatus}, 
        {headers:{Authorization:`Bearer ${token}`}}
      )
      setMsgs(msgs.map(m => m.id === msgId ? {...m, is_pinned: !currentStatus} : m))
      showToast(!currentStatus ? 'Message pinned' : 'Message unpinned', 'success')
    } catch(e) {
      console.error(e)
      showToast('Failed to pin', 'error')
    }
  }

  const deleteEmail = async (msgId) => {
    if (!window.confirm('Delete this email?')) return
    
    try {
      await axios.delete(`/api/mail/${msgId}`, {
        headers:{Authorization:`Bearer ${token}`}
      })
      setMsgs(msgs.filter(m => m.id !== msgId))
      showToast('Email deleted', 'success')
    } catch(e) {
      console.error(e)
      showToast('Failed to delete', 'error')
    }
  }

  // Sort: pinned first, then by timestamp
  const sortedMsgs = [...msgs].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1
    if (!a.is_pinned && b.is_pinned) return 1
    return new Date(b.timestamp) - new Date(a.timestamp)
  })

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md h-full flex flex-col">
      {/* Header with Search */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">Inbox</h3>
          <span className="text-sm text-gray-500 dark:text-gray-400">{msgs.length} messages</span>
        </div>
        
        {/* Search Bar */}
        <div className="relative">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search emails..."
            className="w-full px-4 py-2 pl-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#007ACC] dark:bg-gray-700 dark:text-white"
          />
          <svg className="w-5 h-5 absolute left-3 top-2.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Email List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#007ACC]"></div>
          </div>
        ) : sortedMsgs.length === 0 ? (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            {searchQuery ? 'No messages found' : 'No messages in inbox'}
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {sortedMsgs.map(m=> (
              <div
                key={m.id}
                className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                  !m.is_read ? 'bg-blue-50 dark:bg-blue-900 dark:bg-opacity-20' : ''
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    {/* Header Row */}
                    <div className="flex items-center gap-2 mb-1">
                      {m.is_pinned && (
                        <span className="text-yellow-500" title="Pinned">📌</span>
                      )}
                      <h4 className={`font-semibold truncate ${
                        !m.is_read ? 'text-gray-900 dark:text-white' : 'text-gray-700 dark:text-gray-300'
                      }`}>
                        {m.subject || '(no subject)'}
                      </h4>
                      {!m.is_read && (
                        <span className="w-2 h-2 bg-[#007ACC] rounded-full flex-shrink-0"></span>
                      )}
                    </div>
                    
                    {/* Sender */}
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      From: {m.sender}
                    </p>
                    
                    {/* Preview */}
                    <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-2">
                      {m.body.substring(0,150)}{m.body.length > 150 ? '...' : ''}
                    </p>
                    
                    {/* Timestamp */}
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                      {new Date(m.timestamp).toLocaleString()}
                    </p>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-col gap-1 flex-shrink-0">
                    <button
                      onClick={() => togglePin(m.id, m.is_pinned)}
                      className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors"
                      title={m.is_pinned ? 'Unpin' : 'Pin'}
                    >
                      {m.is_pinned ? '📌' : '📍'}
                    </button>
                    <button
                      onClick={() => toggleRead(m.id, m.is_read)}
                      className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors"
                      title={m.is_read ? 'Mark as unread' : 'Mark as read'}
                    >
                      {m.is_read ? '📭' : '📬'}
                    </button>
                    <button
                      onClick={() => deleteEmail(m.id)}
                      className="p-2 hover:bg-red-100 dark:hover:bg-red-900 rounded transition-colors text-red-600 dark:text-red-400"
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Toast Notification */}
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
