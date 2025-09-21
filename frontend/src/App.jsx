import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import Layout from './components/Layout'
import './services/notifications' // Initialize notification service

// Lazy load components for better performance
const Login = lazy(() => import('./pages/Login'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Checklist = lazy(() => import('./pages/Checklist'))
const ShutdownControl = lazy(() => import('./pages/ShutdownControl'))
const Reports = lazy(() => import('./pages/Reports'))
const DeviceManagement = lazy(() => import('./pages/DeviceManagement'))
const Profile = lazy(() => import('./pages/Profile'))

// Loading component
const PageLoader = () => (
  <div className="page-loader">
    <div className="loader-spinner"></div>
    <p>Loading...</p>
  </div>
)

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Login />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="checklist" element={<Checklist />} />
              <Route path="shutdown" element={<ShutdownControl />} />
              <Route path="reports" element={<Reports />} />
              <Route path="device-management" element={<DeviceManagement />} />
              <Route path="profile" element={<Profile />} />
            </Route>
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App