// Simple API cache implementation for performance optimization
class ApiCache {
  constructor() {
    this.cache = new Map()
    this.cacheTimeout = 5 * 60 * 1000 // 5 minutes default
  }

  generateKey(url, params = {}) {
    const paramString = Object.keys(params)
      .sort()
      .map(key => `${key}=${params[key]}`)
      .join('&')
    return `${url}${paramString ? `?${paramString}` : ''}`
  }

  set(url, params, data, timeout = this.cacheTimeout) {
    const key = this.generateKey(url, params)
    const expiresAt = Date.now() + timeout
    
    this.cache.set(key, {
      data,
      expiresAt,
      timestamp: Date.now()
    })
    
    // Clean up expired entries periodically
    this.cleanup()
  }

  get(url, params = {}) {
    const key = this.generateKey(url, params)
    const cached = this.cache.get(key)
    
    if (!cached) {
      return null
    }
    
    // Check if cache is expired
    if (Date.now() > cached.expiresAt) {
      this.cache.delete(key)
      return null
    }
    
    return cached.data
  }

  invalidate(url, params = {}) {
    const key = this.generateKey(url, params)
    this.cache.delete(key)
  }

  invalidatePattern(pattern) {
    const regex = new RegExp(pattern)
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key)
      }
    }
  }

  clear() {
    this.cache.clear()
  }

  cleanup() {
    const now = Date.now()
    for (const [key, value] of this.cache.entries()) {
      if (now > value.expiresAt) {
        this.cache.delete(key)
      }
    }
  }

  // Get cache statistics for debugging
  getStats() {
    return {
      size: this.cache.size,
      entries: Array.from(this.cache.keys())
    }
  }
}

// Create a singleton instance
const apiCache = new ApiCache()

export default apiCache