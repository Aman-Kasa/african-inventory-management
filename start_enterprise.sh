#!/bin/bash

# ===== IPMS Enterprise Startup Script =====
# This script sets up and starts the IPMS Enterprise application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}  IPMS Enterprise Startup${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1

    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Function to check prerequisites
check_prerequisites() {
    print_header
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.10 or higher."
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Python $python_version found"
    
    # Check pip
    if ! command_exists pip3; then
        print_error "pip3 is not installed. Please install pip."
        exit 1
    fi
    
    # Check PostgreSQL
    if ! command_exists psql; then
        print_warning "PostgreSQL client not found. You may need to install it for database operations."
    else
        print_success "PostgreSQL client found"
    fi
    
    # Check Redis
    if ! command_exists redis-cli; then
        print_warning "Redis client not found. You may need to install it for caching."
    else
        print_success "Redis client found"
    fi
    
    print_success "Prerequisites check completed"
}

# Function to setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_warning "Please edit .env file with your configuration before starting the application."
        else
            print_error "env.example file not found. Please create a .env file manually."
        fi
    fi
    
    # Check database connection
    print_status "Checking database connection..."
    if command_exists psql; then
        # Try to connect to database (this will fail if database doesn't exist, which is expected)
        python3 -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://ipms_user:ipms_password@localhost:5432/ipms_db'))
    engine.connect()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    print('This is expected if the database is not set up yet.')
"
    fi
    
    cd ..
    print_success "Backend setup completed"
}

# Function to start backend
start_backend() {
    print_status "Starting backend server..."
    
    cd backend
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if backend is already running
    if port_in_use 5000; then
        print_warning "Backend is already running on port 5000"
        return 0
    fi
    
    # Start backend in background
    print_status "Starting Flask application..."
    nohup python3 app.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    if wait_for_service localhost 5000 "Backend"; then
        print_success "Backend started successfully (PID: $BACKEND_PID)"
        echo $BACKEND_PID > ../logs/backend.pid
    else
        print_error "Failed to start backend"
        exit 1
    fi
    
    cd ..
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend server..."
    
    cd frontend
    
    # Check if frontend is already running
    if port_in_use 8000; then
        print_warning "Frontend is already running on port 8000"
        return 0
    fi
    
    # Start frontend in background
    print_status "Starting HTTP server..."
    nohup python3 -m http.server 8000 > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    if wait_for_service localhost 8000 "Frontend"; then
        print_success "Frontend started successfully (PID: $FRONTEND_PID)"
        echo $FRONTEND_PID > ../logs/frontend.pid
    else
        print_error "Failed to start frontend"
        exit 1
    fi
    
    cd ..
}

# Function to create logs directory
create_logs_directory() {
    if [ ! -d "logs" ]; then
        mkdir -p logs
        print_success "Created logs directory"
    fi
}

# Function to show application status
show_status() {
    print_header
    print_status "Application Status:"
    
    if port_in_use 5000; then
        print_success "Backend: Running on http://localhost:5000"
    else
        print_error "Backend: Not running"
    fi
    
    if port_in_use 8000; then
        print_success "Frontend: Running on http://localhost:8000"
    else
        print_error "Frontend: Not running"
    fi
    
    echo ""
    print_status "Access the application at: http://localhost:8000"
    print_status "API Documentation: http://localhost:5000/api/docs"
    print_status "Health Check: http://localhost:5000/api/health"
}

# Function to stop application
stop_application() {
    print_status "Stopping IPMS Enterprise..."
    
    # Stop backend
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            print_status "Stopping backend (PID: $BACKEND_PID)..."
            kill $BACKEND_PID
            rm logs/backend.pid
            print_success "Backend stopped"
        fi
    fi
    
    # Stop frontend
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_status "Stopping frontend (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
            rm logs/frontend.pid
            print_success "Frontend stopped"
        fi
    fi
    
    print_success "IPMS Enterprise stopped"
}

# Function to show logs
show_logs() {
    local service=$1
    
    case $service in
        "backend")
            if [ -f "logs/backend.log" ]; then
                tail -f logs/backend.log
            else
                print_error "Backend log file not found"
            fi
            ;;
        "frontend")
            if [ -f "logs/frontend.log" ]; then
                tail -f logs/frontend.log
            else
                print_error "Frontend log file not found"
            fi
            ;;
        *)
            print_error "Invalid service. Use 'backend' or 'frontend'"
            ;;
    esac
}

# Function to show help
show_help() {
    echo "IPMS Enterprise Startup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start the application (default)"
    echo "  stop      Stop the application"
    echo "  restart   Restart the application"
    echo "  status    Show application status"
    echo "  setup     Setup the application (install dependencies)"
    echo "  logs      Show application logs"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 stop"
    echo "  $0 logs backend"
    echo "  $0 status"
}

# Main script logic
case "${1:-start}" in
    "start")
        check_prerequisites
        create_logs_directory
        setup_backend
        start_backend
        start_frontend
        show_status
        ;;
    "stop")
        stop_application
        ;;
    "restart")
        stop_application
        sleep 2
        check_prerequisites
        create_logs_directory
        setup_backend
        start_backend
        start_frontend
        show_status
        ;;
    "status")
        show_status
        ;;
    "setup")
        check_prerequisites
        create_logs_directory
        setup_backend
        print_success "Setup completed successfully"
        ;;
    "logs")
        show_logs $2
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 