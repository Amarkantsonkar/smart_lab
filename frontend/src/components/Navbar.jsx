import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

const Navbar = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        {user ? (
          <Link to="/dashboard">Smart Lab Power Shutdown</Link>
        ) : (
          <span>Smart Lab Power Shutdown</span>
        )}
      </div>
      <div className="navbar-menu">
        {user ? (
          <>
            <span className="navbar-item">Welcome, {user.name}</span>
            <button onClick={handleLogout} className="navbar-item button">
              Logout
            </button>
          </>
        ) : (
          location.pathname !== '/' && (
            <Link to="/" className="navbar-item">
              Login
            </Link>
          )
        )}
      </div>
    </nav>
  )
}

export default Navbar