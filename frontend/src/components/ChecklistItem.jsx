import { memo } from 'react'

// Memoized Checklist Item component
const ChecklistItem = memo(({ item, onToggle, loading }) => {
  const handleToggle = () => {
    if (!loading) {
      onToggle(item.taskId, !item.completed)
    }
  }

  return (
    <div className={`checklist-item ${item.completed ? 'completed' : ''} ${item.isCritical ? 'critical' : ''}`}>
      <div className="checklist-item-header">
        <h3 style={{ color: item.isCritical ? '#dc2626' : 'inherit' }}>
          {item.description}
        </h3>
        <div className="item-badges">
          {item.isCritical && (
            <span className="badge critical">Critical</span>
          )}
          <span className={`badge ${item.category?.toLowerCase() || 'general'}`}>
            {item.category || 'General'}
          </span>
        </div>
      </div>
      
      <label className="checkbox-container">
        <input
          type="checkbox"
          checked={item.completed}
          onChange={handleToggle}
          disabled={loading}
        />
        <span className="checkmark"></span>
        <span className="task-label">
          {item.completed ? 'Completed' : 'Pending'}
        </span>
      </label>
      
      {item.completed && item.completedBy && (
        <span className="completed-by">
          Completed by {item.completedBy} on{' '}
          {new Date(item.completedAt).toLocaleString()}
        </span>
      )}
    </div>
  )
})

ChecklistItem.displayName = 'ChecklistItem'

export default ChecklistItem