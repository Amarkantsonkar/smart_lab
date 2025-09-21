/**
 * Tests for Login component
 * Tests user authentication, form validation, and error handling
 */

import React from 'react'
import { screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Login from '../../pages/Login'
import { renderWithProviders, mockFetch, mockApiResponses } from '../utils/testUtils'

// Mock the API service
jest.mock('../../services/api')

describe('Login Component', () => {
  beforeEach(() => {
    mockFetch()
  })

  afterEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  describe('Rendering', () => {
    it('renders login form correctly', () => {
      renderWithProviders(<Login />)
      
      expect(screen.getByRole('heading', { name: /smart lab power shutdown assistant/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
    })

    it('renders welcome message', () => {
      renderWithProviders(<Login />)
      
      expect(screen.getByText(/manage lab shutdowns safely/i)).toBeInTheDocument()
    })

    it('has proper form structure', () => {
      renderWithProviders(<Login />)
      
      const form = screen.getByRole('form')
      expect(form).toBeInTheDocument()
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      expect(usernameInput).toHaveAttribute('type', 'text')
      expect(passwordInput).toHaveAttribute('type', 'password')
    })
  })

  describe('Form Validation', () => {
    it('shows validation errors for empty fields', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Login />)
      
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/username is required/i)).toBeInTheDocument()
        expect(screen.getByText(/password is required/i)).toBeInTheDocument()
      })
    })

    it('shows validation error for short password', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      await user.type(usernameInput, 'testuser')
      await user.type(passwordInput, '123')
      
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/password must be at least 6 characters/i)).toBeInTheDocument()
      })
    })

    it('clears validation errors when user starts typing', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Login />)
      
      // Trigger validation errors
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/username is required/i)).toBeInTheDocument()
      })
      
      // Start typing in username field
      const usernameInput = screen.getByLabelText(/username/i)
      await user.type(usernameInput, 'test')
      
      await waitFor(() => {
        expect(screen.queryByText(/username is required/i)).not.toBeInTheDocument()
      })
    })
  })

  describe('Authentication', () => {
    it('submits form with valid credentials', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      await user.type(usernameInput, 'testuser')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/auth/login'),
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/x-www-form-urlencoded'
            }),
            body: 'username=testuser&password=password123'
          })
        )
      })
    })

    it('handles successful login', async () => {
      const user = userEvent.setup()
      
      // Mock successful login response
      mockFetch({
        '/api/v1/auth/login': {
          method: 'POST',
          response: mockApiResponses.login
        }
      })
      
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      await user.type(usernameInput, 'testuser')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(localStorage.getItem('access_token')).toBe('mock-jwt-token')
        expect(localStorage.getItem('user')).toBe(JSON.stringify(mockApiResponses.login.user))
      })
    })

    it('handles login failure', async () => {
      const user = userEvent.setup()
      
      // Mock failed login response
      mockFetch({
        '/api/v1/auth/login': {
          method: 'POST',
          response: { detail: { message: 'Incorrect username or password' } }
        }
      })
      
      // Override fetch to return error response
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ detail: { message: 'Incorrect username or password' } })
      })
      
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      await user.type(usernameInput, 'wronguser')
      await user.type(passwordInput, 'wrongpassword')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/incorrect username or password/i)).toBeInTheDocument()
      })
    })

    it('handles network errors', async () => {
      const user = userEvent.setup()
      
      // Mock network error
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'))
      
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      await user.type(usernameInput, 'testuser')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument()
      })
    })
  })

  describe('Loading States', () => {
    it('shows loading state during login', async () => {
      const user = userEvent.setup()
      
      // Mock slow response
      global.fetch = jest.fn().mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve(mockApiResponses.login)
          }), 1000)
        )
      )
      
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      await user.type(usernameInput, 'testuser')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      expect(screen.getByText(/signing in/i)).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
    })

    it('disables form during submission', async () => {
      const user = userEvent.setup()
      
      // Mock slow response
      global.fetch = jest.fn().mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            status: 200,
            json: () => Promise.resolve(mockApiResponses.login)
          }), 100)
        )
      )
      
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      await user.type(usernameInput, 'testuser')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      expect(usernameInput).toBeDisabled()
      expect(passwordInput).toBeDisabled()
      expect(submitButton).toBeDisabled()
    })
  })

  describe('Accessibility', () => {
    it('has proper form labels', () => {
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      expect(usernameInput).toHaveAttribute('aria-required', 'true')
      expect(passwordInput).toHaveAttribute('aria-required', 'true')
    })

    it('has proper heading hierarchy', () => {
      renderWithProviders(<Login />)
      
      const mainHeading = screen.getByRole('heading', { level: 1 })
      expect(mainHeading).toBeInTheDocument()
    })

    it('shows error messages with proper ARIA attributes', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Login />)
      
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        const errorMessage = screen.getByText(/username is required/i)
        expect(errorMessage).toHaveAttribute('role', 'alert')
      })
    })
  })

  describe('Keyboard Navigation', () => {
    it('allows form submission with Enter key', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      await user.type(usernameInput, 'testuser')
      await user.type(passwordInput, 'password123')
      await user.keyboard('{Enter}')
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalled()
      })
    })

    it('focuses password field after username', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      await user.type(usernameInput, 'testuser')
      await user.keyboard('{Tab}')
      
      expect(passwordInput).toHaveFocus()
    })
  })

  describe('Role-based Redirects', () => {
    it('redirects admin users to admin dashboard', async () => {
      const user = userEvent.setup()
      
      // Mock admin login response
      const adminResponse = {
        access_token: 'admin-token',
        token_type: 'bearer',
        user: { ...mockApiResponses.login.user, role: 'admin' }
      }
      
      mockFetch({
        '/api/v1/auth/login': {
          method: 'POST',
          response: adminResponse
        }
      })
      
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      await user.type(usernameInput, 'admin')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(localStorage.getItem('user')).toContain('admin')
      })
    })

    it('redirects engineer users to dashboard', async () => {
      const user = userEvent.setup()
      renderWithProviders(<Login />)
      
      const usernameInput = screen.getByLabelText(/username/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /sign in/i })
      
      await user.type(usernameInput, 'engineer')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(localStorage.getItem('user')).toContain('engineer')
      })
    })
  })
})