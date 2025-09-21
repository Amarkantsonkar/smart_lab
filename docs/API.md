# API Documentation

## Smart Lab Power Shutdown Assistant API

### Base URL
- Development: `http://localhost:8000`
- Production: `https://your-domain.com`

### Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Authentication Endpoints

### POST /api/v1/auth/login
Login user and receive JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "string",
    "username": "string",
    "email": "string",
    "role": "engineer|admin"
  }
}
```

### POST /api/v1/auth/register
Register a new user (Admin only).

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "engineer|admin"
}
```

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "role": "string",
  "created_at": "datetime"
}
```

### GET /api/v1/auth/me
Get current user information.

**Response:**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "role": "string",
  "created_at": "datetime"
}
```

## Device Management

### GET /api/v1/devices
Get all devices.

**Query Parameters:**
- `status`: Filter by device status (on, off, maintenance)
- `type`: Filter by device type
- `assigned_user`: Filter by assigned user ID

**Response:**
```json
[
  {
    "id": "string",
    "name": "string",
    "type": "string",
    "location": "string",
    "status": "on|off|maintenance",
    "assigned_user": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

### POST /api/v1/devices
Create a new device (Admin only).

**Request Body:**
```json
{
  "name": "string",
  "type": "string",
  "location": "string",
  "status": "on|off|maintenance",
  "assigned_user": "string"
}
```

### GET /api/v1/devices/{device_id}
Get device by ID.

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "type": "string",
  "location": "string",
  "status": "on|off|maintenance",
  "assigned_user": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### PUT /api/v1/devices/{device_id}
Update device (Admin only).

**Request Body:**
```json
{
  "name": "string",
  "type": "string",
  "location": "string",
  "status": "on|off|maintenance",
  "assigned_user": "string"
}
```

### DELETE /api/v1/devices/{device_id}
Delete device (Admin only).

## Checklist Management

### GET /api/v1/checklist
Get all checklist items.

**Query Parameters:**
- `completed`: Filter by completion status (true, false)
- `is_critical`: Filter by critical status (true, false)

**Response:**
```json
[
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "is_critical": "boolean",
    "completed": "boolean",
    "completed_by": "string",
    "completed_at": "datetime",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

### POST /api/v1/checklist
Create checklist item (Admin only).

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "is_critical": "boolean"
}
```

### PUT /api/v1/checklist/{item_id}
Update checklist item.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "is_critical": "boolean",
  "completed": "boolean"
}
```

### DELETE /api/v1/checklist/{item_id}
Delete checklist item (Admin only).

## Shutdown Operations

### POST /api/v1/shutdown/device/{device_id}
Shutdown a single device.

**Request Body:**
```json
{
  "reason": "string"
}
```

**Response:**
```json
{
  "status": "success|failed",
  "message": "string",
  "log_id": "string",
  "duration": "number"
}
```

### POST /api/v1/shutdown/bulk
Shutdown multiple devices.

**Request Body:**
```json
{
  "device_ids": ["string"],
  "reason": "string"
}
```

**Response:**
```json
{
  "results": [
    {
      "device_id": "string",
      "status": "success|failed",
      "message": "string",
      "log_id": "string",
      "duration": "number"
    }
  ],
  "summary": {
    "total": "number",
    "successful": "number",
    "failed": "number"
  }
}
```

### GET /api/v1/shutdown/status
Get current shutdown status and validation.

**Response:**
```json
{
  "can_shutdown": "boolean",
  "checklist_complete": "boolean",
  "critical_tasks_complete": "boolean",
  "active_devices": "number",
  "validation_errors": ["string"]
}
```

## Reporting

### GET /api/v1/shutdown-logs
Get shutdown logs with filtering and pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10)
- `device_id`: Filter by device ID
- `user_id`: Filter by user ID
- `status`: Filter by status (success, failed)
- `start_date`: Filter by start date (ISO format)
- `end_date`: Filter by end date (ISO format)
- `sort_by`: Sort field (timestamp, duration, status)
- `sort_order`: Sort order (asc, desc)

**Response:**
```json
{
  "items": [
    {
      "id": "string",
      "device_id": "string",
      "device_name": "string",
      "user_id": "string",
      "user_name": "string",
      "status": "success|failed",
      "timestamp": "datetime",
      "duration": "number",
      "reason": "string",
      "error_message": "string"
    }
  ],
  "total": "number",
  "page": "number",
  "total_pages": "number",
  "has_next": "boolean",
  "has_prev": "boolean"
}
```

### GET /api/v1/reports/stats
Get reporting statistics.

**Response:**
```json
{
  "total_shutdowns": "number",
  "successful_shutdowns": "number",
  "failed_shutdowns": "number",
  "success_rate": "number",
  "average_duration": "number",
  "most_active_users": [
    {
      "user_id": "string",
      "username": "string",
      "shutdown_count": "number"
    }
  ],
  "device_statistics": [
    {
      "device_id": "string",
      "device_name": "string",
      "shutdown_count": "number",
      "average_duration": "number"
    }
  ]
}
```

## User Management

### GET /api/v1/users
Get all users (Admin only).

**Response:**
```json
[
  {
    "id": "string",
    "username": "string",
    "email": "string",
    "role": "string",
    "created_at": "datetime",
    "last_login": "datetime"
  }
]
```

### PUT /api/v1/users/{user_id}
Update user (Admin only).

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "role": "engineer|admin"
}
```

### DELETE /api/v1/users/{user_id}
Delete user (Admin only).

## Health Check

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "datetime",
  "version": "string",
  "database": "connected"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "string",
  "errors": ["string"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

API endpoints are rate limited to prevent abuse:
- Authentication endpoints: 5 requests per minute
- General endpoints: 100 requests per minute
- Export endpoints: 10 requests per minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in window
- `X-RateLimit-Reset`: Window reset time (Unix timestamp)

## WebSocket Events

For real-time updates, the application uses custom events:

### Device Status Updates
```javascript
// Listen for device status changes
window.addEventListener('deviceStatusUpdate', (event) => {
  console.log('Device updated:', event.detail);
});
```

### Checklist Updates
```javascript
// Listen for checklist changes
window.addEventListener('checklistUpdate', (event) => {
  console.log('Checklist updated:', event.detail);
});
```

### Shutdown Events
```javascript
// Listen for shutdown events
window.addEventListener('shutdownComplete', (event) => {
  console.log('Shutdown completed:', event.detail);
});
```