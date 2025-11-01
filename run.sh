#!/bin/bash

echo "========================================"
echo "Point and Figure Chart - MT5"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Python found!"
echo ""

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

echo "Dependencies OK!"
echo ""

# Start the application
echo "Starting application..."
echo "Web interface will be available at:"
echo "  - http://localhost:8000"
echo "  - http://127.0.0.1:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 main.py
