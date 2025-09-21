# Smart Lab Power Shutdown Assistant - Phase-wise TODO List

## Phase 1: Project Setup & Initialization
- [x] Initialize project directory structure with `backend`, `frontend`, and `docs` folders
- [x] Create comprehensive phase-wise TODO.md file in root directory
- [ ] Set up version control (Git) with proper .gitignore
- [ ] Document project structure and technology stack in README.md

## Phase 2: Backend Development (FastAPI)
### Setup & Configuration
- [ ] Set up FastAPI backend with basic project structure
- [ ] Install required dependencies (fastapi, uvicorn, python-jose, pymongo, python-dotenv)
- [ ] Configure environment variables for development and production
- [ ] Set up logging configuration

### Authentication & Authorization
- [ ] Implement JWT-based authentication system
- [ ] Define User model with roles (Engineer, Admin)
- [ ] Create registration and login endpoints
- [ ] Implement role-based access control (RBAC) middleware
- [ ] Secure API routes based on user roles

### Data Models & Database Schema
- [ ] Define Pydantic models for all entities
  - User: { name, role, assignedDevices }
  - Device: { deviceId, name, status }
  - Checklist: { taskId, description, completed }
  - ShutdownLog: { logId, device, user, status, timestamp }
- [ ] Create MongoDB schema definitions
- [ ] Set up indexes for frequently queried fields

### API Endpoints
- [ ] Implement CRUD operations for Users
- [ ] Implement CRUD operations for Devices
- [ ] Implement CRUD operations for Checklist items
- [ ] Implement CRUD operations for Shutdown Logs
- [ ] Create validation endpoint to check if all critical checklist items are complete
- [ ] Implement shutdown initiation endpoint with pre-check validation
- [ ] Create dashboard data endpoint for real-time system status
- [ ] Implement reporting endpoint with filtering capabilities

### Business Logic
- [ ] Implement shutdown validation logic that verifies checklist completion before allowing shutdown
- [ ] Create logging mechanism for all shutdown attempts (success/failure)
- [ ] Implement notification trigger when all devices are safely shut down
- [ ] Add input validation and error handling for all endpoints

## Phase 3: Frontend Development (React.js)
### Setup & Architecture
- [ ] Set up React.js frontend using Vite
- [ ] Configure routing (React Router)
- [ ] Set up state management (Context API or Redux)
- [ ] Implement theme and styling system (CSS modules or styled-components)

### Authentication UI
- [ ] Create login page with form validation
- [ ] Implement role-based redirection after login
- [ ] Add JWT token storage and refresh mechanism
- [ ] Create protected routes based on user roles

### Maintenance Checklist Module
- [ ] Design and implement maintenance checklist interface
- [ ] Create toggleable checklist items with persistence
- [ ] Implement visual indicators for completed vs. pending tasks
- [ ] Add validation feedback when attempting shutdown with incomplete checklist

### Shutdown Control Module
- [ ] Design shutdown control panel showing assigned devices
- [ ] Implement device status indicators (powered on/off)
- [ ] Create shutdown button with confirmation dialog
- [ ] Show simulation of shutdown process

### Dashboard Module
- [ ] Develop real-time dashboard displaying all lab systems
- [ ] Implement power state visualization (color-coded indicators)
- [ ] Add summary statistics (total devices, powered on/off, last shutdown time)
- [ ] Include quick actions for common tasks

### Reporting Module
- [ ] Create report view with date filters and status filters
- [ ] Display table of shutdown logs with sorting capabilities
- [ ] Implement CSV export functionality
- [ ] Implement PDF report generation

### Notifications System
- [ ] Integrate toast/alert library for user notifications
- [ ] Show success message on successful shutdown
- [ ] Show error message on failed shutdown attempts
- [ ] Display completion alert when all devices are safely shut down

## Phase 4: Database & Integration
### MongoDB Atlas
- [ ] Create MongoDB Atlas cluster
- [ ] Configure database security settings (IP whitelist, authentication)
- [ ] Set up collections: users, devices, checklist, shutdownLogs
- [ ] Populate initial data for testing
- [ ] Configure backup and monitoring

### Backend-Frontend Integration
- [ ] Connect React frontend to FastAPI backend
- [ ] Handle CORS configuration in FastAPI
- [ ] Implement HTTP client (axios/fetch) with interceptors for auth
- [ ] Create API service layer for all backend communications
- [ ] Handle loading states and error responses in UI

## Phase 5: Testing
### Backend Testing
- [ ] Write unit tests for Pydantic models
- [ ] Write unit tests for authentication logic
- [ ] Write integration tests for all API endpoints
- [ ] Test role-based access control scenarios
- [ ] Test edge cases and error conditions

### Frontend Testing
- [ ] Write unit tests for React components
- [ ] Write integration tests for component interactions
- [ ] Test form validations and user flows
- [ ] Test state management behavior

### End-to-End Testing
- [ ] Set up end-to-end testing framework (Playwright/Cypress)
- [ ] Test complete workflow: login → checklist → shutdown → report
- [ ] Test role-specific workflows for Engineer and Admin
- [ ] Test failure scenarios and error recovery

## Phase 6: Deployment & Documentation
### Deployment Preparation
- [ ] Create Dockerfiles for backend and frontend
- [ ] Configure environment variables for different environments
- [ ] Set up reverse proxy configuration (Nginx)
- [ ] Implement health check endpoints
- [ ] Prepare deployment scripts

### Documentation
- [ ] Generate OpenAPI/Swagger documentation for backend APIs
- [ ] Document frontend component architecture
- [ ] Create setup and installation guide
- [ ] Document user roles and permissions
- [ ] Create troubleshooting guide

## Phase 7: Final Review & Launch
- [ ] Conduct code review for security vulnerabilities
- [ ] Perform performance optimization
- [ ] Test in staging environment
- [ ] Fix any remaining bugs
- [ ] Prepare release notes
- [ ] Deploy to production environment
- [ ] Verify all systems functioning correctly in production