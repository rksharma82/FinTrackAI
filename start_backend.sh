#!/bin/bash

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "WARNING: .env file not found. Please create it with your GEMINI_API_KEY"
    echo "You can copy from .env.example if available"
fi

# Start the backend server
echo "Starting backend server on http://0.0.0.0:8000"
uvicorn main:app --reload --host 0.0.0.0 --port 8000

