#!/bin/bash

# Social Content Platform Console Setup Script

set -e

echo "========================================="
echo "Social Content Platform Console Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Setup Backend
echo ""
echo "Setting up Backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install requirements
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Backend setup complete!"
cd ..

# Setup Frontend
echo ""
echo "Setting up Frontend..."
cd frontend

# Install npm dependencies
echo "Installing Node dependencies..."
npm install

echo "Frontend setup complete!"
cd ..

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To run the application:"
echo ""
echo "1. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate  # or venv\Scripts\activate on Windows"
echo "   python main.py"
echo ""
echo "2. In another terminal, start the frontend:"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "The frontend will be available at http://localhost:3000"
echo "The backend will be available at http://localhost:8000"
echo ""
