import axios from 'axios'
import apiCache from './cache'

// Cache configuration for different endpoints
const CACHE_CONFIG = {
  '/api/v1/devices': { timeout: 2 * 60 * 1000, cacheable: ['GET'] }, // 2 minutes
  '/api/v1/checklist': { timeout: 30 * 1000, cacheable: ['GET'] }, // 30 seconds
  '/api/v1/shutdown-logs': { timeout: 1 * 60 * 1000, cacheable: ['GET'] }, // 1 minute
  '/api/v1/users': { timeout: 5 * 60 * 1000, cacheable: ['GET'] }, // 5 minutes
}

// Helper function to check if request should be cached
const shouldCache = (config) => {
  const method = config.method?.toUpperCase()
  const url = config.url
  
  for (const [pattern, cacheConfig] of Object.entries(CACHE_CONFIG)) {
    if (url.includes(pattern) && cacheConfig.cacheable.includes(method)) {
      return cacheConfig
    }
  }
  return null
}

// Helper function to invalidate related cache entries
const invalidateCache = (config) => {
  const method = config.method?.toUpperCase()
  const url = config.url
  
  // Invalidate cache on write operations
  if (['POST', 'PUT', 'DELETE'].includes(method)) {
    if (url.includes('/api/v1/devices')) {
      apiCache.invalidatePattern('/api/v1/devices')
    }
    if (url.includes('/api/v1/checklist')) {
      apiCache.invalidatePattern('/api/v1/checklist')
    }
    if (url.includes('/api/v1/shutdown')) {
      apiCache.invalidatePattern('/api/v1/shutdown-logs')
      apiCache.invalidatePattern('/api/v1/devices') // Device status might change
    }
    if (url.includes('/api/v1/users')) {
      apiCache.invalidatePattern('/api/v1/users')
    }
  }
}
// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // Increased timeout for file exports
  headers: {
    'Content-Type': 'application/json',
  },
  // Follow redirects automatically
  maxRedirects: 5,
  validateStatus: function (status) {
    return status >= 200 && status < 300; // default
  },
})

// Request interceptor to add auth token and check cache
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Check cache for GET requests
    const cacheConfig = shouldCache(config)
    if (cacheConfig && config.method?.toUpperCase() === 'GET') {
      const cachedData = apiCache.get(config.url, config.params)
      if (cachedData) {
        // Return cached data by canceling the request
        config.cancelToken = axios.CancelToken.source().token
        config.cachedResponse = cachedData
        
        if (import.meta.env.DEV) {
          console.log(`Cache HIT: ${config.method?.toUpperCase()} ${config.url}`, cachedData)
        }
      }
    }
    
    // Log outgoing requests in development
    if (import.meta.env.DEV && !config.cachedResponse) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data
      })
    }
    
    return config
  },
  (error) => {
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors and caching
api.interceptors.response.use(
  (response) => {
    // Handle cached responses
    if (response.config.cachedResponse) {
      return {
        ...response,
        data: response.config.cachedResponse,
        status: 200,
        statusText: 'OK (cached)'
      }
    }
    
    // Cache successful GET responses
    const cacheConfig = shouldCache(response.config)
    if (cacheConfig && response.config.method?.toUpperCase() === 'GET' && response.status === 200) {
      apiCache.set(response.config.url, response.config.params, response.data, cacheConfig.timeout)
      
      if (import.meta.env.DEV) {
        console.log(`Cache SET: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
      }
    }
    
    // Invalidate cache for write operations
    invalidateCache(response.config)
    
    // Log successful responses in development
    if (import.meta.env.DEV) {
      console.log(`API Response: ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    }
    return response
  },
  (error) => {
    // Log errors in development
    if (import.meta.env.DEV) {
      console.error('API Error:', {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
    }
    
    // Handle different error types
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      
      // Only redirect if not already on login page
      if (window.location.pathname !== '/') {
        window.location.href = '/'
      }
    } else if (error.response?.status === 403) {
      // Forbidden - show error message
      console.error('Access forbidden:', error.response.data?.detail)
    } else if (error.response?.status === 422) {
      // Validation error - extract validation details
      const validationErrors = error.response.data?.detail
      if (validationErrors) {
        console.error('Validation errors:', validationErrors)
      }
    } else if (error.response?.status >= 500) {
      // Server error
      console.error('Server error:', error.response.data?.detail || error.message)
    } else if (error.code === 'ECONNABORTED') {
      // Timeout error
      console.error('Request timeout')
    } else if (!error.response) {
      // Network error
      console.error('Network error - check if backend is running')
    }
    
    // Enhance error object with more details
    const enhancedError = {
      ...error,
      isNetworkError: !error.response,
      isTimeoutError: error.code === 'ECONNABORTED',
      isValidationError: error.response?.status === 422,
      isAuthError: error.response?.status === 401,
      isForbiddenError: error.response?.status === 403,
      isServerError: error.response?.status >= 500,
      userMessage: getUserFriendlyErrorMessage(error)
    }
    
    return Promise.reject(enhancedError)
  }
)

// Helper function to get user-friendly error messages
function getUserFriendlyErrorMessage(error) {
  if (!error.response) {
    return 'Network error. Please check your connection and try again.'
  }
  
  // Try to extract message from response data
  const responseData = error.response.data
  if (responseData?.detail) {
    if (typeof responseData.detail === 'string') {
      return responseData.detail
    } else if (responseData.detail.message) {
      return responseData.detail.message
    }
  }
  
  // Fallback to status-based messages
  switch (error.response.status) {
    case 400:
      return 'Invalid request. Please check your input and try again.'
    case 401:
      return 'You are not authorized. Please log in again.'
    case 403:
      return 'You do not have permission to perform this action.'
    case 404:
      return 'The requested resource was not found.'
    case 422:
      return 'Validation error. Please check your input.'
    case 429:
      return 'Too many requests. Please wait a moment and try again.'
    case 500:
      return 'Server error. Please try again later.'
    case 503:
      return 'Service temporarily unavailable. Please try again later.'
    default:
      return 'An unexpected error occurred.'
  }
}

export default api