#!/bin/bash
# Quick script to kill whatever is using port 5000

echo "Finding process using port 5000..."

# Find PID using port 5000
PID=$(sudo lsof -ti :5000 2>/dev/null)

if [ -z "$PID" ]; then
    echo "No process found using port 5000 with lsof."
    echo "Trying alternative methods..."
    
    # Try with fuser
    PID=$(sudo fuser 5000/tcp 2>/dev/null | awk '{print $1}')
    
    if [ -z "$PID" ]; then
        echo "Could not find process using port 5000."
        echo "The port might be in TIME_WAIT state. Try waiting 60 seconds."
        exit 1
    fi
fi

echo "Found process(es) using port 5000: $PID"
echo "Process details:"
ps -p $PID -o pid,cmd,etime 2>/dev/null || echo "Process details not available"

echo ""
read -p "Kill process(es) $PID? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo kill -9 $PID
    sleep 1
    
    # Verify
    if python3 test_port_5000.py 2>/dev/null; then
        echo "✓ Port 5000 is now free!"
    else
        echo "⚠ Port 5000 may still be in use. Wait a few seconds and try again."
    fi
else
    echo "Cancelled."
fi


