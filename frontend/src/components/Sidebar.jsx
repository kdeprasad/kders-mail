import React, {useState, useEffect} from 'react'
import axios from 'axios'

export default function Sidebar({token, email}){
  const [activeTab, setActiveTab] = useState('groups') // 'groups' or 'users'
  const [groups, setGroups] = useState([])
  const [users, setUsers] = useState([])
  const [searchQuery, setSearchQuery] = useState('')
  const [isTeacher, setIsTeacher] = useState(false)
  const [showCreateGroup, setShowCreateGroup] = useState(false)
  const [newGroupName, setNewGroupName] = useState('')
  const [selectedGroupMembers, setSelectedGroupMembers] = useState([])

  // Fetch groups
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const response = await axios.get('/api/groups', {
          headers: {Authorization: `Bearer ${token}`}
        })
        setGroups(response.data || [])
      } catch (error) {
        console.error('Failed to fetch groups:', error)
      }
    }
    fetchGroups()
  }, [token])

  // Check if user is teacher
  useEffect(() => {
    const checkTeacherStatus = async () => {
      try {
        // Decode JWT to check if teacher (simple client-side check)
        const payload = JSON.parse(atob(token.split('.')[1]))
        setIsTeacher(payload.is_teacher === true)
      } catch (error) {
        console.error('Failed to decode token:', error)
      }
    }
    checkTeacherStatus()
  }, [token])

  // Search users (when typing in search)
  useEffect(() => {
    if (activeTab === 'users' && searchQuery.length > 0) {
      const searchUsers = async () => {
        try {
          const response = await axios.get(`/api/users/search?q=${encodeURIComponent(searchQuery)}`, {
            headers: {Authorization: `Bearer ${token}`}
          })
          setUsers(response.data || [])
        } catch (error) {
          console.error('Failed to search users:', error)
          setUsers([])
        }
      }
      const debounce = setTimeout(searchUsers, 300)
      return () => clearTimeout(debounce)
    } else {
      setUsers([])
    }
  }, [searchQuery, activeTab, token])

  const handleCreateGroup = async (e) => {
    e.preventDefault()
    if (!newGroupName.trim()) return

    try {
      await axios.post('/api/groups', 
        {name: newGroupName}, 
        {headers: {Authorization: `Bearer ${token}`}}
      )
      
      // Refresh groups
      const response = await axios.get('/api/groups', {
        headers: {Authorization: `Bearer ${token}`}
      })
      setGroups(response.data || [])
      
      setNewGroupName('')
      setShowCreateGroup(false)
      alert('Group created successfully!')
    } catch (error) {
      console.error('Failed to create group:', error)
      alert('Failed to create group')
    }
  }

  const handleSendGroupMessage = async (group) => {
    const subject = prompt(`Subject for message to ${group.name}:`)
    if (!subject) return
    
    const body = prompt(`Message body:`)
    if (!body) return

    try {
      // Get group members
      const membersResponse = await axios.get(`/api/groups/${group.id}/members`, {
        headers: {Authorization: `Bearer ${token}`}
      })
      const members = membersResponse.data || []
      
      // Send message to each member
      for (const member of members) {
        await axios.post('/api/mail/compose', 
          {recipient: member.email, subject: `[${group.name}] ${subject}`, body}, 
          {headers: {Authorization: `Bearer ${token}`}}
        )
      }
      
      alert('Group message sent successfully!')
    } catch (error) {
      console.error('Failed to send group message:', error)
      alert('Failed to send group message')
    }
  }

  return (
    <div className="w-[280px] bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setActiveTab('groups')}
          className={`flex-1 py-3 text-sm font-semibold transition-colors ${
            activeTab === 'groups'
              ? 'text-[#007ACC] dark:text-[#0098FF] border-b-2 border-[#007ACC] dark:border-[#0098FF]'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          Groups
        </button>
        <button
          onClick={() => setActiveTab('users')}
          className={`flex-1 py-3 text-sm font-semibold transition-colors ${
            activeTab === 'users'
              ? 'text-[#007ACC] dark:text-[#0098FF] border-b-2 border-[#007ACC] dark:border-[#0098FF]'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          Users
        </button>
      </div>

      {/* Search bar */}
      {activeTab === 'users' && (
        <div className="p-3 border-b border-gray-200 dark:border-gray-700">
          <input
            type="text"
            placeholder="Search users..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 focus:outline-none focus:border-[#007ACC] dark:focus:border-[#0098FF]"
          />
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'groups' && (
          <div>
            {isTeacher && (
              <div className="p-3 border-b border-gray-200 dark:border-gray-700">
                {!showCreateGroup ? (
                  <button
                    onClick={() => setShowCreateGroup(true)}
                    className="w-full px-3 py-2 bg-[#007ACC] hover:bg-[#005A9E] text-white rounded text-sm font-semibold transition-colors"
                  >
                    + Create Group
                  </button>
                ) : (
                  <form onSubmit={handleCreateGroup} className="space-y-2">
                    <input
                      type="text"
                      placeholder="Group name"
                      value={newGroupName}
                      onChange={(e) => setNewGroupName(e.target.value)}
                      className="w-full px-3 py-2 text-sm rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:border-[#007ACC]"
                      required
                    />
                    <div className="flex gap-2">
                      <button
                        type="submit"
                        className="flex-1 px-3 py-1 bg-[#007ACC] hover:bg-[#005A9E] text-white rounded text-sm transition-colors"
                      >
                        Create
                      </button>
                      <button
                        type="button"
                        onClick={() => {setShowCreateGroup(false); setNewGroupName('')}}
                        className="flex-1 px-3 py-1 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded text-sm transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                )}
              </div>
            )}

            {groups.length === 0 ? (
              <div className="p-4 text-center text-sm text-gray-500 dark:text-gray-400">
                No groups yet
              </div>
            ) : (
              <div>
                {groups.map((group) => (
                  <div
                    key={group.id}
                    className="px-3 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-10 h-10 rounded-full bg-[#007ACC] dark:bg-[#0098FF] flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
                        {group.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-sm text-gray-900 dark:text-white truncate">
                          {group.name}
                        </h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Group</p>
                      </div>
                    </div>
                    {isTeacher && (
                      <button
                        onClick={() => handleSendGroupMessage(group)}
                        className="mt-2 w-full px-2 py-1 bg-[#007ACC] hover:bg-[#005A9E] text-white rounded text-xs transition-colors"
                      >
                        Send Message
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'users' && (
          <div>
            {searchQuery === '' ? (
              <div className="p-4 text-center text-sm text-gray-500 dark:text-gray-400">
                Type to search users
              </div>
            ) : users.length === 0 ? (
              <div className="p-4 text-center text-sm text-gray-500 dark:text-gray-400">
                No users found
              </div>
            ) : (
              users.map((user) => (
                <div
                  key={user.id}
                  className="px-3 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-100 dark:border-gray-700 cursor-pointer transition-colors"
                  onClick={() => {
                    // Could trigger compose to this user
                    alert(`Start conversation with ${user.email}`)
                  }}
                >
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-semibold">
                      {user.email.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-sm text-gray-900 dark:text-white truncate">
                        {user.full_name || user.email}
                      </h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {user.email}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

    </div>
  )
}
