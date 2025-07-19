#!/bin/bash

# Inventory & Procurement Management System - Backend Startup Script

echo "=== Inventory & Procurement Management System ==="
echo "Starting Backend Server..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "Error: Please run this script from the project root directory."
    echo "Expected to find: backend/app.py"
    exit 1
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "Please edit .env file with your configuration before continuing."
    echo "Press Enter to continue or Ctrl+C to exit..."
    read
fi

# Check if PostgreSQL is running
echo "Checking database connection..."
if ! python3 -c "import psycopg2; psycopg2.connect('postgresql://ipms_user:ipms_password@localhost:5432/ipms_db')" 2>/dev/null; then
    echo "Warning: Database connection failed. Please ensure PostgreSQL is running and configured."
    echo "You can run: python3 setup_database.py to set up the database."
    echo "Press Enter to continue anyway or Ctrl+C to exit..."
    read
fi

# Start the Flask application
echo "Starting Flask application..."
echo "Server will be available at: http://localhost:5000"
echo "API documentation: http://localhost:5000/api/health"
echo ""
echo "Default admin credentials:"
echo "Email: admin@ipms.com"
echo "Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py 