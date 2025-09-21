# Setup Instructions

## Prerequisites

Before setting up the Smart Lab Power Shutdown Assistant, ensure you have the following installed:

### Required Software
- **Node.js** (v18.0.0 or higher)
  - Download from [nodejs.org](https://nodejs.org/)
  - Verify installation: `node --version`

- **Python** (v3.11.0 or higher)
  - Download from [python.org](https://www.python.org/)
  - Verify installation: `python --version`

- **Git** (latest version)
  - Download from [git-scm.com](https://git-scm.com/)
  - Verify installation: `git --version`

### Optional (for containerized deployment)
- **Docker** (v20.0.0 or higher)
  - Download from [docker.com](https://www.docker.com/)
  - Verify installation: `docker --version`

- **Docker Compose** (v2.0.0 or higher)
  - Usually included with Docker Desktop
  - Verify installation: `docker-compose --version`

## MongoDB Atlas Setup

### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Click "Try Free" to create an account
3. Complete the registration process

### Step 2: Create a Cluster
1. After logging in, click "Build a Database"
2. Choose "Shared" (free tier) for development
3. Select your cloud provider and region
4. Choose "M0 Sandbox" (free tier)
5. Name your cluster (e.g., "smart-lab-cluster")
6. Click "Create Cluster"

### Step 3: Configure Database Access
1. Go to "Database Access" in the left sidebar
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Create a username and secure password
5. Set built-in role to "Read and write to any database"
6. Click "Add User"

### Step 4: Configure Network Access
1. Go to "Network Access" in the left sidebar
2. Click "Add IP Address"
3. For development, click "Allow Access from Anywhere" (0.0.0.0/0)
4. For production, add your specific IP addresses
5. Click "Confirm"

### Step 5: Get Connection String
1. Go to "Database" in the left sidebar
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Select "Python" as driver and "3.6 or later" as version
5. Copy the connection string
6. Replace `<password>` with your database user password
7. Replace `<dbname>` with your database name (e.g., "smart_lab_db")

Example connection string:
```
mongodb+srv://username:password@cluster.mongodb.net/smart_lab_db?retryWrites=true&w=majority
```

## Local Development Setup

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd smart-lab-power-shutdown-assistant
```

### Step 2: Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Verify installation**
   ```bash
   pip list
   ```

### Step 3: Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Verify installation**
   ```bash
   npm list
   ```

### Step 4: Environment Configuration

1. **Copy environment template**
   ```bash
   cd ..  # Return to root directory
   cp .env.example .env
   ```

2. **Edit environment file**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Configure required variables**
   ```bash
   # MongoDB Configuration
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/smart_lab_db?retryWrites=true&w=majority
   
   # JWT Configuration (generate a secure secret key)
   SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Application Configuration
   PROJECT_NAME=Smart Lab Power Shutdown Assistant
   DEBUG=true
   
   # Frontend Configuration
   VITE_API_BASE_URL=http://localhost:8000
   ```

### Step 5: Database Initialization

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Activate virtual environment** (if not already active)
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Run database setup script**
   ```bash
   python scripts/setup_mongodb.py
   ```

4. **Verify database setup**
   - Check MongoDB Atlas dashboard
   - You should see your database and collections created

### Step 6: Start Development Servers

1. **Start Backend Server**
   
   Open a new terminal and run:
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Backend will be available at: http://localhost:8000

2. **Start Frontend Server**
   
   Open another terminal and run:
   ```bash
   cd frontend
   npm run dev
   ```
   
   Frontend will be available at: http://localhost:5173

### Step 7: Verify Installation

1. **Check Backend Health**
   ```bash
   curl http://localhost:8000/health
   ```
   
   Should return:
   ```json
   {
     "status": "healthy",
     "timestamp": "2023-XX-XXTXX:XX:XX.XXXXXX",
     "database": "connected"
   }
   ```

2. **Check API Documentation**
   Visit: http://localhost:8000/docs

3. **Check Frontend**
   Visit: http://localhost:5173

## Docker Setup (Alternative)

### Step 1: Prepare Environment
```bash
# Copy environment file
cp .env.example .env

# Edit with your MongoDB Atlas connection string
nano .env
```

### Step 2: Build and Run with Docker Compose
```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Step 3: Verify Docker Deployment
```bash
# Check running containers
docker-compose ps

# Check logs
docker-compose logs -f

# Check health
curl http://localhost:80/health
curl http://localhost:8000/health
```

## Production Setup

### Step 1: Prepare Production Environment
```bash
# Copy production environment template
cp .env.production .env

# Edit with production values
nano .env
```

### Step 2: Configure Production MongoDB Atlas
1. Create a separate production cluster
2. Configure production database user
3. Restrict network access to production IPs
4. Update connection string in `.env`

### Step 3: Deploy to Production
```bash
# Deploy with production configuration
./deploy.sh production
```

### Step 4: Configure Domain and SSL
1. Point your domain to the server IP
2. Configure SSL certificate (Let's Encrypt recommended)
3. Update CORS origins in environment variables

## Troubleshooting

### Common Issues

#### Backend Won't Start
- **Issue**: Module not found errors
- **Solution**: Ensure virtual environment is activated and dependencies are installed
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  ```

#### Database Connection Failed
- **Issue**: Cannot connect to MongoDB Atlas
- **Solutions**:
  1. Check connection string format
  2. Verify database user credentials
  3. Ensure IP is whitelisted
  4. Check network connectivity

#### Frontend Build Errors
- **Issue**: npm install or npm run dev fails
- **Solutions**:
  1. Clear npm cache: `npm cache clean --force`
  2. Delete node_modules: `rm -rf node_modules && npm install`
  3. Check Node.js version compatibility

#### CORS Errors
- **Issue**: Frontend cannot connect to backend
- **Solution**: Verify CORS origins in backend configuration
  ```python
  # In main.py
  allow_origins=[
      "http://localhost:3000",
      "http://localhost:5173",
      # Add your frontend URL
  ]
  ```

#### Docker Issues
- **Issue**: Container build failures
- **Solutions**:
  1. Check Docker daemon is running
  2. Verify Dockerfile syntax
  3. Check available disk space
  4. Clear Docker cache: `docker system prune`

### Environment Variables Checklist

Ensure all required environment variables are set:

- [ ] `MONGODB_URL` - Valid MongoDB Atlas connection string
- [ ] `SECRET_KEY` - Secure random string (min 32 characters)
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- [ ] `PROJECT_NAME` - Application name
- [ ] `DEBUG` - Development/production flag
- [ ] `VITE_API_BASE_URL` - Backend API URL

### Performance Optimization

#### Development
- Use `--reload` flag for FastAPI auto-reload
- Enable React development tools
- Use browser dev tools for debugging

#### Production
- Set `DEBUG=false`
- Use production-optimized builds
- Configure proper logging levels
- Set up monitoring and alerting

### Security Checklist

- [ ] Use strong, unique SECRET_KEY
- [ ] Configure proper MongoDB Atlas access controls
- [ ] Set up network security (firewall rules)
- [ ] Use HTTPS in production
- [ ] Regularly update dependencies
- [ ] Monitor for security vulnerabilities

## Getting Help

If you encounter issues during setup:

1. **Check logs** for error messages
2. **Verify prerequisites** are correctly installed
3. **Review environment variables** for typos
4. **Consult troubleshooting section** above
5. **Create an issue** on GitHub with:
   - Operating system and version
   - Node.js and Python versions
   - Complete error messages
   - Steps to reproduce the issue

## Next Steps

After successful setup:

1. **Create admin user** through the registration endpoint
2. **Add initial devices** to the system
3. **Configure checklist items** for your lab procedures
4. **Test shutdown procedures** in a safe environment
5. **Set up monitoring** and alerting for production use

Congratulations! Your Smart Lab Power Shutdown Assistant is now ready to use. 🎉