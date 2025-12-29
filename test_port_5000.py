#!/usr/bin/env python3
"""Test if port 5000 can be bound."""
import socket
import sys

def test_port(port):
    """Test if we can bind to the specified port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        s.bind(('0.0.0.0', port))
        s.close()
        print(f"✓ Port {port} is FREE - can bind successfully!")
        return True
    except OSError as e:
        print(f"✗ Port {port} is BLOCKED - cannot bind: {e}")
        return False

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    success = test_port(port)
    sys.exit(0 if success else 1)


