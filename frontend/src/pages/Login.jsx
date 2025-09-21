import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import notifications from '../services/notifications'
import LoginForm from '../components/LoginForm'

const Login = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (credentials) => {
    try {
      setLoading(true)
      setError('')
      
      // Call the backend login endpoint
      const response = await api.post('/api/v1/auth/login', {
        username: credentials.username,
        password: credentials.password
      })
      
      // Store token first so it's available for subsequent requests
      const token = response.data.access_token
      localStorage.setItem('access_token', token)
      
      // Get user info (now with token in localStorage)
      const userResponse = await api.get('/api/v1/auth/me')
      
      // Store user info and call auth hook
      login(userResponse.data, token)
      
      // Show success notification
      notifications.success(`Welcome back, ${userResponse.data.name}!`, 3000)
      
    } catch (err) {
      let errorMessage = 'Invalid username or password'
      
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail
        // Handle both string and object detail formats
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (detail.message) {
          errorMessage = detail.message
        }
      } else if (err.userMessage) {
        errorMessage = err.userMessage
      }
      
      setError(errorMessage)
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <LoginForm onLogin={handleLogin} loading={loading} />
      {error && <div className="auth-error">{error}</div>}
    </div>
  )
}

export default Login