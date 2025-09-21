import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import api from '../services/api'
import notifications from '../services/notifications'
import ConfirmationDialog from '../components/ConfirmationDialog'

const ShutdownControl = () => {
  const { user } = useAuth()
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [shutdownStatus, setShutdownStatus] = useState({})
  const [showShutdownAllDialog, setShowShutdownAllDialog] = useState(false)
  const [shutdownAllStatus, setShutdownAllStatus] = useState('idle')
  const [validationResult, setValidationResult] = useState({ allCompleted: false, incompleteItems: [] })

  useEffect(() => {
    fetchUserDevices()
    validateChecklist()
    
    // Listen for checklist updates from other components
    const handleChecklistUpdated = () => {
      validateChecklist()
    }
    
    window.addEventListener('checklist-updated', handleChecklistUpdated)
    
    return () => {
      window.removeEventListener('checklist-updated', handleChecklistUpdated)
    }
  }, [])

  const fetchUserDevices = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/v1/devices/')
      
      // Filter devices based on user role and assignments
      let userDevices = response.data
      
      if (user.role === 'Engineer') {
        // Engineers can only see their assigned devices
        userDevices = response.data.filter(device => 
          user.assignedDevices && user.assignedDevices.includes(device.deviceId)
        )
      }
      // Admins can see all devices (no filtering)
      
      setDevices(userDevices)
      setError('')
    } catch (err) {
      const errorMessage = err.userMessage || 'Failed to load devices'
      setError(errorMessage)
      notifications.error(errorMessage)
      console.error('Error fetching devices:', err)
    } finally {
      setLoading(false)
    }
  }

  const validateChecklist = async () => {
    try {
      const response = await api.post('/api/v1/shutdown/validate-checklist')
      setValidationResult(response.data)
    } catch (err) {
      const errorMessage = err.userMessage || 'Failed to validate checklist'
      setError(errorMessage)
      notifications.error(errorMessage)
      console.error('Error validating checklist:', err)
    }
  }

  const handleShutdown = async (deviceId) => {
    if (!validationResult?.allCompleted) {
      setError('Cannot shutdown: critical checklist items are incomplete')
      return
    }

    try {
      setShutdownStatus(prev => ({ ...prev, [deviceId]: 'shutting_down' }))
      
      const response = await api.post(`/api/v1/shutdown/initiate/${deviceId}`)
      
      // Update device status locally
      setDevices(prev => prev.map(device => 
        device.deviceId === deviceId 
          ? { ...device, status: 'off', lastShutdown: new Date().toISOString() }
          : device
      ))
      
      setShutdownStatus(prev => ({ ...prev, [deviceId]: 'success' }))
      
      // Show success message
      notifications.success(`Device ${deviceId} shutdown successfully`)
      
      // If all devices are off, show special message
      if (response.data.allDevicesOff) {
        notifications.success('All lab devices have been safely shut down!', 8000)
      }
      
      // Refresh checklist validation
      validateChecklist()
    } catch (err) {
      const errorMessage = err.userMessage || err.response?.data?.detail?.message || 'Failed to shutdown device'
      notifications.error(errorMessage)
      setShutdownStatus(prev => ({ ...prev, [deviceId]: 'error' }))
    }
  }

  const getDeviceStatusColor = (status) => {
    switch (status) {
      case 'on': return 'bg-green-500'
      case 'off': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const handleShutdownAll = () => {
    if (!validationResult?.allCompleted) {
      setError('Cannot shutdown all devices: critical checklist items are incomplete')
      return
    }

    const activeDevices = devices.filter(device => device.status === 'on')
    if (activeDevices.length === 0) {
      setError('No active devices to shutdown')
      return
    }

    setShowShutdownAllDialog(true)
  }

  const confirmShutdownAll = async () => {
    try {
      setShutdownAllStatus('shutting_down')
      setShowShutdownAllDialog(false)
      
      const activeDevices = devices.filter(device => device.status === 'on')
      
      // Shutdown all active devices sequentially
      for (const device of activeDevices) {
        setShutdownStatus(prev => ({ ...prev, [device.deviceId]: 'shutting_down' }))
        
        try {
          await api.post(`/api/v1/shutdown/initiate/${device.deviceId}`)
          setShutdownStatus(prev => ({ ...prev, [device.deviceId]: 'success' }))
        } catch (err) {
          setShutdownStatus(prev => ({ ...prev, [device.deviceId]: 'error' }))
          console.error(`Failed to shutdown device ${device.deviceId}:`, err)
        }
      }
      
      // Update all device statuses locally
      setDevices(prev => prev.map(device => 
        device.status === 'on' 
          ? { ...device, status: 'off', lastShutdown: new Date().toISOString() }
          : device
      ))
      
      setShutdownAllStatus('success')
      notifications.success('All lab devices have been safely shut down!', 8000)
      
      // Clear status after delay
      setTimeout(() => {
        setShutdownAllStatus('idle')
      }, 3000)
      
      // Refresh validation
      validateChecklist()
    } catch (err) {
      setShutdownAllStatus('error')
      notifications.error('Failed to shutdown all devices')
      console.error('Error during shutdown all:', err)
      
      setTimeout(() => {
        setShutdownAllStatus('idle')
      }, 3000)
    }
  }

  const cancelShutdownAll = () => {
    setShowShutdownAllDialog(false)
  }

  const getShutdownButtonStatus = (deviceId) => {
    if (shutdownStatus[deviceId] === 'shutting_down') return 'Shutting Down...'
    if (shutdownStatus[deviceId] === 'success') return 'Shutdown Complete'
    if (shutdownStatus[deviceId] === 'error') return 'Error - Retry'
    return 'Shutdown'
  }

  const getValidationStatusClass = () => {
    return validationResult?.allCompleted ? 'validation-status ready' : 'validation-status blocked'
  }

  const getActiveDevicesCount = () => {
    return devices.filter(device => device.status === 'on').length
  }

  return (
    <div className="shutdown-control">
      <h1>Shutdown Control Panel</h1>
      
      {error && <div className={`alert ${error.includes('successfully') ? 'alert-success' : 'alert-error'}`}>{error}</div>}
      
      {/* Validation Status Card */}
      <div className={getValidationStatusClass()}>
        {validationResult?.allCompleted ? (
          <div>
            <strong>✅ Ready for Shutdown</strong>
            <p>All critical checklist items have been completed. Devices can be safely shut down.</p>
          </div>
        ) : (
          <div>
            <strong>⚠️ Shutdown Blocked</strong>
            <p>{validationResult?.incompleteItems?.length || 0} critical checklist items remaining. Complete all critical tasks before shutdown.</p>
          </div>
        )}
      </div>
      
      {loading ? (
        <div className="loading">Loading your devices...</div>
      ) : (
        <>
          {/* Device Grid */}
          <div className="devices-grid">
            {devices.map(device => (
              <div key={device.deviceId} className="device-card">
                <h3>{device.name}</h3>
                <p>ID: {device.deviceId}</p>
                <div className="device-status">
                  <span className={`status-indicator ${getDeviceStatusColor(device.status)}`}></span>
                  <span>Status: {device.status}</span>
                </div>
                {device.location && <p>Location: {device.location}</p>}
                {device.lastShutdown && <p>Last Shutdown: {new Date(device.lastShutdown).toLocaleString()}</p>}
                
                <button
                  onClick={() => handleShutdown(device.deviceId)}
                  disabled={device.status === 'off' || shutdownStatus[device.deviceId] === 'shutting_down' || !validationResult?.allCompleted}
                  className={`shutdown-button ${
                    device.status === 'off' ? 'disabled' : 
                    shutdownStatus[device.deviceId] === 'success' ? 'success' : 
                    shutdownStatus[device.deviceId] === 'error' ? 'error' : ''
                  }`}
                >
                  {getShutdownButtonStatus(device.deviceId)}
                </button>
              </div>
            ))}
          </div>
          
          {/* Shutdown All Section */}
          {getActiveDevicesCount() > 1 && (
            <div className="shutdown-all-section">
              <h3>Shutdown All Devices</h3>
              <p>Shutdown all {getActiveDevicesCount()} active devices at once.</p>
              <button
                onClick={handleShutdownAll}
                disabled={!validationResult?.allCompleted || shutdownAllStatus === 'shutting_down'}
                className="shutdown-all-button"
              >
                {shutdownAllStatus === 'shutting_down' ? 'Shutting Down All Devices...' : `Shutdown All ${getActiveDevicesCount()} Devices`}
              </button>
            </div>
          )}
        </>
      )}
      
      {/* Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showShutdownAllDialog}
        title="Shutdown All Devices?"
        message={`Are you sure you want to shutdown all ${getActiveDevicesCount()} active devices? This action cannot be undone.`}
        onConfirm={confirmShutdownAll}
        onCancel={cancelShutdownAll}
      />
    </div>
  )
}

export default ShutdownControl