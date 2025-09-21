import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import api from '../services/api'
import notifications from '../services/notifications'
import ConfirmationDialog from '../components/ConfirmationDialog'

const Profile = () => {
  const { user, refreshUser } = useAuth()
  const [formData, setFormData] = useState({
    name: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showChangePasswordDialog, setShowChangePasswordDialog] = useState(false)
  const [showChangeUsernameDialog, setShowChangeUsernameDialog] = useState(false)

  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        name: user.name
      }))
    }
  }, [user])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    setError('')
  }

  const validatePasswordChange = () => {
    if (!formData.currentPassword) {
      setError('Current password is required')
      return false
    }
    if (!formData.newPassword) {
      setError('New password is required')
      return false
    }
    if (formData.newPassword.length < 6) {
      setError('New password must be at least 6 characters long')
      return false
    }
    if (formData.newPassword !== formData.confirmPassword) {
      setError('Passwords do not match')
      return false
    }
    return true
  }

  const handleChangePassword = () => {
    if (validatePasswordChange()) {
      setShowChangePasswordDialog(true)
    }
  }

  const confirmChangePassword = async () => {
    try {
      setLoading(true)
      
      // First verify current password by attempting login
      await api.post('/api/v1/auth/login', {
        username: user.name,
        password: formData.currentPassword
      })
      
      // If login successful, update password
      await api.put('/api/v1/auth/profile', {
        password: formData.newPassword
      })
      
      setFormData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }))
      
      setShowChangePasswordDialog(false)
      notifications.success('Password updated successfully')
      setError('')
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.userMessage || 'Failed to update password'
      setError(errorMessage)
      notifications.error(errorMessage)
      setShowChangePasswordDialog(false)
    } finally {
      setLoading(false)
    }
  }

  const handleChangeUsername = () => {
    if (!formData.name.trim()) {
      setError('Username cannot be empty')
      return
    }
    if (formData.name === user.name) {
      setError('New username must be different from current username')
      return
    }
    setShowChangeUsernameDialog(true)
  }

  const confirmChangeUsername = async () => {
    try {
      setLoading(true)
      
      await api.put('/api/v1/auth/profile', {
        name: formData.name.trim()
      })
      
      // Refresh user data to get updated information
      await refreshUser()
      
      setShowChangeUsernameDialog(false)
      notifications.success('Username updated successfully')
      setError('')
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.userMessage || 'Failed to update username'
      setError(errorMessage)
      notifications.error(errorMessage)
      setShowChangeUsernameDialog(false)
      
      // Reset username to original value on error
      setFormData(prev => ({
        ...prev,
        name: user.name
      }))
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="profile">
        <div className="loading">Loading profile...</div>
      </div>
    )
  }

  return (
    <div className="profile">
      <h1>User Profile</h1>
      <p>Manage your account information</p>
      
      {error && <div className="alert alert-error">{error}</div>}
      
      <div className="profile-sections">
        {/* Profile Information */}
        <div className="profile-section">
          <h2>Profile Information</h2>
          <div className="profile-info">
            <div className="info-item">
              <label>Role:</label>
              <span className={`role-badge ${user.role.toLowerCase()}`}>{user.role}</span>
            </div>
            <div className="info-item">
              <label>Member Since:</label>
              <span>{new Date(user.createdAt).toLocaleDateString()}</span>
            </div>
            <div className="info-item">
              <label>Last Updated:</label>
              <span>{new Date(user.updatedAt).toLocaleDateString()}</span>
            </div>
            <div className="info-item">
              <label>Assigned Devices:</label>
              <span>{user.assignedDevices.length} devices</span>
            </div>
          </div>
        </div>
        
        {/* Change Username */}
        <div className="profile-section">
          <h2>Change Username</h2>
          <div className="form-group">
            <label htmlFor="name">Username:</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="Enter new username"
              disabled={loading}
            />
          </div>
          <button
            onClick={handleChangeUsername}
            disabled={loading || formData.name === user.name || !formData.name.trim()}
            className="button button-primary"
          >
            {loading ? 'Updating...' : 'Update Username'}
          </button>
        </div>
        
        {/* Change Password */}
        <div className="profile-section">
          <h2>Change Password</h2>
          <div className="form-group">
            <label htmlFor="currentPassword">Current Password:</label>
            <input
              type="password"
              id="currentPassword"
              name="currentPassword"
              value={formData.currentPassword}
              onChange={handleInputChange}
              placeholder="Enter current password"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="newPassword">New Password:</label>
            <input
              type="password"
              id="newPassword"
              name="newPassword"
              value={formData.newPassword}
              onChange={handleInputChange}
              placeholder="Enter new password (min 6 characters)"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password:</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              placeholder="Confirm new password"
              disabled={loading}
            />
          </div>
          <button
            onClick={handleChangePassword}
            disabled={loading || !formData.currentPassword || !formData.newPassword || !formData.confirmPassword}
            className="button button-primary"
          >
            {loading ? 'Updating...' : 'Update Password'}
          </button>
        </div>
      </div>
      
      {/* Change Username Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showChangeUsernameDialog}
        title="Change Username"
        message={`Are you sure you want to change your username from "${user.name}" to "${formData.name}"?`}
        onConfirm={confirmChangeUsername}
        onCancel={() => setShowChangeUsernameDialog(false)}
        type="info"
      />
      
      {/* Change Password Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showChangePasswordDialog}
        title="Change Password"
        message="Are you sure you want to change your password? You will need to use the new password for future logins."
        onConfirm={confirmChangePassword}
        onCancel={() => setShowChangePasswordDialog(false)}
        type="warning"
      />
    </div>
  )
}

export default Profile