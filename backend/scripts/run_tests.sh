#!/bin/bash

# Smart Lab Power Shutdown Assistant - Backend Test Runner
# This script runs the complete test suite with coverage reporting

set -e  # Exit on any error

echo "🧪 Smart Lab Power Shutdown Assistant - Backend Test Suite"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

cd "$BACKEND_DIR"

echo -e "${BLUE}📍 Working directory: $BACKEND_DIR${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
source venv/bin/activate

# Install test dependencies
echo -e "${BLUE}📦 Installing test dependencies...${NC}"
pip install -r requirements-test.txt > /dev/null 2>&1

# Check if MongoDB is running
echo -e "${BLUE}🔍 Checking MongoDB connection...${NC}"
if ! python -c "
import pymongo
try:
    client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=1000)
    client.server_info()
    print('✅ MongoDB is running')
except:
    print('❌ MongoDB is not running. Please start MongoDB first.')
    exit(1)
" 2>/dev/null; then
    echo -e "${RED}❌ MongoDB connection failed. Please ensure MongoDB is running.${NC}"
    echo -e "${YELLOW}💡 To start MongoDB:${NC}"
    echo -e "   macOS: brew services start mongodb-community"
    echo -e "   Ubuntu: sudo systemctl start mongod"
    echo -e "   Windows: net start MongoDB"
    exit 1
fi

# Parse command line arguments
VERBOSE=false
COVERAGE=true
PARALLEL=false
SPECIFIC_TEST=""
MARKERS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-coverage)
            COVERAGE=false
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -t|--test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        -m|--markers)
            MARKERS="-m $2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose       Run tests in verbose mode"
            echo "  --no-coverage       Skip coverage reporting"
            echo "  -p, --parallel      Run tests in parallel"
            echo "  -t, --test FILE     Run specific test file"
            echo "  -m, --markers EXPR  Run tests matching marker expression"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                          # Run all tests with coverage"
            echo "  $0 -v                       # Run tests in verbose mode"
            echo "  $0 -t test_auth.py         # Run specific test file"
            echo "  $0 -m \"not slow\"           # Skip slow tests"
            echo "  $0 -p --no-coverage        # Run in parallel without coverage"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Build pytest command
PYTEST_CMD="pytest"

if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
fi

if [ "$COVERAGE" = true ] && [ "$PARALLEL" = false ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=80"
fi

if [ -n "$SPECIFIC_TEST" ]; then
    PYTEST_CMD="$PYTEST_CMD tests/$SPECIFIC_TEST"
fi

if [ -n "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD $MARKERS"
fi

echo -e "${BLUE}🚀 Running tests...${NC}"
echo -e "${BLUE}Command: $PYTEST_CMD${NC}"
echo ""

# Run tests
if eval $PYTEST_CMD; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    
    if [ "$COVERAGE" = true ] && [ "$PARALLEL" = false ]; then
        echo -e "${GREEN}📊 Coverage report generated in htmlcov/index.html${NC}"
    fi
    
    # Run additional checks
    echo ""
    echo -e "${BLUE}🔍 Running additional code quality checks...${NC}"
    
    # Check for security issues (if bandit is installed)
    if command -v bandit &> /dev/null; then
        echo -e "${BLUE}🔒 Security check with bandit...${NC}"
        bandit -r src/ -f json -o security-report.json || echo -e "${YELLOW}⚠️  Security issues found. Check security-report.json${NC}"
    fi
    
    # Check code style (if flake8 is installed)
    if command -v flake8 &> /dev/null; then
        echo -e "${BLUE}📏 Code style check with flake8...${NC}"
        flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503 || echo -e "${YELLOW}⚠️  Code style issues found${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 Test suite completed successfully!${NC}"
    
else
    echo ""
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo -e "${YELLOW}💡 Tips for debugging:${NC}"
    echo -e "   - Run with -v for verbose output"
    echo -e "   - Run specific test file with -t test_file.py"
    echo -e "   - Check test database connection"
    echo -e "   - Ensure all dependencies are installed"
    exit 1
fi

# Cleanup
echo -e "${BLUE}🧹 Cleaning up test artifacts...${NC}"
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo -e "${GREEN}✨ Done!${NC}"