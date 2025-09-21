const ConfirmationDialog = ({ 
  isOpen, 
  onConfirm, 
  onCancel, 
  title, 
  message, 
  confirmText = 'Confirm', 
  cancelText = 'Cancel',
  type = 'warning'
}) => {
  if (!isOpen) return null

  const getTypeIcon = () => {
    switch (type) {
      case 'danger': return '🔴'
      case 'warning': return '⚠️'
      case 'info': return 'ℹ️'
      case 'success': return '✅'
      default: return '❓'
    }
  }

  const getTypeClass = () => {
    switch (type) {
      case 'danger': return 'dialog-danger'
      case 'warning': return 'dialog-warning' 
      case 'info': return 'dialog-info'
      case 'success': return 'dialog-success'
      default: return 'dialog-default'
    }
  }

  return (
    <div className="modal-overlay">
      <div className={`modal ${getTypeClass()}`}>
        <div className="modal-header">
          <h3>
            <span className="dialog-icon">{getTypeIcon()}</span>
            {title}
          </h3>
        </div>
        
        <div className="modal-body">
          <p>{message}</p>
        </div>
        
        <div className="modal-footer">
          <button 
            onClick={onCancel}
            className="button button-secondary"
          >
            {cancelText}
          </button>
          <button 
            onClick={onConfirm}
            className={`button ${type === 'danger' ? 'button-danger' : 'button-primary'}`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}

export default ConfirmationDialog