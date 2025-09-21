# MongoDB Setup Guide

This guide covers setting up MongoDB for the Smart Lab Power Shutdown Assistant, including both local MongoDB and MongoDB Atlas configurations.

## Table of Contents

1. [Local MongoDB Setup](#local-mongodb-setup)
2. [MongoDB Atlas Setup](#mongodb-atlas-setup)
3. [Database Schema](#database-schema)
4. [Collections and Indexes](#collections-and-indexes)
5. [Initial Data Setup](#initial-data-setup)
6. [Migration Scripts](#migration-scripts)
7. [Troubleshooting](#troubleshooting)

## Local MongoDB Setup

### Installation

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

**Windows:**
1. Download MongoDB Community Server from https://www.mongodb.com/try/download/community
2. Run the installer and follow the setup wizard
3. Start MongoDB as a Windows service

### Configuration

1. **Update environment variables** in `backend/.env`:
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE_NAME=smart_lab_shutdown
```

2. **Run the setup script**:
```bash
cd backend
python scripts/setup_mongodb.py
```

## MongoDB Atlas Setup

### Step 1: Create Account and Cluster

1. **Sign up for MongoDB Atlas**:
   - Go to https://www.mongodb.com/cloud/atlas
   - Create a free account

2. **Create a new cluster**:
   - Click "Build a Database"
   - Choose "FREE" tier (M0 Sandbox)
   - Select cloud provider and region
   - Name your cluster (e.g., "smart-lab-cluster")

### Step 2: Configure Database Access

1. **Create database user**:
   - Go to "Database Access" in sidebar
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Create username and secure password
   - Grant "Atlas Admin" privileges (or specific database permissions)

### Step 3: Configure Network Access

1. **Add IP addresses**:
   - Go to "Network Access" in sidebar
   - Click "Add IP Address"
   - For development: Add `0.0.0.0/0` (allow access from anywhere)
   - For production: Add specific IP addresses

### Step 4: Get Connection String

1. **Connect to cluster**:
   - Go to "Databases" and click "Connect"
   - Choose "Connect your application"
   - Select "Python" and "3.6 or later"
   - Copy the connection string

2. **Update environment variables** in `backend/.env`:
```env
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster-url>/<database>?retryWrites=true&w=majority
MONGODB_DATABASE_NAME=smart_lab_shutdown
```

### Step 5: Install Dependencies and Setup

```bash
cd backend
pip install motor pymongo[srv] dnspython
python scripts/setup_mongodb.py
```

## Database Schema

### Collections Overview

| Collection | Purpose | Key Fields |
|------------|---------|------------|
| `users` | User accounts and authentication | email, username, role, assignedDevices |
| `devices` | Lab equipment and servers | deviceId, name, status, location |
| `checklist` | Maintenance checklist items | taskId, description, isCritical, completed |
| `shutdown_logs` | Shutdown attempt records | deviceId, userId, status, timestamp |
| `migrations` | Database migration tracking | name, applied_at, status |
| `audit_logs` | System audit trail | user_id, action, resource_type, timestamp |

## Collections and Indexes

### Users Collection

**Document Structure:**
```javascript
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "hashed_password": "string",
  "full_name": "string",
  "role": "admin|engineer",
  "is_active": boolean,
  "assignedDevices": ["string"],
  "preferences": {
    "theme": "light|dark",
    "notifications": {
      "email": boolean,
      "browser": boolean,
      "shutdown_alerts": boolean
    }
  },
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Indexes:**
- `email` (unique)
- `username` (unique)
- `role`
- `created_at` (descending)
- `is_active`

### Devices Collection

**Document Structure:**
```javascript
{
  "_id": ObjectId,
  "deviceId": "string",
  "name": "string",
  "type": "server|network|storage",
  "location": "string",
  "status": "on|off|maintenance",
  "assignedUsers": ["string"],
  "specifications": {
    "cpu": "string",
    "ram": "string",
    "storage": "string"
  },
  "metadata": {
    "manufacturer": "string",
    "model": "string",
    "serial_number": "string",
    "purchase_date": ISODate,
    "warranty_expires": ISODate
  },
  "lastShutdown": ISODate,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Indexes:**
- `deviceId` (unique)
- `name`
- `status`
- `location`
- `assignedUsers`
- `lastShutdown` (descending)

### Checklist Collection

**Document Structure:**
```javascript
{
  "_id": ObjectId,
  "taskId": "string",
  "description": "string",
  "category": "safety|security|backup|network",
  "isCritical": boolean,
  "completed": boolean,
  "completedBy": "string",
  "completedAt": ISODate,
  "dependencies": ["string"],
  "priority": number,
  "instructions": "string",
  "estimatedDuration": number,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

**Indexes:**
- `taskId` (unique)
- `category`
- `isCritical`
- `completed`
- `completedBy`
- `completedAt` (descending)
- Compound: `category + isCritical`
- Compound: `completed + isCritical`

### Shutdown Logs Collection

**Document Structure:**
```javascript
{
  "_id": ObjectId,
  "deviceId": "string",
  "deviceName": "string",
  "userId": "string",
  "userName": "string",
  "status": "success|failed",
  "timestamp": ISODate,
  "duration": number,
  "reason": "string",
  "errorMessage": "string",
  "checklistValidation": {
    "allCompleted": boolean,
    "criticalCompleted": boolean,
    "incompleteItems": ["string"]
  }
}
```

**Indexes:**
- `deviceId`
- `userId`
- `status`
- `timestamp` (descending)
- Compound: `deviceId + timestamp`
- Compound: `userId + timestamp`
- Compound: `status + timestamp`

## Initial Data Setup

The setup script creates initial data including:

### Default Admin User
- **Username:** `admin`
- **Password:** `admin123` (⚠️ Change in production!)
- **Email:** `admin@smartlab.com`
- **Role:** `admin`

### Sample Devices
- Main Database Server (SRV-001)
- Web Application Server (SRV-002)
- Core Network Switch (NET-001)

### Sample Checklist Items
- Safety verification tasks (Critical)
- Security checkpoint tasks (Critical)
- Backup verification (Critical)
- Network connectivity check (Non-critical)

## Migration Scripts

### Running Migrations

```bash
# Setup initial database
python scripts/setup_mongodb.py

# Run database migrations
python scripts/migrate_database.py
```

### Available Migrations

1. **001_initial_schema** - Basic collections and indexes
2. **002_add_user_preferences** - User preference settings
3. **003_add_device_metadata** - Device metadata and specifications
4. **004_add_checklist_dependencies** - Task dependency tracking
5. **005_add_audit_logs** - Audit trail system

### Creating New Migrations

1. Add migration method to `DatabaseMigrator` class:
```python
async def migration_006_your_migration_name(self):
    """Description of your migration"""
    # Migration code here
    pass
```

2. Add migration name to the migrations list:
```python
migrations = [
    # ... existing migrations
    "006_your_migration_name"
]
```

## Troubleshooting

### Common Issues

#### Connection Errors

**Problem:** `pymongo.errors.ServerSelectionTimeoutError`
**Solutions:**
- Verify MongoDB is running locally: `brew services list | grep mongodb`
- Check connection string format
- Ensure network access is configured (Atlas)
- Verify credentials are correct

#### Authentication Errors

**Problem:** `pymongo.errors.OperationFailure: Authentication failed`
**Solutions:**
- Verify username and password in connection string
- Check user permissions in Atlas dashboard
- Ensure database user has correct privileges

#### SSL/TLS Errors (Atlas)

**Problem:** SSL certificate verification failed
**Solutions:**
- Install required packages: `pip install pymongo[srv] dnspython`
- Use full connection string with SSL parameters
- Update to latest version of pymongo

### Database Maintenance

#### Backup Database
```bash
# Local MongoDB
mongodump --db smart_lab_shutdown --out ./backup

# Atlas (using mongodump with connection string)
mongodump --uri "mongodb+srv://..." --db smart_lab_shutdown --out ./backup
```

#### Restore Database
```bash
# Local MongoDB
mongorestore --db smart_lab_shutdown ./backup/smart_lab_shutdown

# Atlas
mongorestore --uri "mongodb+srv://..." --db smart_lab_shutdown ./backup/smart_lab_shutdown
```

#### Check Database Statistics
```python
# Connect to database and run
python -c "
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

async def stats():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE_NAME]
    stats = await db.command('dbStats')
    print(f'Database: {stats[\"db\"]}')
    print(f'Collections: {stats[\"collections\"]}')
    print(f'Data Size: {stats[\"dataSize\"]} bytes')
    print(f'Index Size: {stats[\"indexSize\"]} bytes')
    client.close()

asyncio.run(stats())
"
```

### Performance Optimization

#### Index Usage Analysis
```javascript
// In MongoDB shell
db.shutdown_logs.explain("executionStats").find({"deviceId": "SRV-001"})
```

#### Query Performance Tips
1. Use compound indexes for multi-field queries
2. Limit result sets with `.limit()`
3. Use projection to fetch only needed fields
4. Consider using aggregation pipelines for complex queries

### Security Best Practices

1. **Authentication:**
   - Use strong passwords
   - Enable authentication in production
   - Use connection string authentication

2. **Network Security:**
   - Restrict IP access in Atlas
   - Use SSL/TLS connections
   - Configure firewall rules

3. **Database Security:**
   - Grant minimal required privileges
   - Regularly update MongoDB version
   - Monitor access logs

4. **Application Security:**
   - Validate all inputs
   - Use parameterized queries
   - Implement rate limiting
   - Log security events

For additional help, consult the [MongoDB Documentation](https://docs.mongodb.com/) or contact the development team.