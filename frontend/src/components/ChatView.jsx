import React, {useState} from 'react'

export default function ChatView({conversation, onSendMessage, userEmail, token}){
  const [replyBody, setReplyBody] = useState('')
  const [isReplying, setIsReplying] = useState(false)
  const [newRecipient, setNewRecipient] = useState('')
  const [newSubject, setNewSubject] = useState('')
  const [newBody, setNewBody] = useState('')
  const [isComposing, setIsComposing] = useState(false)

  const handleSendReply = async (e) => {
    e.preventDefault()
    if (!replyBody.trim() || !conversation) return
    
    const success = await onSendMessage(
      conversation.sender,
      `Re: ${conversation.subject || 'No subject'}`,
      replyBody
    )
    
    if (success) {
      setReplyBody('')
      setIsReplying(false)
      alert('Reply sent!')
    }
  }

  const handleSendNew = async (e) => {
    e.preventDefault()
    if (!newRecipient.trim() || !newBody.trim()) return
    
    const success = await onSendMessage(newRecipient, newSubject, newBody)
    
    if (success) {
      setNewRecipient('')
      setNewSubject('')
      setNewBody('')
      setIsComposing(false)
      alert('Message sent!')
    }
  }

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (isComposing) {
    return (
      <div className="flex-1 bg-[#f0f2f5] dark:bg-gray-900 flex flex-col">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">New Message</h2>
            <button
              onClick={() => setIsComposing(false)}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Compose form */}
        <div className="flex-1 overflow-y-auto p-4">
          <form onSubmit={handleSendNew} className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
            <div className="mb-3">
              <input
                type="email"
                placeholder="To: email@example.com"
                value={newRecipient}
                onChange={(e) => setNewRecipient(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:border-[#007ACC] dark:focus:border-[#0098FF]"
                required
              />
            </div>
            <div className="mb-3">
              <input
                type="text"
                placeholder="Subject"
                value={newSubject}
                onChange={(e) => setNewSubject(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:border-[#007ACC] dark:focus:border-[#0098FF]"
              />
            </div>
            <div className="mb-3">
              <textarea
                placeholder="Type your message..."
                value={newBody}
                onChange={(e) => setNewBody(e.target.value)}
                rows={10}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:border-[#007ACC] dark:focus:border-[#0098FF] resize-none"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full px-4 py-2 bg-[#007ACC] hover:bg-[#005A9E] text-white rounded font-semibold transition-colors"
            >
              Send Message
            </button>
          </form>
        </div>
      </div>
    )
  }

  if (!conversation) {
    return (
      <div className="flex-1 bg-[#f0f2f5] dark:bg-gray-900 flex flex-col items-center justify-center">
        <div className="text-center">
          <div className="w-20 h-20 bg-[#008069] dark:bg-[#00a884] rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
            Select a conversation
          </h3>
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            Choose a message from the list or start a new one
          </p>
          <button
            onClick={() => setIsComposing(true)}
            className="px-6 py-2 bg-[#007ACC] hover:bg-[#005A9E] text-white rounded-full font-semibold transition-colors"
          >
            + New Message
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 bg-[#f0f2f5] dark:bg-gray-900 flex flex-col">
      {/* Chat header */}
      <div className="bg-white dark:bg-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#007ACC] dark:bg-[#0098FF] flex items-center justify-center text-white font-semibold">
            {conversation.sender.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="font-semibold text-gray-900 dark:text-white">{conversation.sender}</h2>
            <p className="text-xs text-gray-500 dark:text-gray-400">{conversation.subject || 'No subject'}</p>
          </div>
        </div>
        <button
          onClick={() => setIsComposing(true)}
          className="px-4 py-2 bg-[#007ACC] hover:bg-[#005A9E] text-white rounded text-sm transition-colors"
        >
          + New
        </button>
      </div>

      {/* Message display */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-3xl mx-auto">
          {/* Email message bubble */}
          <div className="mb-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">From: {conversation.sender}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">To: {conversation.recipient}</p>
                  {conversation.subject && (
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mt-1">
                      Subject: {conversation.subject}
                    </p>
                  )}
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {formatTimestamp(conversation.timestamp)}
                </span>
              </div>
              <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{conversation.body}</p>
              </div>
            </div>
          </div>

          {/* Reply section */}
          {!isReplying && (
            <button
              onClick={() => setIsReplying(true)}
              className="w-full px-4 py-2 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-[#007ACC] dark:text-[#0098FF] rounded-lg border border-[#007ACC] dark:border-[#0098FF] font-semibold transition-colors"
            >
              Reply
            </button>
          )}

          {isReplying && (
            <form onSubmit={handleSendReply} className="mt-4">
              <textarea
                value={replyBody}
                onChange={(e) => setReplyBody(e.target.value)}
                placeholder="Type your reply..."
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:border-[#007ACC] dark:focus:border-[#0098FF] resize-none"
                required
              />
              <div className="flex gap-2 mt-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-[#007ACC] hover:bg-[#005A9E] text-white rounded font-semibold transition-colors"
                >
                  Send Reply
                </button>
                <button
                  type="button"
                  onClick={() => {setIsReplying(false); setReplyBody('')}}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 rounded font-semibold transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
