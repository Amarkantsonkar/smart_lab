import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import api from '../services/api'

const Reports = () => {
  const { user } = useAuth()
  const [logs, setLogs] = useState([])
  const [devices, setDevices] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [itemsPerPage] = useState(10)
  const [filters, setFilters] = useState({
    deviceId: '',
    userId: '',
    status: '',
    startDate: '',
    endDate: '',
    sortBy: 'timestamp',
    sortOrder: 'desc'
  })

  useEffect(() => {
    fetchInitialData()
  }, [])

  useEffect(() => {
    fetchLogs()
  }, [currentPage, filters])

  const fetchInitialData = async () => {
    try {
      const [devicesResponse] = await Promise.all([
        api.get('/api/v1/devices/')
      ])
      
      setDevices(devicesResponse.data)
      // Note: User management API not available, using static user data
      setUsers([
        { id: 'admin', name: 'Administrator', role: 'Admin' },
        { id: 'engineer', name: 'Engineer User', role: 'Engineer' }
      ])
    } catch (err) {
      console.error('Error fetching initial data:', err)
    }
  }

  const fetchLogs = async () => {
    try {
      setLoading(true)
      const params = {
        page: currentPage,
        limit: itemsPerPage,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder
      }
      
      // Add filters if they have values
      if (filters.deviceId) params.device_id = filters.deviceId
      if (filters.userId) params.user_id = filters.userId
      if (filters.status) params.status = filters.status
      if (filters.startDate) params.start_date = filters.startDate
      if (filters.endDate) params.end_date = filters.endDate
      
      const response = await api.get('/api/v1/shutdown-logs/', { params })
      
      setLogs(response.data.items || response.data)
      setTotalPages(response.data.total_pages || 1)
      setError('')
    } catch (err) {
      setError('Failed to load shutdown logs')
      console.error('Error fetching logs:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters(prev => ({ ...prev, [name]: value }))
    setCurrentPage(1) // Reset to first page when filters change
  }

  const handleSort = (column) => {
    setFilters(prev => ({
      ...prev,
      sortBy: column,
      sortOrder: prev.sortBy === column && prev.sortOrder === 'desc' ? 'asc' : 'desc'
    }))
    setCurrentPage(1)
  }

  const handlePageChange = (page) => {
    setCurrentPage(page)
  }

  const handleSearch = () => {
    setCurrentPage(1)
    fetchLogs()
  }

  const handleReset = () => {
    setFilters({
      deviceId: '',
      userId: '',
      status: '',
      startDate: '',
      endDate: '',
      sortBy: 'timestamp',
      sortOrder: 'desc'
    })
    setCurrentPage(1)
  }

  const handleExportCSV = async () => {
    try {
      // Fetch all logs for export (without pagination)
      const params = {
        export: true,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder
      }
      
      if (filters.deviceId) params.device_id = filters.deviceId
      if (filters.userId) params.user_id = filters.userId
      if (filters.status) params.status = filters.status
      if (filters.startDate) params.start_date = filters.startDate
      if (filters.endDate) params.end_date = filters.endDate
      
      const response = await api.get('/api/v1/shutdown-logs/', { params })
      const allLogs = response.data.items || response.data
      
      // Create CSV content
      const headers = ['Device ID', 'Device Name', 'User', 'Status', 'Timestamp', 'Duration (s)', 'Reason', 'Error Message']
      const csvContent = [
        headers.join(','),
        ...allLogs.map(log => [
          log.deviceId || '',
          log.deviceName || '',
          log.userName || '',
          log.status || '',
          new Date(log.timestamp).toLocaleString(),
          log.duration || 0,
          log.reason || '',
          log.errorMessage || ''
        ].map(field => `"${String(field).replace(/"/g, '""')}"`).join(','))
      ].join('\n')
      
      // Create download link
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `shutdown-logs-${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError('Failed to export CSV')
      console.error('Error exporting CSV:', err)
    }
  }

  const handleExportJSON = async () => {
    try {
      const params = {
        export: true,
        sort_by: filters.sortBy,
        sort_order: filters.sortOrder
      }
      
      if (filters.deviceId) params.device_id = filters.deviceId
      if (filters.userId) params.user_id = filters.userId
      if (filters.status) params.status = filters.status
      if (filters.startDate) params.start_date = filters.startDate
      if (filters.endDate) params.end_date = filters.endDate
      
      const response = await api.get('/api/v1/shutdown-logs/', { params })
      const allLogs = response.data.items || response.data
      
      const jsonContent = JSON.stringify({
        exportDate: new Date().toISOString(),
        filters: filters,
        totalRecords: allLogs.length,
        logs: allLogs
      }, null, 2)
      
      const blob = new Blob([jsonContent], { type: 'application/json' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `shutdown-logs-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError('Failed to export JSON')
      console.error('Error exporting JSON:', err)
    }
  }

  const successCount = logs.filter(log => log.status === 'success').length
  const failureCount = logs.filter(log => log.status === 'failed').length
  const avgDuration = logs.length > 0 ? 
    Math.round(logs.reduce((sum, log) => sum + (log.duration || 0), 0) / logs.length) : 0

  // Device-specific analytics
  const deviceShutdownCounts = devices.reduce((acc, device) => {
    const deviceLogs = logs.filter(log => log.device === device.deviceId)
    acc[device.deviceId] = {
      name: device.name,
      total: deviceLogs.length,
      successful: deviceLogs.filter(log => log.status === 'success').length,
      failed: deviceLogs.filter(log => log.status === 'failed').length,
      lastShutdown: device.lastShutdown
    }
    return acc
  }, {})

  const mostShutdownDevice = Object.entries(deviceShutdownCounts)
    .sort((a, b) => b[1].total - a[1].total)[0]

  const deviceReliability = Object.entries(deviceShutdownCounts)
    .map(([deviceId, stats]) => ({
      deviceId,
      name: stats.name,
      reliability: stats.total > 0 ? Math.round((stats.successful / stats.total) * 100) : 100
    }))
    .sort((a, b) => a.reliability - b.reliability)

  const getSortIcon = (column) => {
    if (filters.sortBy !== column) return '↕️'
    return filters.sortOrder === 'desc' ? '↓' : '↑'
  }

  const renderPagination = () => {
    const pages = []
    const maxPagesToShow = 5
    let startPage = Math.max(1, currentPage - Math.floor(maxPagesToShow / 2))
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1)
    
    if (endPage - startPage + 1 < maxPagesToShow) {
      startPage = Math.max(1, endPage - maxPagesToShow + 1)
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => handlePageChange(i)}
          className={`pagination-button ${currentPage === i ? 'active' : ''}`}
        >
          {i}
        </button>
      )
    }
    
    return (
      <div className="pagination">
        <button
          onClick={() => handlePageChange(1)}
          disabled={currentPage === 1}
          className="pagination-button"
        >
          First
        </button>
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="pagination-button"
        >
          Previous
        </button>
        {pages}
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="pagination-button"
        >
          Next
        </button>
        <button
          onClick={() => handlePageChange(totalPages)}
          disabled={currentPage === totalPages}
          className="pagination-button"
        >
          Last
        </button>
      </div>
    )
  }

  return (
    <div className="reports">
      <div className="reports-header">
        <h1>Shutdown Reports & Analytics</h1>
        <div className="export-buttons">
          <button onClick={handleExportCSV} className="button button-export">
            📄 Export CSV
          </button>
          <button onClick={handleExportJSON} className="button button-export">
            📁 Export JSON
          </button>
        </div>
      </div>
      
      {error && <div className="alert alert-error">{error}</div>}
      
      {/* Advanced Filters */}
      <div className="filters-section">
        <h3>Filters & Search</h3>
        <div className="filters-grid">
          <div className="filter-group">
            <label htmlFor="deviceId">Device:</label>
            <select
              id="deviceId"
              name="deviceId"
              value={filters.deviceId}
              onChange={handleFilterChange}
            >
              <option value="">All Devices</option>
              {devices.map(device => (
                <option key={device.deviceId} value={device.deviceId}>
                  {device.name} ({device.deviceId})
                </option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label htmlFor="userId">User:</label>
            <select
              id="userId"
              name="userId"
              value={filters.userId}
              onChange={handleFilterChange}
            >
              <option value="">All Users</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name} ({user.role})
                </option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label htmlFor="status">Status:</label>
            <select
              id="status"
              name="status"
              value={filters.status}
              onChange={handleFilterChange}
            >
              <option value="">All Statuses</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label htmlFor="startDate">Start Date:</label>
            <input
              type="datetime-local"
              id="startDate"
              name="startDate"
              value={filters.startDate}
              onChange={handleFilterChange}
            />
          </div>
          
          <div className="filter-group">
            <label htmlFor="endDate">End Date:</label>
            <input
              type="datetime-local"
              id="endDate"
              name="endDate"
              value={filters.endDate}
              onChange={handleFilterChange}
            />
          </div>
          
          <div className="filter-actions">
            <button onClick={handleSearch} className="button button-primary">
              🔍 Search
            </button>
            <button onClick={handleReset} className="button button-secondary">
              🔄 Reset
            </button>
          </div>
        </div>
      </div>
      
      {/* Summary Statistics */}
      <div className="reports-summary">
        <div className="summary-card">
          <h3>Total Shutdowns</h3>
          <p className="summary-value">{logs.length}</p>
        </div>
        <div className="summary-card success">
          <h3>Successful</h3>
          <p className="summary-value">{successCount}</p>
        </div>
        <div className="summary-card error">
          <h3>Failed</h3>
          <p className="summary-value">{failureCount}</p>
        </div>
        <div className="summary-card">
          <h3>Success Rate</h3>
          <p className="summary-value">{logs.length > 0 ? Math.round((successCount / logs.length) * 100) : 0}%</p>
        </div>
        <div className="summary-card">
          <h3>Avg Duration</h3>
          <p className="summary-value">{avgDuration}s</p>
        </div>
      </div>
                
      {/* Device Analytics */}
      <div className="device-analytics">
        <h3>Device Performance Analytics</h3>
                  
        <div className="analytics-grid">
          <div className="analytics-card">
            <h4>Most Active Device</h4>
            {mostShutdownDevice ? (
              <div className="analytics-content">
                <p className="device-name">{mostShutdownDevice[1].name}</p>
                <p className="device-stats">{mostShutdownDevice[1].total} shutdowns</p>
                <p className="device-success-rate">
                  {mostShutdownDevice[1].total > 0 
                    ? Math.round((mostShutdownDevice[1].successful / mostShutdownDevice[1].total) * 100)
                    : 0}% success rate
                </p>
              </div>
            ) : (
              <p className="no-data">No shutdown data available</p>
            )}
          </div>
                    
          <div className="analytics-card">
            <h4>Device Reliability</h4>
            <div className="reliability-list">
              {deviceReliability.slice(0, 3).map(device => (
                <div key={device.deviceId} className="reliability-item">
                  <span className="device-name">{device.name}</span>
                  <span className={`reliability-score ${device.reliability < 80 ? 'low' : device.reliability < 95 ? 'medium' : 'high'}`}>
                    {device.reliability}%
                  </span>
                </div>
              ))}
              {deviceReliability.length === 0 && (
                <p className="no-data">No reliability data available</p>
              )}
            </div>
          </div>
                    
          <div className="analytics-card">
            <h4>Device Status Overview</h4>
            <div className="status-overview">
              <div className="status-item">
                <span className="status-label">Online:</span>
                <span className="status-count">{devices.filter(d => d.status === 'on').length}</span>
              </div>
              <div className="status-item">
                <span className="status-label">Offline:</span>
                <span className="status-count">{devices.filter(d => d.status === 'off').length}</span>
              </div>
              <div className="status-item">
                <span className="status-label">Maintenance:</span>
                <span className="status-count">{devices.filter(d => d.status === 'maintenance').length}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {loading ? (
        <div className="loading">Loading reports...</div>
      ) : (
        <>
          {/* Data Table */}
          <div className="table-section">
            <div className="table-header">
              <h3>Shutdown Logs</h3>
              <span className="table-info">
                Showing {((currentPage - 1) * itemsPerPage) + 1}-{Math.min(currentPage * itemsPerPage, logs.length)} of {logs.length} entries
              </span>
            </div>
            
            <div className="logs-table-container">
              <table className="logs-table">
                <thead>
                  <tr>
                    <th onClick={() => handleSort('deviceId')} className="sortable">
                      Device {getSortIcon('deviceId')}
                    </th>
                    <th onClick={() => handleSort('userName')} className="sortable">
                      User {getSortIcon('userName')}
                    </th>
                    <th onClick={() => handleSort('status')} className="sortable">
                      Status {getSortIcon('status')}
                    </th>
                    <th onClick={() => handleSort('timestamp')} className="sortable">
                      Timestamp {getSortIcon('timestamp')}
                    </th>
                    <th onClick={() => handleSort('duration')} className="sortable">
                      Duration {getSortIcon('duration')}
                    </th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="no-data">No shutdown logs found</td>
                    </tr>
                  ) : (
                    logs.map((log, index) => (
                      <tr key={log.id || log._id || log.logId || `log-${index}-${log.timestamp}`} className={log.status === 'failed' ? 'failed-row' : 'success-row'}>
                        <td>
                          <div className="device-info">
                            <strong>{log.deviceName || log.deviceId}</strong>
                            <br />
                            <small>{log.deviceId}</small>
                          </div>
                        </td>
                        <td>{log.userName}</td>
                        <td>
                          <span className={`status-badge ${log.status === 'success' ? 'success' : 'error'}`}>
                            {log.status === 'success' ? '✅' : '❌'} {log.status}
                          </span>
                        </td>
                        <td>
                          <div className="timestamp">
                            {new Date(log.timestamp).toLocaleDateString()}
                            <br />
                            <small>{new Date(log.timestamp).toLocaleTimeString()}</small>
                          </div>
                        </td>
                        <td>{log.duration || 0}s</td>
                        <td>
                          <div className="log-details">
                            {log.reason && (
                              <div className="detail-item">
                                <strong>Reason:</strong> {log.reason}
                              </div>
                            )}
                            {log.errorMessage && (
                              <div className="detail-item error">
                                <strong>Error:</strong> {log.errorMessage}
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            
            {/* Pagination */}
            {totalPages > 1 && renderPagination()}
          </div>
        </>
      )}
    </div>
  )
}

export default Reports