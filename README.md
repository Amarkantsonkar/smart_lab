# Smart Lab Power Shutdown Assistant

A comprehensive full-stack web application for managing lab power shutdown procedures with role-based authentication, maintenance checklists, and automated shutdown capabilities.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Frontend Components](#frontend-components)
- [Database Schema](#database-schema)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Smart Lab Power Shutdown Assistant addresses critical issues in server labs where systems need to be powered down safely and efficiently after maintenance. The application provides:

- **Role-based authentication** with Engineer and Admin roles
- **Digital maintenance checklist** that enforces critical task completion
- **Automated shutdown simulation** with comprehensive logging
- **Real-time dashboard** showing lab system power states
- **Advanced reporting** with CSV/PDF export capabilities
- **Real-time notifications** for system status updates

## ✨ Features

### Core Functionality
- 🔐 **JWT-based Authentication** with role-based access control
- ✅ **Smart Checklist System** preventing shutdown until critical tasks are complete
- 🔌 **Device Management** with real-time status monitoring
- 📊 **Comprehensive Dashboard** with system health indicators
- 📈 **Advanced Reporting** with filtering and export options
- 🔔 **Real-time Notifications** for important system events

### Technical Features
- 🏗️ **RESTful API** with comprehensive error handling
- 🔄 **Real-time Updates** using custom event system
- 📱 **Responsive Design** optimized for mobile and desktop
- 🐳 **Docker Support** for easy deployment
- 🛡️ **Security Best Practices** with CORS and security headers
- 📈 **Database Optimization** with proper indexing and migrations

## 🛠 Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.11+** - Programming language
- **Motor** - Async MongoDB driver
- **JWT** - JSON Web Tokens for authentication
- **Pydantic** - Data validation and settings management
- **pytest** - Testing framework

### Frontend
- **React.js 18+** - User interface framework
- **Vite** - Build tool and development server
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API communication
- **Jest & React Testing Library** - Testing frameworks

### Database
- **MongoDB Atlas** - Cloud database service
- **Motor** - Async MongoDB driver for Python

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container application management
- **Nginx** - Web server and reverse proxy

## 📋 Prerequisites

Before installing the application, ensure you have:

- **Node.js** (v18.0.0 or higher)
- **Python** (v3.11.0 or higher)
- **Docker** and **Docker Compose** (for containerized deployment)
- **MongoDB Atlas Account** (or local MongoDB instance)
- **Git** for version control

## 🚀 Installation

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-lab-power-shutdown-assistant
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your configuration
   nano .env
   ```

5. **Database Setup**
   ```bash
   cd backend
   python scripts/setup_mongodb.py
   ```

6. **Start Development Servers**
   
   Terminal 1 (Backend):
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```

### Docker Deployment

1. **Quick Start**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Configure your environment variables
   nano .env
   
   # Deploy using the automated script
   ./deploy.sh
   ```

2. **Manual Docker Commands**
   ```bash
   # Build and start services
   docker-compose up --build -d
   
   # View logs
   docker-compose logs -f
   
   # Stop services
   docker-compose down
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# MongoDB Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/smart_lab_db

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
PROJECT_NAME=Smart Lab Power Shutdown Assistant
DEBUG=true

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
```

### MongoDB Atlas Setup

1. **Create MongoDB Atlas Account**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a free account
   - Create a new cluster

2. **Configure Database Access**
   - Create a database user with read/write permissions
   - Add your IP address to the IP whitelist
   - Get your connection string

3. **Database Configuration**
   - Replace `MONGODB_URL` in your `.env` file
   - Run the setup script: `python backend/scripts/setup_mongodb.py`

## 🌐 Deployment

### Production Deployment

1. **Prepare Production Environment**
   ```bash
   cp .env.production .env
   # Edit with production values
   ```

2. **Deploy with Docker**
   ```bash
   ./deploy.sh production
   ```

3. **Verify Deployment**
   - Frontend: http://your-domain.com
   - Backend API: http://your-domain.com/api
   - API Docs: http://your-domain.com/docs

### Cloud Deployment Options

- **AWS**: Use ECS with Fargate for containerized deployment
- **Google Cloud**: Deploy to Cloud Run or GKE
- **Azure**: Use Container Instances or AKS
- **DigitalOcean**: Deploy to App Platform or Droplets
- **Heroku**: Use container registry for deployment

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/register` | User registration |
| GET | `/api/v1/auth/me` | Get current user |

### Device Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/devices` | List all devices |
| POST | `/api/v1/devices` | Create new device |
| GET | `/api/v1/devices/{id}` | Get device by ID |
| PUT | `/api/v1/devices/{id}` | Update device |
| DELETE | `/api/v1/devices/{id}` | Delete device |

### Checklist Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/checklist` | Get checklist items |
| POST | `/api/v1/checklist` | Create checklist item |
| PUT | `/api/v1/checklist/{id}` | Update checklist item |
| DELETE | `/api/v1/checklist/{id}` | Delete checklist item |

### Shutdown Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/shutdown/device/{id}` | Shutdown single device |
| POST | `/api/v1/shutdown/bulk` | Bulk shutdown devices |
| GET | `/api/v1/shutdown/status` | Get shutdown status |

### Reporting

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/shutdown-logs` | Get shutdown logs |
| GET | `/api/v1/reports/export` | Export reports |

For detailed API documentation, visit `/docs` when the backend is running.

## 🎨 Frontend Components

### Core Components

- **`App.jsx`** - Main application component with routing
- **`Layout.jsx`** - Common layout wrapper with navigation
- **`Login.jsx`** - Authentication interface
- **`Dashboard.jsx`** - Real-time system overview
- **`Checklist.jsx`** - Maintenance checklist interface
- **`ShutdownControl.jsx`** - Device shutdown management
- **`Reports.jsx`** - Advanced reporting and analytics

### Hooks and Services

- **`useAuth.js`** - Authentication state management
- **`api.js`** - HTTP client configuration
- **`notifications.js`** - Toast notification system

### Key Features

- **Responsive Design** - Optimized for all screen sizes
- **Real-time Updates** - Live data synchronization
- **Form Validation** - Client-side input validation
- **Error Handling** - Comprehensive error management
- **Accessibility** - WCAG compliant interfaces

## 🗄️ Database Schema

### Collections

#### Users
```javascript
{
  _id: ObjectId,
  username: String,
  email: String,
  passwordHash: String,
  role: String, // "engineer" | "admin"
  createdAt: Date,
  updatedAt: Date
}
```

#### Devices
```javascript
{
  _id: ObjectId,
  name: String,
  type: String,
  location: String,
  status: String, // "on" | "off" | "maintenance"
  assignedUser: ObjectId,
  createdAt: Date,
  updatedAt: Date
}
```

#### Checklist Items
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  isCritical: Boolean,
  completed: Boolean,
  completedBy: ObjectId,
  completedAt: Date,
  createdAt: Date,
  updatedAt: Date
}
```

#### Shutdown Logs
```javascript
{
  _id: ObjectId,
  deviceId: ObjectId,
  userId: ObjectId,
  status: String, // "success" | "failed"
  timestamp: Date,
  duration: Number,
  reason: String,
  errorMessage: String
}
```

## 🔒 Security

### Authentication & Authorization
- JWT-based authentication with secure token handling
- Role-based access control (Engineer/Admin)
- Password hashing using bcrypt
- Token expiration and refresh mechanisms

### API Security
- CORS configuration for cross-origin requests
- Request rate limiting
- Input validation and sanitization
- SQL injection prevention through ODM

### Frontend Security
- XSS protection through React's built-in escaping
- CSRF protection for state-changing operations
- Secure token storage in localStorage
- Content Security Policy headers

### Deployment Security
- HTTPS enforcement in production
- Security headers (X-Frame-Options, X-XSS-Protection)
- Docker security best practices
- Environment variable protection

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v --cov=src
```

### Frontend Testing
```bash
cd frontend
npm test
npm run test:coverage
```

### End-to-End Testing
```bash
# Install Playwright
npm install -g @playwright/test

# Run E2E tests
npx playwright test
```

## 📈 Performance

### Frontend Optimization
- Code splitting with React lazy loading
- Image optimization and compression
- Bundle size analysis with webpack-bundle-analyzer
- Service worker for caching (optional)

### Backend Optimization
- Database indexing for frequently queried fields
- Connection pooling for database operations
- Async/await for non-blocking operations
- Response caching for read-heavy endpoints

### Database Optimization
- Compound indexes for complex queries
- TTL indexes for temporary data
- Aggregation pipelines for analytics
- Connection optimization

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript code
- Write tests for new features
- Update documentation for API changes
- Follow conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- 📧 Email: support@smartlab.com
- 📝 Issues: Create an issue on GitHub
- 📖 Documentation: Check the `/docs` endpoint
- 💬 Discussions: Use GitHub Discussions

## 🎯 Roadmap

### Upcoming Features
- [ ] Mobile app using React Native
- [ ] Advanced analytics and reporting
- [ ] Integration with external monitoring tools
- [ ] Automated backup and recovery
- [ ] Multi-language support
- [ ] Advanced user management

### Known Issues
- See GitHub Issues for current known issues
- Check the changelog for recent fixes

---


