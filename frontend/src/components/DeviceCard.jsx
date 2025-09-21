import { memo } from 'react'

// Memoized Device Card component for better performance
const DeviceCard = memo(({ device, onShutdown, loading, getDeviceStatusColor }) => {
  return (
    <div key={device.id} className={`device-card ${device.status}`}>
      <div className="device-header">
        <h4>{device.name}</h4>
        <span className={`status-indicator ${getDeviceStatusColor(device.status)}`}></span>
      </div>
      <div className="device-info">
        <p>ID: {device.deviceId}</p>
        <p>Status: {device.status}</p>
        {device.location && <p>Location: {device.location}</p>}
        {device.lastShutdown && (
          <p>Last Shutdown: {new Date(device.lastShutdown).toLocaleString()}</p>
        )}
      </div>
      {onShutdown && (
        <button
          onClick={() => onShutdown(device.deviceId)}
          disabled={loading || device.status === 'off'}
          className={`shutdown-button ${device.status === 'off' ? 'disabled' : ''}`}
        >
          {loading ? 'Shutting down...' : 'Shutdown'}
        </button>
      )}
    </div>
  )
})

DeviceCard.displayName = 'DeviceCard'

export default DeviceCard