import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import Navbar from './Navbar'

const Layout = () => {
  const { user } = useAuth()
  const location = useLocation()

  const isActive = (path) => {
    return location.pathname === path ? 'nav-link active' : 'nav-link'
  }

  return (
    <div className="app-container">
      <Navbar />
      {user && (
        <nav className="main-nav">
          <div className="nav-container">
            <Link to="/dashboard" className={isActive('/dashboard')}>
              📊 Dashboard
            </Link>
            <Link to="/checklist" className={isActive('/checklist')}>
              ✅ Checklist
            </Link>
            <Link to="/shutdown" className={isActive('/shutdown')}>
              🔌 Shutdown Control
            </Link>
            <Link to="/reports" className={isActive('/reports')}>
              📈 Reports
            </Link>
            {user.role === 'Admin' && (
              <Link to="/device-management" className={isActive('/device-management')}>
                ⚙️ Device Management
              </Link>
            )}
            <Link to="/profile" className={isActive('/profile')}>
              👤 Profile
            </Link>
          </div>
        </nav>
      )}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout