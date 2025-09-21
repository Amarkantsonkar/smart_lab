const ChecklistStats = ({ items }) => {
  if (!items || items.length === 0) {
    return (
      <div className="checklist-stats">
        <h3>Checklist Statistics</h3>
        <p className="no-data">No checklist items available</p>
      </div>
    )
  }

  const totalItems = items.length
  const completedItems = items.filter(item => item.completed).length
  const criticalItems = items.filter(item => item.isCritical)
  const criticalCompleted = criticalItems.filter(item => item.completed).length
  const nonCriticalItems = items.filter(item => !item.isCritical)
  const nonCriticalCompleted = nonCriticalItems.filter(item => item.completed).length

  const overallProgress = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0
  const criticalProgress = criticalItems.length > 0 ? Math.round((criticalCompleted / criticalItems.length) * 100) : 0

  const isReadyForShutdown = criticalItems.length > 0 && criticalCompleted === criticalItems.length

  return (
    <div className="checklist-stats">
      <h3>Checklist Statistics</h3>
      
      <div className="stats-grid">
        <div className={`stat-card ${overallProgress === 100 ? 'success' : 'warning'}`}>
          <h4>Overall Progress</h4>
          <div className="stat-number">{overallProgress}%</div>
          <div className="stat-detail">{completedItems}/{totalItems} tasks</div>
        </div>

        <div className={`stat-card ${criticalProgress === 100 ? 'success' : 'warning'}`}>
          <h4>Critical Tasks</h4>
          <div className="stat-number">{criticalProgress}%</div>
          <div className="stat-detail">{criticalCompleted}/{criticalItems.length} critical</div>
        </div>

        <div className={`stat-card ${nonCriticalCompleted === nonCriticalItems.length ? 'success' : 'warning'}`}>
          <h4>Non-Critical Tasks</h4>
          <div className="stat-number">{nonCriticalItems.length > 0 ? Math.round((nonCriticalCompleted / nonCriticalItems.length) * 100) : 0}%</div>
          <div className="stat-detail">{nonCriticalCompleted}/{nonCriticalItems.length} non-critical</div>
        </div>

        <div className={`stat-card ${isReadyForShutdown ? 'success' : 'warning'}`}>
          <h4>Shutdown Ready</h4>
          <div className="stat-number">{isReadyForShutdown ? 'YES' : 'NO'}</div>
          <div className="stat-detail">{isReadyForShutdown ? 'All critical tasks done' : 'Critical tasks pending'}</div>
        </div>
      </div>

      <div className="critical-stats">
        <h4>Critical Task Progress</h4>
        <div className="progress-bar-container">
          <div 
            className="progress-bar" 
            style={{ width: `${criticalProgress}%` }}
          ></div>
        </div>
        {criticalProgress < 100 && (
          <p className="warning-text">
            ⚠️ All critical tasks must be completed before shutdown
          </p>
        )}
      </div>
    </div>
  )
}

export default ChecklistStats