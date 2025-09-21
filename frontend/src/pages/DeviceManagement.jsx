import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import api from '../services/api'
import notifications from '../services/notifications'
import ConfirmationDialog from '../components/ConfirmationDialog'

const DeviceManagement = () => {
  const { user } = useAuth()
  const [engineers, setEngineers] = useState([])
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedEngineer, setSelectedEngineer] = useState(null)
  const [selectedDevices, setSelectedDevices] = useState([])
  const [showAssignDialog, setShowAssignDialog] = useState(false)
  const [showRemoveDialog, setShowRemoveDialog] = useState(false)
  const [deviceToRemove, setDeviceToRemove] = useState(null)
  const [showStartDialog, setShowStartDialog] = useState(false)
  const [showStartAllDialog, setShowStartAllDialog] = useState(false)
  const [deviceToStart, setDeviceToStart] = useState(null)
  const [startingDevices, setStartingDevices] = useState(new Set())

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [engineersResponse, devicesResponse] = await Promise.all([
        api.get('/api/v1/users/engineers/with-devices'),
        api.get('/api/v1/devices/')
      ])
      
      setEngineers(engineersResponse.data)
      setDevices(devicesResponse.data)
      setError('')
    } catch (err) {
      const errorMessage = err.userMessage || 'Failed to load data'
      setError(errorMessage)
      notifications.error(errorMessage)
      console.error('Error fetching data:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAssignDevices = () => {
    if (!selectedEngineer || selectedDevices.length === 0) {
      setError('Please select an engineer and at least one device')
      return
    }
    setShowAssignDialog(true)
  }

  const confirmAssignDevices = async () => {
    try {
      await api.put(`/api/v1/users/${selectedEngineer.id}/assign-devices`, selectedDevices)
      
      // Update local state
      setEngineers(prev => prev.map(engineer => 
        engineer.id === selectedEngineer.id 
          ? { 
              ...engineer, 
              assignedDevices: [...new Set([...engineer.assignedDevices, ...selectedDevices])],
              assignedDeviceDetails: [
                ...engineer.assignedDeviceDetails,
                ...devices.filter(device => selectedDevices.includes(device.deviceId))
                  .filter(device => !engineer.assignedDevices.includes(device.deviceId))
              ]
            }
          : engineer
      ))
      
      setSelectedDevices([])
      setSelectedEngineer(null)
      setShowAssignDialog(false)
      
      notifications.success(`Successfully assigned ${selectedDevices.length} devices to ${selectedEngineer.name}`)
      setError('')
    } catch (err) {
      const errorMessage = err.userMessage || 'Failed to assign devices'
      setError(errorMessage)
      notifications.error(errorMessage)
      setShowAssignDialog(false)
    }
  }

  const handleRemoveDevice = (engineer, deviceId) => {
    setSelectedEngineer(engineer)
    setDeviceToRemove(deviceId)
    setShowRemoveDialog(true)
  }

  const confirmRemoveDevice = async () => {
    try {
      await api.put(`/api/v1/users/${selectedEngineer.id}/remove-devices`, [deviceToRemove])
      
      // Update local state
      setEngineers(prev => prev.map(engineer => 
        engineer.id === selectedEngineer.id 
          ? { 
              ...engineer, 
              assignedDevices: engineer.assignedDevices.filter(id => id !== deviceToRemove),
              assignedDeviceDetails: engineer.assignedDeviceDetails.filter(device => device.deviceId !== deviceToRemove)
            }
          : engineer
      ))
      
      setShowRemoveDialog(false)
      setDeviceToRemove(null)
      setSelectedEngineer(null)
      
      notifications.success('Device successfully removed from engineer')
      setError('')
    } catch (err) {
      const errorMessage = err.userMessage || 'Failed to remove device'
      setError(errorMessage)
      notifications.error(errorMessage)
      setShowRemoveDialog(false)
    }
  }

  const getAvailableDevices = () => {
    const assignedDeviceIds = engineers.flatMap(engineer => engineer.assignedDevices)
    return devices.filter(device => !assignedDeviceIds.includes(device.deviceId))
  }

  const getUnassignedDevicesForEngineer = (engineer) => {
    return devices.filter(device => !engineer.assignedDevices.includes(device.deviceId))
  }

  const handleStartDevice = (device) => {
    setDeviceToStart(device)
    setShowStartDialog(true)
  }

  const confirmStartDevice = async () => {
    try {
      setStartingDevices(prev => new Set([...prev, deviceToStart.deviceId]))
      setShowStartDialog(false)
      
      const response = await api.post(`/api/v1/devices/start/${deviceToStart.deviceId}`)
      
      // Update local device state
      setDevices(prev => prev.map(device => 
        device.deviceId === deviceToStart.deviceId 
          ? { ...device, status: 'on' }
          : device
      ))
      
      // Update engineers' assigned device details
      setEngineers(prev => prev.map(engineer => ({
        ...engineer,
        assignedDeviceDetails: engineer.assignedDeviceDetails.map(device => 
          device.deviceId === deviceToStart.deviceId 
            ? { ...device, status: 'on' }
            : device
        )
      })))
      
      notifications.success(response.data.message)
      setDeviceToStart(null)
      setError('')
    } catch (err) {
      const errorMessage = err.userMessage || 'Failed to start device'
      setError(errorMessage)
      notifications.error(errorMessage)
    } finally {
      setStartingDevices(prev => {
        const newSet = new Set(prev)
        newSet.delete(deviceToStart?.deviceId)
        return newSet
      })
    }
  }

  const handleStartAllDevices = () => {
    const offDevices = devices.filter(device => device.status === 'off' || device.status === 'maintenance')
    if (offDevices.length === 0) {
      notifications.info('All devices are already powered on')
      return
    }
    setShowStartAllDialog(true)
  }

  const confirmStartAllDevices = async () => {
    try {
      setShowStartAllDialog(false)
      setStartingDevices(new Set(['all']))
      
      const response = await api.post('/api/v1/devices/start-all')
      
      // Update all devices to 'on' status
      setDevices(prev => prev.map(device => 
        device.status === 'off' || device.status === 'maintenance'
          ? { ...device, status: 'on' }
          : device
      ))
      
      // Update engineers' assigned device details
      setEngineers(prev => prev.map(engineer => ({
        ...engineer,
        assignedDeviceDetails: engineer.assignedDeviceDetails.map(device => 
          device.status === 'off' || device.status === 'maintenance'
            ? { ...device, status: 'on' }
            : device
        )
      })))
      
      notifications.success(response.data.message)
      setError('')
    } catch (err) {
      const errorMessage = err.userMessage || 'Failed to start devices'
      setError(errorMessage)
      notifications.error(errorMessage)
    } finally {
      setStartingDevices(new Set())
    }
  }

  const getOffDevicesCount = () => {
    return devices.filter(device => device.status === 'off' || device.status === 'maintenance').length
  }

  if (user?.role !== 'Admin') {
    return (
      <div className="device-management">
        <div className="alert alert-error">
          Access Denied: Only administrators can manage device assignments.
        </div>
      </div>
    )
  }

  return (
    <div className="device-management">
      <h1>Device Management</h1>
      <p>Assign and manage devices for engineers</p>
      
      {error && <div className="alert alert-error">{error}</div>}
      
      {loading ? (
        <div className="loading">Loading device assignments...</div>
      ) : (
        <>
          {/* Device Assignment Section */}
          <div className="assignment-section">
            <h2>Assign New Devices</h2>
            
            <div className="assignment-form">
              <div className="form-group">
                <label htmlFor="engineer-select">Select Engineer:</label>
                <select
                  id="engineer-select"
                  value={selectedEngineer?.id || ''}
                  onChange={(e) => {
                    const engineer = engineers.find(eng => eng.id === e.target.value)
                    setSelectedEngineer(engineer || null)
                    setSelectedDevices([])
                  }}
                >
                  <option value="">Choose an engineer...</option>
                  {engineers.map(engineer => (
                    <option key={engineer.id} value={engineer.id}>
                      {engineer.name} ({engineer.assignedDevices.length} devices assigned)
                    </option>
                  ))}
                </select>
              </div>
              
              {selectedEngineer && (
                <div className="form-group">
                  <label>Available Devices for {selectedEngineer.name}:</label>
                  <div className="devices-grid">
                    {getUnassignedDevicesForEngineer(selectedEngineer).map(device => (
                      <div key={device.deviceId} className="device-option">
                        <label className="checkbox-container">
                          <input
                            type="checkbox"
                            checked={selectedDevices.includes(device.deviceId)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedDevices(prev => [...prev, device.deviceId])
                              } else {
                                setSelectedDevices(prev => prev.filter(id => id !== device.deviceId))
                              }
                            }}
                          />
                          <span className="checkmark"></span>
                          <div className="device-info">
                            <strong>{device.name}</strong>
                            <span className="device-id">ID: {device.deviceId}</span>
                            <span className="device-location">Location: {device.location}</span>
                            <span className={`device-status ${device.status}`}>Status: {device.status}</span>
                            <span className="device-assignments">Assigned to: {device.assignedUsers && device.assignedUsers.length > 0 ? device.assignedUsers.join(', ') : 'None'}</span>
                          </div>
                        </label>
                      </div>
                    ))}
                  </div>
                  
                  {getUnassignedDevicesForEngineer(selectedEngineer).length === 0 && (
                    <p className="no-devices">All devices are already assigned to this engineer.</p>
                  )}
                  
                  <button
                    onClick={handleAssignDevices}
                    disabled={selectedDevices.length === 0}
                    className="button button-primary"
                  >
                    Assign Selected Devices ({selectedDevices.length})
                  </button>
                </div>
              )}
            </div>
          </div>
          
          {/* Server Management Section */}
          <div className="server-management-section">
            <h2>Server Management</h2>
            <p>Start and control server power states</p>
            
            <div className="server-controls">
              <div className="bulk-controls">
                <button
                  onClick={handleStartAllDevices}
                  disabled={startingDevices.has('all') || getOffDevicesCount() === 0}
                  className="button button-success"
                >
                  {startingDevices.has('all') ? 'Starting All Devices...' : `Start All Devices (${getOffDevicesCount()})`}
                </button>
                <span className="control-info">
                  {getOffDevicesCount() === 0 ? 'All devices are already running' : `${getOffDevicesCount()} devices available to start`}
                </span>
              </div>
              
              <div className="device-grid">
                {devices.map(device => (
                  <div key={device.deviceId} className={`device-control-card ${device.status}`}>
                    <div className="device-header">
                      <h4>{device.name}</h4>
                      <span className={`status-badge ${device.status}`}>
                        {device.status === 'on' && '🟢 Online'}
                        {device.status === 'off' && '🔴 Offline'}
                        {device.status === 'maintenance' && '🟡 Maintenance'}
                      </span>
                    </div>
                    
                    <div className="device-details">
                      <p><strong>ID:</strong> {device.deviceId}</p>
                      <p><strong>Location:</strong> {device.location || 'Not specified'}</p>
                      <p><strong>Assigned Users:</strong> {device.assignedUsers && device.assignedUsers.length > 0 ? device.assignedUsers.join(', ') : 'Unassigned'}</p>
                      {device.lastStartup && (
                        <p><strong>Last Started:</strong> {new Date(device.lastStartup).toLocaleString()}</p>
                      )}
                      {device.lastShutdown && (
                        <p><strong>Last Shutdown:</strong> {new Date(device.lastShutdown).toLocaleString()}</p>
                      )}
                    </div>
                    
                    <div className="device-actions">
                      <button
                        onClick={() => handleStartDevice(device)}
                        disabled={device.status === 'on' || startingDevices.has(device.deviceId)}
                        className={`button ${device.status === 'on' ? 'button-disabled' : 'button-primary'}`}
                      >
                        {startingDevices.has(device.deviceId) ? 'Starting...' : 
                         device.status === 'on' ? 'Already Running' : 'Start Device'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
          
          {/* Current Assignments Section */}
          <div className="assignments-list">
            <h2>Current Device Assignments</h2>
            
            {engineers.length === 0 ? (
              <div className="no-data">No engineers found</div>
            ) : (
              <div className="engineers-grid">
                {engineers.map(engineer => (
                  <div key={engineer.id} className="engineer-card">
                    <div className="engineer-header">
                      <h3>{engineer.name}</h3>
                      <span className="engineer-role">{engineer.role}</span>
                      <span className="device-count">{engineer.assignedDevices.length} devices</span>
                    </div>
                    
                    <div className="assigned-devices">
                      {engineer.assignedDeviceDetails.length === 0 ? (
                        <p className="no-assignments">No devices assigned</p>
                      ) : (
                        engineer.assignedDeviceDetails.map(device => (
                          <div key={device.deviceId} className="assigned-device">
                            <div className="device-details">
                              <strong>{device.name}</strong>
                              <span className="device-id">ID: {device.deviceId}</span>
                              <span className="device-location">Location: {device.location}</span>
                              <span className={`device-status ${device.status}`}>Status: {device.status}</span>
                            </div>
                            <button
                              onClick={() => handleRemoveDevice(engineer, device.deviceId)}
                              className="button button-danger button-small"
                            >
                              Remove
                            </button>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Unassigned Devices Section */}
          <div className="unassigned-devices">
            <h2>Unassigned Devices</h2>
            <div className="devices-grid">
              {getAvailableDevices().map(device => (
                <div key={device.deviceId} className="device-card unassigned">
                  <h4>{device.name}</h4>
                  <p>ID: {device.deviceId}</p>
                  <p>Location: {device.location}</p>
                  <p>Assigned to: {device.assignedUsers && device.assignedUsers.length > 0 ? device.assignedUsers.join(', ') : 'None'}</p>
                  <span className={`device-status ${device.status}`}>Status: {device.status}</span>
                </div>
              ))}
            </div>
            
            {getAvailableDevices().length === 0 && (
              <p className="no-data">All devices are currently assigned to engineers.</p>
            )}
          </div>
        </>
      )}
      
      {/* Assignment Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showAssignDialog}
        title="Assign Devices"
        message={`Are you sure you want to assign ${selectedDevices.length} device(s) to ${selectedEngineer?.name}?`}
        onConfirm={confirmAssignDevices}
        onCancel={() => setShowAssignDialog(false)}
        type="info"
      />
      
      {/* Remove Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showRemoveDialog}
        title="Remove Device Assignment"
        message={`Are you sure you want to remove device ${deviceToRemove} from ${selectedEngineer?.name}?`}
        onConfirm={confirmRemoveDevice}
        onCancel={() => setShowRemoveDialog(false)}
        type="warning"
      />
      
      {/* Start Device Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showStartDialog}
        title="Start Device"
        message={`Are you sure you want to start device ${deviceToStart?.name} (${deviceToStart?.deviceId})? This will power on the device.`}
        onConfirm={confirmStartDevice}
        onCancel={() => setShowStartDialog(false)}
        type="info"
      />
      
      {/* Start All Devices Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={showStartAllDialog}
        title="Start All Devices"
        message={`Are you sure you want to start all ${getOffDevicesCount()} offline devices? This will power on all devices that are currently off or in maintenance.`}
        onConfirm={confirmStartAllDevices}
        onCancel={() => setShowStartAllDialog(false)}
        type="info"
      />
    </div>
  )
}

export default DeviceManagement