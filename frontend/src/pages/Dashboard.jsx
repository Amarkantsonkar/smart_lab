import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import notifications from '../services/notifications'
import api from '../services/api'

const Dashboard = () => {
  const { user } = useAuth()
  const [devices, setDevices] = useState([])
  const [displayDevices, setDisplayDevices] = useState([])
  const [checklistStats, setChecklistStats] = useState(null)
  const [recentLogs, setRecentLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshInterval, setRefreshInterval] = useState(15) // seconds

  useEffect(() => {
    fetchDashboardData()
  }, [])
  
  useEffect(() => {
    let interval
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchDashboardData(false) // Silent refresh
      }, refreshInterval * 1000)
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [autoRefresh, refreshInterval])

  const fetchDashboardData = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true)
      } else {
        setRefreshing(true)
      }
      
      // Fetch all dashboard data in parallel
      const [devicesResponse, checklistResponse, logsResponse] = await Promise.all([
        api.get('/api/v1/devices/'),
        api.get('/api/v1/checklist/'),
        api.get('/api/v1/shutdown-logs/?limit=5')
      ])
      
      setDevices(devicesResponse.data)
      
      // Filter devices for display based on user role
      const filteredDevices = user.role === 'Engineer' 
        ? devicesResponse.data.filter(device => 
            user.assignedDevices && user.assignedDevices.includes(device.deviceId)
          )
        : devicesResponse.data // Admins see all devices
      
      setDisplayDevices(filteredDevices)
      
      // Calculate checklist statistics
      const checklistItems = checklistResponse.data
      const totalItems = checklistItems.length
      const completedItems = checklistItems.filter(item => item.completed).length
      const criticalItems = checklistItems.filter(item => item.isCritical)
      const criticalCompleted = criticalItems.filter(item => item.completed).length
      
      setChecklistStats({
        total: totalItems,
        completed: completedItems,
        critical: criticalItems.length,
        criticalCompleted: criticalCompleted,
        completionPercentage: totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0,
        criticalCompletionPercentage: criticalItems.length > 0 ? Math.round((criticalCompleted / criticalItems.length) * 100) : 0
      })
      
      setRecentLogs(logsResponse.data)
      setLastUpdated(new Date())
      setError('')
    } catch (err) {
      const errorMessage = err.userMessage || 'Failed to load dashboard data'
      
      // Only show error notifications for manual refreshes to avoid spam
      if (showLoading) {
        setError(errorMessage)
        notifications.error(errorMessage)
      }
      console.error('Error fetching dashboard data:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const getDeviceStatusColor = (status) => {
    switch (status) {
      case 'on': return 'bg-green-500'
      case 'off': return 'bg-red-500'
      case 'maintenance': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  const getSystemHealthStatus = () => {
    if (!displayDevices.length) return { status: 'unknown', message: 'No devices available' }
    
    const activeDevices = displayDevices.filter(d => d.status === 'on').length
    const totalDevices = displayDevices.length
    const percentage = (activeDevices / totalDevices) * 100
    
    if (percentage === 0) {
      return { status: 'shutdown', message: 'All systems offline', color: 'text-red-600' }
    } else if (percentage < 50) {
      return { status: 'warning', message: 'Partial system shutdown', color: 'text-yellow-600' }
    } else {
      return { status: 'operational', message: 'Systems operational', color: 'text-green-600' }
    }
  }

  const refreshData = () => {
    fetchDashboardData(true)
    notifications.info('Dashboard data refreshed', 2000)
  }
  
  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh)
    notifications.info(`Auto-refresh ${!autoRefresh ? 'enabled' : 'disabled'}`, 2000)
  }
  
  const handleRefreshIntervalChange = (newInterval) => {
    setRefreshInterval(newInterval)
    notifications.info(`Refresh interval set to ${newInterval} seconds`, 2000)
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Lab System Dashboard</h1>
        <div className="dashboard-controls">
          <div className="refresh-controls">
            <label className="refresh-interval-label">
              Refresh Interval:
              <select 
                value={refreshInterval} 
                onChange={(e) => handleRefreshIntervalChange(Number(e.target.value))}
                className="refresh-interval-select"
              >
                <option value={5}>5 seconds</option>
                <option value={10}>10 seconds</option>
                <option value={15}>15 seconds</option>
                <option value={30}>30 seconds</option>
                <option value={60}>1 minute</option>
              </select>
            </label>
            <button 
              onClick={toggleAutoRefresh} 
              className={`button ${autoRefresh ? 'button-success' : 'button-secondary'}`}
            >
              {autoRefresh ? '🔄 Auto-refresh ON' : '⏸️ Auto-refresh OFF'}
            </button>
          </div>
          <div className="status-info">
            <span className="last-updated">
              Last updated: {lastUpdated.toLocaleTimeString()}
              {refreshing && <span className="refreshing-indicator"> 🔄</span>}
            </span>
            <button onClick={refreshData} className="button button-primary" disabled={loading || refreshing}>
              {refreshing ? 'Refreshing...' : 'Refresh Now'}
            </button>
          </div>
        </div>
      </div>
      
      {error && <div className="alert alert-error">{error}</div>}
      
      {loading ? (
        <div className="loading">Loading dashboard...</div>
      ) : (
        <>
          {/* System Status Overview */}
          <div className="system-status">
            <div className={`status-card ${getSystemHealthStatus().status}`}>
              <h2 className={getSystemHealthStatus().color}>{getSystemHealthStatus().message}</h2>
              <p>{displayDevices.filter(d => d.status === 'on').length} of {displayDevices.length} devices online</p>
            </div>
          </div>
          
          {/* Statistics Grid */}
          <div className="stats-grid">
            <div className="stat-card device-stats">
              <h3>Device Status</h3>
              <div className="stat-details">
                <div className="stat-item">
                  <span className="stat-label">Total Devices:</span>
                  <span className="stat-value">{displayDevices.length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Powered On:</span>
                  <span className="stat-value text-green-600">{displayDevices.filter(d => d.status === 'on').length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Powered Off:</span>
                  <span className="stat-value text-red-600">{displayDevices.filter(d => d.status === 'off').length}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">In Maintenance:</span>
                  <span className="stat-value text-yellow-600">{displayDevices.filter(d => d.status === 'maintenance').length}</span>
                </div>
              </div>
            </div>
            
            {checklistStats && (
              <div className="stat-card checklist-stats">
                <h3>Maintenance Checklist</h3>
                <div className="stat-details">
                  <div className="stat-item">
                    <span className="stat-label">Overall Progress:</span>
                    <span className="stat-value">{checklistStats.completionPercentage}%</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Critical Tasks:</span>
                    <span className={`stat-value ${checklistStats.criticalCompletionPercentage === 100 ? 'text-green-600' : 'text-red-600'}`}>
                      {checklistStats.criticalCompleted}/{checklistStats.critical}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Ready for Shutdown:</span>
                    <span className={`stat-value ${checklistStats.criticalCompletionPercentage === 100 ? 'text-green-600' : 'text-red-600'}`}>
                      {checklistStats.criticalCompletionPercentage === 100 ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
              </div>
            )}
            
            <div className="stat-card user-info">
              <h3>User Information</h3>
              <div className="stat-details">
                <div className="stat-item">
                  <span className="stat-label">Role:</span>
                  <span className="stat-value">{user.role}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Assigned Devices:</span>
                  <span className="stat-value">{user.assignedDevices?.length || 0}</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Recent Activity */}
          {recentLogs.length > 0 && (
            <div className="recent-activity">
              <h3>Recent Shutdown Activity</h3>
              <div className="activity-list">
                {recentLogs.map((log, index) => (
                  <div key={log.logId || log._id || `log-${index}-${log.timestamp}`} className="activity-item">
                    <div className="activity-icon">
                      {log.success ? '✅' : '❌'}
                    </div>
                    <div className="activity-details">
                      <p className="activity-description">
                        {log.success ? 'Successfully shutdown' : 'Failed to shutdown'} device {log.deviceId}
                      </p>
                      <p className="activity-meta">
                        by {log.userId} • {new Date(log.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Device Grid */}
          <div className="dashboard-devices">
            <h3>All Devices</h3>
            <div className="devices-grid">
              {displayDevices.map((device, index) => (
                <div key={device.id || device._id || device.deviceId || `device-${index}`} className={`device-card ${device.status}`}>
                  <div className="device-header">
                    <h4>{device.name}</h4>
                    <span className={`status-indicator ${getDeviceStatusColor(device.status)}`}></span>
                  </div>
                  <div className="device-info">
                    <p>ID: {device.deviceId}</p>
                    <p>Status: {device.status}</p>
                    {device.location && <p>Location: {device.location}</p>}
                    {device.lastStartup && (
                      <p>Last Started: {new Date(device.lastStartup).toLocaleString()}</p>
                    )}
                    {device.lastShutdown && (
                      <p>Last Shutdown: {new Date(device.lastShutdown).toLocaleString()}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Dashboard