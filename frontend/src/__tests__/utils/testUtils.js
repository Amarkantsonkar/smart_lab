// Test utilities for Smart Lab Power Shutdown Assistant frontend tests

import React from 'react'
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../../hooks/useAuth'

// Mock user data
export const mockUser = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  full_name: 'Test User',
  role: 'engineer',
  assignedDevices: ['DEV-001', 'DEV-002']
}

export const mockAdmin = {
  id: '2',
  username: 'testadmin', 
  email: 'admin@example.com',
  full_name: 'Test Admin',
  role: 'admin',
  assignedDevices: []
}

// Mock device data
export const mockDevices = [
  {
    id: '1',
    deviceId: 'DEV-001',
    name: 'Test Server 1',
    type: 'server',
    location: 'Rack A1',
    status: 'on',
    assignedUsers: ['1'],
    specifications: {
      cpu: 'Intel Xeon',
      ram: '32GB',
      storage: '1TB SSD'
    }
  },
  {
    id: '2', 
    deviceId: 'DEV-002',
    name: 'Test Server 2',
    type: 'server',
    location: 'Rack A2',
    status: 'off',
    assignedUsers: ['1'],
    specifications: {
      cpu: 'Intel Xeon',
      ram: '16GB',
      storage: '500GB SSD'
    }
  }
]

// Mock checklist data
export const mockChecklistItems = [
  {
    id: '1',
    taskId: 'SAFETY-001',
    description: 'Verify all personnel have exited the lab area',
    category: 'safety',
    isCritical: true,
    completed: false,
    instructions: 'Check all rooms and ensure no personnel remain',
    estimatedDuration: 5
  },
  {
    id: '2',
    taskId: 'BACKUP-001', 
    description: 'Complete database backup',
    category: 'backup',
    isCritical: true,
    completed: true,
    completedBy: 'testuser',
    completedAt: '2023-12-01T10:00:00Z',
    instructions: 'Run full database backup and verify integrity',
    estimatedDuration: 30
  },
  {
    id: '3',
    taskId: 'NETWORK-001',
    description: 'Verify network connectivity', 
    category: 'network',
    isCritical: false,
    completed: false,
    instructions: 'Test network connections',
    estimatedDuration: 15
  }
]

// Mock shutdown logs
export const mockShutdownLogs = [
  {
    id: '1',
    deviceId: 'DEV-001',
    deviceName: 'Test Server 1',
    userId: '1',
    userName: 'testuser',
    status: 'success',
    timestamp: '2023-12-01T12:00:00Z',
    duration: 45,
    reason: 'Maintenance shutdown'
  },
  {
    id: '2',
    deviceId: 'DEV-002', 
    deviceName: 'Test Server 2',
    userId: '1',
    userName: 'testuser',
    status: 'failed',
    timestamp: '2023-12-01T11:30:00Z',
    duration: 0,
    reason: 'Emergency shutdown attempt',
    errorMessage: 'Critical checklist items incomplete'
  }
]

// Custom render function with providers
export function renderWithProviders(ui, { 
  initialUser = null,
  initialRoute = '/',
  ...renderOptions 
} = {}) {
  // Mock the useAuth hook to return the provided user
  const mockUseAuth = {
    user: initialUser,
    login: jest.fn(),
    logout: jest.fn()
  }

  function Wrapper({ children }) {
    // Mock the AuthProvider to use our mock data
    React.useEffect(() => {
      if (initialUser) {
        localStorage.setItem('user', JSON.stringify(initialUser))
        localStorage.setItem('access_token', 'mock-token')
      }
    }, [])

    return (
      <BrowserRouter>
        <AuthProvider>
          {children}
        </AuthProvider>
      </BrowserRouter>
    )
  }

  return render(ui, { wrapper: Wrapper, ...renderOptions })
}

// Mock API responses
export const mockApiResponses = {
  // Auth responses
  login: {
    access_token: 'mock-jwt-token',
    token_type: 'bearer',
    user: mockUser
  },
  register: mockUser,

  // Device responses  
  devices: mockDevices,
  device: mockDevices[0],

  // Checklist responses
  checklist: mockChecklistItems,
  checklistItem: mockChecklistItems[0],
  validateChecklist: {
    allCompleted: false,
    criticalCompleted: false,
    incompleteItems: [mockChecklistItems[0]],
    totalItems: 3,
    completedItems: 1,
    criticalItems: 2,
    completedCriticalItems: 1
  },

  // Shutdown responses
  shutdownSuccess: {
    success: true,
    deviceId: 'DEV-001',
    duration: 45,
    timestamp: '2023-12-01T12:00:00Z'
  },
  shutdownFailure: {
    success: false,
    deviceId: 'DEV-001',
    error: 'Critical checklist items incomplete'
  },
  shutdownLogs: mockShutdownLogs
}

// Mock fetch function
export function mockFetch(mockResponses = {}) {
  const defaultResponses = {
    '/api/v1/auth/login': { method: 'POST', response: mockApiResponses.login },
    '/api/v1/auth/register': { method: 'POST', response: mockApiResponses.register },
    '/api/v1/devices': { method: 'GET', response: mockApiResponses.devices },
    '/api/v1/checklist': { method: 'GET', response: mockApiResponses.checklist },
    '/api/v1/shutdown/validate-checklist': { method: 'POST', response: mockApiResponses.validateChecklist },
    '/api/v1/shutdown-logs': { method: 'GET', response: mockApiResponses.shutdownLogs },
    ...mockResponses
  }

  global.fetch = jest.fn((url, options = {}) => {
    const method = options.method || 'GET'
    const endpoint = url.replace('http://localhost:8000', '')
    
    const mockConfig = defaultResponses[endpoint]
    
    if (mockConfig && mockConfig.method === method) {
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve(mockConfig.response),
        headers: new Headers(),
        text: () => Promise.resolve(JSON.stringify(mockConfig.response))
      })
    }
    
    // Default to 404 for unmatched routes
    return Promise.resolve({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: { message: 'Not found' } }),
      headers: new Headers(),
      text: () => Promise.resolve('Not found')
    })
  })
}

// Helper to wait for async operations
export const waitForAsync = () => new Promise(resolve => setTimeout(resolve, 0))

// Custom matchers
export const customMatchers = {
  toBeInTheDocument: (received) => {
    const pass = document.body.contains(received)
    return {
      message: () => `expected element ${pass ? 'not ' : ''}to be in the document`,
      pass
    }
  }
}

// Test data factories
export const createMockUser = (overrides = {}) => ({
  ...mockUser,
  ...overrides
})

export const createMockDevice = (overrides = {}) => ({
  ...mockDevices[0],
  ...overrides
})

export const createMockChecklistItem = (overrides = {}) => ({
  ...mockChecklistItems[0],
  ...overrides
})

export const createMockShutdownLog = (overrides = {}) => ({
  ...mockShutdownLogs[0],
  ...overrides
})