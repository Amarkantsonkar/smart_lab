import { useState } from 'react'

const LoginForm = ({ onLogin, loading }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  })
  const [errors, setErrors] = useState({})

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required'
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters long'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (validateForm()) {
      onLogin(formData)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <div className="form-header">
        <h2>Smart Lab Power Shutdown</h2>
        <p>Secure access to lab power management system</p>
      </div>
      
      {Object.keys(errors).length > 0 && (
        <div className="form-error">
          Please correct the errors below.
        </div>
      )}
      
      <div className="form-group">
        <label htmlFor="username">Username</label>
        <input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          className={errors.username ? 'error' : ''}
          placeholder="Enter your username"
        />
        {errors.username && <span className="error-message">{errors.username}</span>}
      </div>
      
      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          className={errors.password ? 'error' : ''}
          placeholder="Enter your password"
        />
        {errors.password && <span className="error-message">{errors.password}</span>}
      </div>
      
      <button 
        type="submit" 
        className="btn-primary"
        disabled={loading}
      >
        {loading ? 'Signing in...' : 'Sign In'}
      </button>
      
      <p className="form-footer">
        Demo credentials: admin/admin123 or engineer/engineer123
      </p>
    </form>
  )
}

export default LoginForm