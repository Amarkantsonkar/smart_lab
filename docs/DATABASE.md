# MongoDB Atlas Database Configuration

## Database Structure

The application uses MongoDB Atlas with the following collections:

### users collection
```json
type User = {
  _id: ObjectId,
  name: string,
  role: "Engineer" | "Admin",
  assignedDevices: string[],
  createdAt: Date,
  updatedAt: Date
}
```

### devices collection
```json
type Device = {
  _id: ObjectId,
  deviceId: string,
  name: string,
  status: "on" | "off" | "maintenance",
  location: string,
  lastShutdown: Date,
  createdAt: Date,
  updatedAt: Date
}
```

### checklist collection
```json
type ChecklistItem = {
  _id: ObjectId,
  taskId: string,
  description: string,
  category: "safety" | "security" | "backup" | "network",
  isCritical: boolean,
  completed: boolean,
  completedBy: string,
  completedAt: Date,
  createdAt: Date,
  updatedAt: Date
}
```

### shutdownLogs collection
```json
type ShutdownLog = {
  _id: ObjectId,
  logId: string,
  device: string,
  user: string,
  userName: string,
  status: "success" | "failed",
  reason?: string,
  timestamp: Date,
  duration: number
}
```

## Indexes

The following indexes should be created for optimal query performance:

- `users` collection:
  - `{ name: 1 }` (unique)
  - `{ role: 1 }`

- `devices` collection:
  - `{ deviceId: 1 }` (unique)
  - `{ status: 1 }`

- `checklist` collection:
  - `{ taskId: 1 }` (unique)
  - `{ isCritical: 1, completed: 1 }`

- `shutdownLogs` collection:
  - `{ timestamp: -1 }`
  - `{ device: 1, timestamp: -1 }`
  - `{ user: 1, timestamp: -1 }`

## Sample Data

### Users
```json
{
  "name": "john_doe",
  "role": "Engineer",
  "assignedDevices": ["server-01", "server-02"]
}
```

### Devices
```json
{
  "deviceId": "server-01",
  "name": "Main Application Server",
  "status": "on",
  "location": "Rack A1"
}
```

### Checklist Items
```json
{
  "taskId": "chk-001",
  "description": "Verify all data backups are complete",
  "category": "backup",
  "isCritical": true,
  "completed": false
}
```

## Connection String

The MongoDB connection string should follow this format:
```
mongodb+srv://<username>:<password>@cluster.mongodb.net/smartlab?retryWrites=true&w=majority
```

Replace `<username>` and `<password>` with your actual credentials.