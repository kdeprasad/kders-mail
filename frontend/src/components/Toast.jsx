import React, { useEffect } from 'react'

export default function Toast({ message, type = 'success', onClose, duration = 3000 }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose()
    }, duration)
    return () => clearTimeout(timer)
  }, [duration, onClose])

  const bgColor = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
    warning: 'bg-yellow-500'
  }[type] || 'bg-gray-500'

  const icon = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
    warning: '⚠'
  }[type] || 'ℹ'

  return (
    <div className={`fixed bottom-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3 animate-slide-up z-50`}>
      <span className="text-xl font-bold">{icon}</span>
      <span className="font-medium">{message}</span>
      <button 
        onClick={onClose}
        className="ml-4 hover:bg-white hover:bg-opacity-20 rounded-full w-6 h-6 flex items-center justify-center transition-colors"
      >
        ✕
      </button>
    </div>
  )
}
