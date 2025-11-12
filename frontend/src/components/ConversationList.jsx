import React from 'react'

export default function ConversationList({conversations, selectedConversation, onSelectConversation, searchQuery, onSearchChange, token}){
  const formatTime = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    const now = new Date()
    const diffInHours = (now - date) / (1000 * 60 * 60)
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})
    } else if (diffInHours < 168) {
      return date.toLocaleDateString('en-US', {weekday: 'short'})
    } else {
      return date.toLocaleDateString('en-US', {month: 'short', day: 'numeric'})
    }
  }

  return (
    <div className="w-[400px] bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Search bar */}
      <div className="p-3 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
        <div className="relative">
          <input
            type="text"
            placeholder="Search or start new conversation"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full px-4 py-2 pl-10 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 focus:outline-none focus:border-[#007ACC] dark:focus:border-[#0098FF] text-sm"
          />
          <svg className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">
            No messages yet
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => onSelectConversation(conv)}
              className={`px-4 py-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700 transition-colors ${
                selectedConversation?.id === conv.id ? 'bg-gray-100 dark:bg-gray-700' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* Sender name - on top */}
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-10 h-10 rounded-full bg-[#007ACC] dark:bg-[#0098FF] flex items-center justify-center text-white font-semibold flex-shrink-0">
                      {conv.sender.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-gray-900 dark:text-white truncate text-sm">
                        {conv.sender}
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {conv.subject || 'No subject'}
                      </p>
                    </div>
                  </div>
                  {/* Message preview */}
                  <p className="text-sm text-gray-600 dark:text-gray-300 truncate pl-12">
                    {conv.body.substring(0, 50)}...
                  </p>
                </div>
                {/* Time */}
                <span className="text-xs text-gray-500 dark:text-gray-400 ml-2 flex-shrink-0">
                  {formatTime(conv.timestamp)}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
