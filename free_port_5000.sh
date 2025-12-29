#!/bin/bash
# Script to free port 5000

echo "Checking for processes using port 5000..."

# Try to find and kill processes using port 5000
if command -v lsof &> /dev/null; then
    PIDS=$(sudo lsof -ti :5000 2>/dev/null)
    if [ ! -z "$PIDS" ]; then
        echo "Found processes using port 5000: $PIDS"
        echo "Killing processes..."
        sudo kill -9 $PIDS
        sleep 1
        echo "Processes killed."
    else
        echo "No processes found with lsof."
    fi
fi

# Also check for Python Flask processes
PYTHON_PIDS=$(pgrep -f "python.*main\.py|flask run|gunicorn.*5000")
if [ ! -z "$PYTHON_PIDS" ]; then
    echo "Found Python processes that might be using port 5000: $PYTHON_PIDS"
    echo "Killing Python processes..."
    kill -9 $PYTHON_PIDS 2>/dev/null
    sleep 1
    echo "Python processes killed."
fi

# Verify port is free
echo ""
echo "Verifying port 5000 is free..."
if python3 -c "import socket; s = socket.socket(); result = s.connect_ex(('localhost', 5000)); s.close(); exit(0 if result != 0 else 1)" 2>/dev/null; then
    echo "✓ Port 5000 is now free!"
else
    echo "⚠ Port 5000 may still be in use or in TIME_WAIT state."
    echo "   If it's in TIME_WAIT, wait a few seconds and try again."
    echo "   Or try: sudo sysctl -w net.ipv4.tcp_tw_reuse=1"
fi


