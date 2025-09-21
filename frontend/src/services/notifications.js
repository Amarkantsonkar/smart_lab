// Toast notification service
class NotificationService {
  constructor() {
    this.container = null
    this.init()
  }

  init() {
    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
      this.container = document.createElement('div')
      this.container.id = 'notification-container'
      this.container.className = 'notification-container'
      document.body.appendChild(this.container)
    } else {
      this.container = document.getElementById('notification-container')
    }
  }

  show(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div')
    notification.className = `notification notification-${type}`
    
    const icon = this.getIcon(type)
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-icon">${icon}</span>
        <span class="notification-message">${message}</span>
        <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
      </div>
    `

    this.container.appendChild(notification)

    // Auto remove after duration
    if (duration > 0) {
      setTimeout(() => {
        if (notification.parentElement) {
          notification.remove()
        }
      }, duration)
    }

    // Add entrance animation
    requestAnimationFrame(() => {
      notification.classList.add('notification-show')
    })

    return notification
  }

  getIcon(type) {
    switch (type) {
      case 'success':
        return '✅'
      case 'error':
        return '❌'
      case 'warning':
        return '⚠️'
      case 'info':
      default:
        return 'ℹ️'
    }
  }

  success(message, duration) {
    return this.show(message, 'success', duration)
  }

  error(message, duration) {
    return this.show(message, 'error', duration)
  }

  warning(message, duration) {
    return this.show(message, 'warning', duration)
  }

  info(message, duration) {
    return this.show(message, 'info', duration)
  }

  clear() {
    if (this.container) {
      this.container.innerHTML = ''
    }
  }
}

// Create singleton instance
const notifications = new NotificationService()

export default notifications