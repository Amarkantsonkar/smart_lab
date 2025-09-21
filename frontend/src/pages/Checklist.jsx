import { useState, useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'
import api from '../services/api'
import notifications from '../services/notifications'
import ChecklistFilter from '../components/ChecklistFilter'
import ChecklistStats from '../components/ChecklistStats'
import ConfirmationDialog from '../components/ConfirmationDialog'

const Checklist = () => {
  const { user } = useAuth()
  const [checklistItems, setChecklistItems] = useState([])
  const [filteredItems, setFilteredItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCompleteDialog, setShowCompleteDialog] = useState(false)
  const [filters, setFilters] = useState({ category: '', status: '', criticality: '' })

  useEffect(() => {
    fetchChecklistItems()
    
    // Listen for checklist updates from other components
    const handleChecklistUpdated = () => {
      fetchChecklistItems()
    }
    
    window.addEventListener('checklist-updated', handleChecklistUpdated)
    
    return () => {
      window.removeEventListener('checklist-updated', handleChecklistUpdated)
    }
  }, [])

  const fetchChecklistItems = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/v1/checklist/')
      setChecklistItems(response.data)
      setFilteredItems(response.data)
      setError('')
    } catch (err) {
      setError('Failed to load checklist items')
      console.error('Error fetching checklist:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (filters) => {
    let filtered = checklistItems
    
    // Apply category filter
    if (filters.category) {
      filtered = filtered.filter(item => item.category === filters.category)
    }
    
    // Apply status filter
    if (filters.status === 'completed') {
      filtered = filtered.filter(item => item.completed)
    } else if (filters.status === 'pending') {
      filtered = filtered.filter(item => !item.completed)
    }
    
    // Apply criticality filter
    if (filters.criticality === 'critical') {
      filtered = filtered.filter(item => item.isCritical)
    } else if (filters.criticality === 'non-critical') {
      filtered = filtered.filter(item => !item.isCritical)
    }
    
    setFilteredItems(filtered)
  }

  const handleToggleComplete = async (item) => {
    try {
      setError('') // Clear any previous errors
      
      const updatedItem = { ...item, completed: !item.completed }
      await api.put(`/api/v1/checklist/${item.taskId}`, {
        completed: !item.completed
      })
      
      // Update local state
      const updatedItems = checklistItems.map(i => 
        i.id === item.id ? { ...i, completed: !i.completed } : i
      )
      
      setChecklistItems(updatedItems)
      
      // Re-apply current filters
      handleFilterChange(filters)
      
      // Refresh the validation result in shutdown control
      window.dispatchEvent(new CustomEvent('checklist-updated'))
      
      // Show success notification
      notifications.success(`${!item.completed ? 'Completed' : 'Unchecked'}: ${item.description}`, 3000)
      
    } catch (err) {
      const errorMessage = err.userMessage || 'Failed to update checklist item'
      setError(errorMessage)
      notifications.error(errorMessage)
      console.error('Error updating checklist:', err)
    }
  }

  const getCriticalityColor = (isCritical) => {
    return isCritical ? 'text-red-600 font-bold' : 'text-gray-600'
  }

  const getCategoryBadge = (category) => {
    const colors = {
      safety: 'bg-red-100 text-red-800',
      security: 'bg-blue-100 text-blue-800',
      backup: 'bg-green-100 text-green-800',
      network: 'bg-purple-100 text-purple-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  const handleCompleteAll = () => {
    // Check if all critical tasks are completed
    const criticalTasks = checklistItems.filter(item => item.isCritical)
    const incompleteCriticalTasks = criticalTasks.filter(item => !item.completed)
    
    if (incompleteCriticalTasks.length > 0) {
      setError('Cannot complete checklist: All critical tasks must be completed first')
      return
    }
    
    // Show confirmation dialog if there are pending non-critical tasks
    const pendingNonCriticalTasks = checklistItems.filter(item => !item.isCritical && !item.completed)
    if (pendingNonCriticalTasks.length > 0) {
      setShowCompleteDialog(true)
    } else {
      // All tasks are already completed
      setError('All tasks are already completed')
    }
  }

  const confirmCompleteAll = async () => {
    try {
      // Mark all remaining non-critical tasks as completed
      const pendingNonCriticalTasks = checklistItems.filter(item => !item.isCritical && !item.completed)
      
      for (const task of pendingNonCriticalTasks) {
        await api.put(`/api/v1/checklist/${task.taskId}`, {
          completed: true
        })
      }
      
      // Update local state
      const updatedItems = checklistItems.map(item => 
        !item.isCritical && !item.completed ? { ...item, completed: true } : item
      )
      
      setChecklistItems(updatedItems)
      setFilteredItems(updatedItems)
      setShowCompleteDialog(false)
      
      // Refresh the validation result in shutdown control
      window.dispatchEvent(new CustomEvent('checklist-updated'))
      
      // Show success message
      notifications.success('All non-critical tasks completed successfully!', 5000)
      setError('')
    } catch (err) {
      setError('Failed to complete checklist items')
      console.error('Error completing checklist:', err)
      setShowCompleteDialog(false)
    }
  }

  const cancelCompleteAll = () => {
    setShowCompleteDialog(false)
  }

  return (
    <div className="checklist">
      <h1>Maintenance Checklist</h1>
      
      {error && <div className="alert alert-error">{error}</div>}
      
      <ChecklistStats items={checklistItems} />
      
      <ChecklistFilter onFilterChange={handleFilterChange} />
      
      <div className="checklist-actions">
        <button onClick={handleCompleteAll} className="button button-primary">
          Complete All Non-Critical Tasks
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading checklist...</div>
      ) : (
        <div className="checklist-items">
          {filteredItems.length === 0 ? (
            <div className="no-data">No checklist items match the current filters</div>
          ) : (
            filteredItems.map(item => (
              <div key={item.taskId} className={`checklist-item ${item.completed ? 'completed' : ''}${item.isCritical ? ' critical' : ''}`}> // Add critical class for styling
                <div className="checklist-item-header">
                  <h3 className={getCriticalityColor(item.isCritical)}>
                    {item.isCritical ? '⚠️ ' : 'ℹ️ '}{item.description}
                  </h3>
                  <span className={`badge ${getCategoryBadge(item.category)}`}>
                    {item.category}
                  </span>
                </div>
                <div className="checklist-item-actions">
                  <label className="checkbox-container">
                    <input
                      type="checkbox"
                      checked={item.completed}
                      onChange={() => handleToggleComplete(item)}
                    />
                    <span className="checkmark"></span>
                    {item.completed ? 'Completed' : 'Mark as Complete'}
                  </label>
                  {item.completedBy && (
                    <small className="completed-by">
                      Completed by {item.completedBy} on {new Date(item.completedAt).toLocaleString()}
                    </small>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
      
      <ConfirmationDialog
        isOpen={showCompleteDialog}
        title="Complete All Non-Critical Tasks?"
        message="There are still some non-critical tasks pending. Would you like to mark all remaining non-critical tasks as completed?"
        onConfirm={confirmCompleteAll}
        onCancel={cancelCompleteAll}
      />
    </div>
  )
}

export default Checklist