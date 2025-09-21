/**
 * Tests for Checklist component
 * Tests checklist validation logic according to project specifications:
 * Critical checklist tasks must be completed before shutdown; 
 * UI must prevent completion of all non-critical tasks if critical ones remain incomplete.
 */

import React from 'react'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Checklist from '../../pages/Checklist'
import { 
  renderWithProviders, 
  mockFetch, 
  mockApiResponses, 
  mockUser, 
  mockChecklistItems,
  createMockChecklistItem 
} from '../utils/testUtils'

// Mock the notification service
jest.mock('../../services/notifications', () => ({
  success: jest.fn(),
  error: jest.fn(),
  warning: jest.fn(),
  info: jest.fn(),
}))

describe('Checklist Component', () => {
  beforeEach(() => {
    mockFetch()
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  describe('Rendering', () => {
    it('renders checklist page correctly', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      expect(screen.getByText(/maintenance checklist/i)).toBeInTheDocument()
      
      await waitFor(() => {
        expect(screen.getByText(/verify all personnel have exited/i)).toBeInTheDocument()
        expect(screen.getByText(/complete database backup/i)).toBeInTheDocument()
      })
    })

    it('displays loading state initially', () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      expect(screen.getByText(/loading checklist/i)).toBeInTheDocument()
    })

    it('renders checklist statistics', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        expect(screen.getByText(/total items/i)).toBeInTheDocument()
        expect(screen.getByText(/completed/i)).toBeInTheDocument()
        expect(screen.getByText(/pending/i)).toBeInTheDocument()
      })
    })

    it('renders filter section', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        expect(screen.getByText(/filters & search/i)).toBeInTheDocument()
      })
    })
  })

  describe('Checklist Items Display', () => {
    it('displays checklist items with correct information', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        // Check critical item display
        expect(screen.getByText(/⚠️.*verify all personnel have exited/i)).toBeInTheDocument()
        
        // Check completed item display
        expect(screen.getByText(/complete database backup/i)).toBeInTheDocument()
        
        // Check category badges
        expect(screen.getByText(/safety/i)).toBeInTheDocument()
        expect(screen.getByText(/backup/i)).toBeInTheDocument()
      })
    })

    it('shows different icons for critical and non-critical items', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        // Critical items should have warning icon
        expect(screen.getByText(/⚠️/)).toBeInTheDocument()
        
        // Non-critical items should have info icon  
        expect(screen.getByText(/ℹ️/)).toBeInTheDocument()
      })
    })

    it('displays completion information for completed items', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        expect(screen.getByText(/completed by testuser/i)).toBeInTheDocument()
      })
    })

    it('applies correct styling for critical items', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const criticalItem = screen.getByText(/verify all personnel have exited/i).closest('.checklist-item')
        expect(criticalItem).toHaveClass('critical')
      })
    })
  })

  describe('Checklist Completion Logic - Project Specifications', () => {
    it('allows marking critical tasks as complete', async () => {
      const user = userEvent.setup()
      
      // Mock API response for completion
      mockFetch({
        '/api/v1/checklist': { method: 'GET', response: mockChecklistItems },
        '/api/v1/checklist/SAFETY-001': { 
          method: 'PUT', 
          response: { ...mockChecklistItems[0], completed: true } 
        }
      })
      
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const checkbox = screen.getByLabelText(/mark as complete/i)
        expect(checkbox).toBeInTheDocument()
      })
      
      const criticalTaskCheckbox = screen.getAllByLabelText(/mark as complete/i)[0]
      await user.click(criticalTaskCheckbox)
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/checklist/SAFETY-001'),
          expect.objectContaining({
            method: 'PUT',
            body: JSON.stringify({ completed: true })
          })
        )
      })
    })

    it('prevents completion of non-critical tasks when critical tasks are incomplete', async () => {
      const user = userEvent.setup()
      
      // Mock checklist with incomplete critical task
      const checklistWithIncompleteCritical = [
        createMockChecklistItem({ 
          taskId: 'CRITICAL-001', 
          isCritical: true, 
          completed: false 
        }),
        createMockChecklistItem({ 
          taskId: 'NORMAL-001', 
          isCritical: false, 
          completed: false 
        })
      ]
      
      // Mock API to return validation error
      mockFetch({
        '/api/v1/checklist': { method: 'GET', response: checklistWithIncompleteCritical },
        '/api/v1/checklist/NORMAL-001': { 
          method: 'PUT', 
          response: { 
            detail: { message: 'Critical tasks must be completed first' } 
          }
        }
      })
      
      // Override fetch to return error for non-critical completion
      global.fetch = jest.fn((url, options) => {
        if (url.includes('NORMAL-001') && options?.method === 'PUT') {
          return Promise.resolve({
            ok: false,
            status: 400,
            json: () => Promise.resolve({ 
              detail: { message: 'Critical tasks must be completed first' } 
            })
          })
        }
        
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(checklistWithIncompleteCritical)
        })
      })
      
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const checkboxes = screen.getAllByLabelText(/mark as complete/i)
        expect(checkboxes).toHaveLength(2)
      })
      
      // Try to complete non-critical task
      const nonCriticalCheckbox = screen.getAllByLabelText(/mark as complete/i)[1]
      await user.click(nonCriticalCheckbox)
      
      await waitFor(() => {
        expect(screen.getByText(/critical tasks must be completed first/i)).toBeInTheDocument()
      })
    })

    it('allows completion of non-critical tasks when all critical tasks are complete', async () => {
      const user = userEvent.setup()
      
      // Mock checklist with all critical tasks completed
      const checklistWithCompletedCritical = [
        createMockChecklistItem({ 
          taskId: 'CRITICAL-001', 
          isCritical: true, 
          completed: true 
        }),
        createMockChecklistItem({ 
          taskId: 'NORMAL-001', 
          isCritical: false, 
          completed: false 
        })
      ]
      
      mockFetch({
        '/api/v1/checklist': { method: 'GET', response: checklistWithCompletedCritical },
        '/api/v1/checklist/NORMAL-001': { 
          method: 'PUT', 
          response: { ...checklistWithCompletedCritical[1], completed: true } 
        }
      })
      
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const checkboxes = screen.getAllByLabelText(/mark as complete/i)
        expect(checkboxes).toHaveLength(1) // Only non-critical task should be completable
      })
      
      const nonCriticalCheckbox = screen.getByLabelText(/mark as complete/i)
      await user.click(nonCriticalCheckbox)
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/checklist/NORMAL-001'),
          expect.objectContaining({
            method: 'PUT',
            body: JSON.stringify({ completed: true })
          })
        )
      })
    })

    it('shows warning when critical tasks are incomplete', async () => {
      const checklistWithIncompleteCritical = [
        createMockChecklistItem({ 
          taskId: 'CRITICAL-001', 
          isCritical: true, 
          completed: false,
          description: 'Critical safety check'
        })
      ]
      
      mockFetch({
        '/api/v1/checklist': { method: 'GET', response: checklistWithIncompleteCritical }
      })
      
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        expect(screen.getByText(/critical task\(s\) remaining.*shutdown blocked/i)).toBeInTheDocument()
      })
    })
  })

  describe('Bulk Operations', () => {
    it('shows complete all non-critical tasks button', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        expect(screen.getByText(/complete all non-critical tasks/i)).toBeInTheDocument()
      })
    })

    it('prevents bulk completion when critical tasks are incomplete', async () => {
      const user = userEvent.setup()
      
      const checklistWithIncompleteCritical = [
        createMockChecklistItem({ 
          taskId: 'CRITICAL-001', 
          isCritical: true, 
          completed: false 
        })
      ]
      
      mockFetch({
        '/api/v1/checklist': { method: 'GET', response: checklistWithIncompleteCritical }
      })
      
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const completeAllButton = screen.getByText(/complete all non-critical tasks/i)
        expect(completeAllButton).toBeInTheDocument()
      })
      
      const completeAllButton = screen.getByText(/complete all non-critical tasks/i)
      await user.click(completeAllButton)
      
      await waitFor(() => {
        expect(screen.getByText(/cannot complete checklist.*critical tasks must be completed first/i)).toBeInTheDocument()
      })
    })

    it('shows confirmation dialog for bulk completion', async () => {
      const user = userEvent.setup()
      
      const checklistWithCompletedCritical = [
        createMockChecklistItem({ 
          taskId: 'CRITICAL-001', 
          isCritical: true, 
          completed: true 
        }),
        createMockChecklistItem({ 
          taskId: 'NORMAL-001', 
          isCritical: false, 
          completed: false 
        })
      ]
      
      mockFetch({
        '/api/v1/checklist': { method: 'GET', response: checklistWithCompletedCritical }
      })
      
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const completeAllButton = screen.getByText(/complete all non-critical tasks/i)
        expect(completeAllButton).toBeInTheDocument()
      })
      
      const completeAllButton = screen.getByText(/complete all non-critical tasks/i)
      await user.click(completeAllButton)
      
      await waitFor(() => {
        expect(screen.getByText(/complete all non-critical tasks\?/i)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /confirm/i })).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
      })
    })
  })

  describe('Filtering', () => {
    it('filters checklist items by category', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const categoryFilter = screen.getByLabelText(/category/i)
        expect(categoryFilter).toBeInTheDocument()
      })
      
      const categoryFilter = screen.getByLabelText(/category/i)
      await user.selectOptions(categoryFilter, 'safety')
      
      // Check that only safety items are displayed
      await waitFor(() => {
        expect(screen.getByText(/verify all personnel have exited/i)).toBeInTheDocument()
        expect(screen.queryByText(/complete database backup/i)).not.toBeInTheDocument()
      })
    })

    it('filters checklist items by completion status', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const statusFilter = screen.getByLabelText(/status/i)
        expect(statusFilter).toBeInTheDocument()
      })
      
      const statusFilter = screen.getByLabelText(/status/i)
      await user.selectOptions(statusFilter, 'completed')
      
      // Check that only completed items are displayed
      await waitFor(() => {
        expect(screen.getByText(/complete database backup/i)).toBeInTheDocument()
        expect(screen.queryByText(/verify all personnel have exited/i)).not.toBeInTheDocument()
      })
    })

    it('filters checklist items by criticality', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const criticalityFilter = screen.getByLabelText(/criticality/i)
        expect(criticalityFilter).toBeInTheDocument()
      })
      
      const criticalityFilter = screen.getByLabelText(/criticality/i)
      await user.selectOptions(criticalityFilter, 'critical')
      
      // Check that only critical items are displayed
      await waitFor(() => {
        expect(screen.getByText(/verify all personnel have exited/i)).toBeInTheDocument()
        expect(screen.getByText(/complete database backup/i)).toBeInTheDocument()
        expect(screen.queryByText(/verify network connectivity/i)).not.toBeInTheDocument()
      })
    })

    it('clears filters when clear button is clicked', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const clearButton = screen.getByText(/clear filters/i)
        expect(clearButton).toBeInTheDocument()
      })
      
      // Apply a filter first
      const categoryFilter = screen.getByLabelText(/category/i)
      await user.selectOptions(categoryFilter, 'safety')
      
      // Clear filters
      const clearButton = screen.getByText(/clear filters/i)
      await user.click(clearButton)
      
      // Check that all items are displayed again
      await waitFor(() => {
        expect(screen.getByText(/verify all personnel have exited/i)).toBeInTheDocument()
        expect(screen.getByText(/complete database backup/i)).toBeInTheDocument()
        expect(screen.getByText(/verify network connectivity/i)).toBeInTheDocument()
      })
    })
  })

  describe('Real-time Updates', () => {
    it('listens for checklist update events', async () => {
      const mockEventListener = jest.spyOn(window, 'addEventListener')
      
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      expect(mockEventListener).toHaveBeenCalledWith(
        'checklist-updated',
        expect.any(Function)
      )
    })

    it('refetches data when checklist update event is dispatched', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      // Clear previous fetch calls
      jest.clearAllMocks()
      
      // Dispatch checklist update event
      window.dispatchEvent(new CustomEvent('checklist-updated'))
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/checklist'),
          expect.any(Object)
        )
      })
    })

    it('cleans up event listener on unmount', () => {
      const mockRemoveEventListener = jest.spyOn(window, 'removeEventListener')
      
      const { unmount } = renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      unmount()
      
      expect(mockRemoveEventListener).toHaveBeenCalledWith(
        'checklist-updated',
        expect.any(Function)
      )
    })
  })

  describe('Error Handling', () => {
    it('displays error message when fetch fails', async () => {
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'))
      
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load checklist items/i)).toBeInTheDocument()
      })
    })

    it('handles completion toggle errors gracefully', async () => {
      const user = userEvent.setup()
      
      mockFetch({
        '/api/v1/checklist': { method: 'GET', response: mockChecklistItems }
      })
      
      // Mock failed completion request
      global.fetch = jest.fn((url, options) => {
        if (options?.method === 'PUT') {
          return Promise.reject(new Error('Update failed'))
        }
        
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve(mockChecklistItems)
        })
      })
      
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const checkbox = screen.getAllByLabelText(/mark as complete/i)[0]
        expect(checkbox).toBeInTheDocument()
      })
      
      const checkbox = screen.getAllByLabelText(/mark as complete/i)[0]
      await user.click(checkbox)
      
      await waitFor(() => {
        expect(screen.getByText(/failed to update checklist item/i)).toBeInTheDocument()
      })
    })
  })

  describe('Accessibility', () => {
    it('has proper heading structure', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
    })

    it('has accessible form labels', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        expect(screen.getByLabelText(/category/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/status/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/criticality/i)).toBeInTheDocument()
      })
    })

    it('has accessible checkboxes', async () => {
      renderWithProviders(<Checklist />, { initialUser: mockUser })
      
      await waitFor(() => {
        const checkboxes = screen.getAllByRole('checkbox')
        checkboxes.forEach(checkbox => {
          expect(checkbox).toHaveAccessibleName()
        })
      })
    })
  })
})