"""Main entry point for the virtual camera server application."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.web import create_app
from src.services.logger import setup_logging

# Setup logging
setup_logging()

if __name__ == "__main__":
    app = create_app()
    
    print("=" * 60)
    print("Virtual Camera Server - Web Interface")
    print("=" * 60)
    print("\nStarting web server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

