#!/usr/bin/env python3
"""
Dependency Installation Script for Virtual Camera Server

This script automates the installation of all system and Python dependencies
required for the Virtual Camera Server application.

Usage:
    python3 install_dependencies.py

The script will:
1. Detect your operating system
2. Install system dependencies (GStreamer, etc.)
3. Create a virtual environment (if needed)
4. Install Python dependencies
5. Verify the installation
"""

import sys
import os
import subprocess
import platform
import shutil
from pathlib import Path

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Print an info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def run_command(cmd, check=True, shell=False, sudo=False):
    """Run a shell command and return the result."""
    if sudo and platform.system() != "Windows":
        cmd = ["sudo"] + (cmd if isinstance(cmd, list) else cmd.split())
    
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        
        result = subprocess.run(
            cmd,
            check=check,
            shell=shell,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr
    except FileNotFoundError:
        return False, "", "Command not found"

def check_command_exists(cmd):
    """Check if a command exists in PATH."""
    return shutil.which(cmd) is not None

def check_python_version():
    """Check if Python version is 3.11 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print_error(f"Python 3.11+ required. Found Python {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_linux_dependencies():
    """Install system dependencies on Linux (Ubuntu/Debian)."""
    print_header("Installing Linux System Dependencies")
    
    packages = [
        "python3-pip",
        "python3-venv",
        "python3-dev",
        "python3-tk",
        "pkg-config",
        "python3-gi",
        "python3-gi-cairo",
        "gir1.2-gstreamer-1.0",
        "gir1.2-gst-rtsp-server-1.0",
        "libcairo2-dev",
        "libgirepository1.0-dev",
        "libgirepository-2.0-dev",
        "gobject-introspection",
        "gstreamer1.0-tools",
        "gstreamer1.0-plugins-base",
        "gstreamer1.0-plugins-good",
        "gstreamer1.0-plugins-bad",
        "libgstreamer1.0-dev",
        "libgstrtspserver-1.0-dev"
    ]
    
    print_info("Updating package list...")
    success, _, _ = run_command(["apt-get", "update"], sudo=True)
    if not success:
        print_error("Failed to update package list")
        return False
    
    print_info(f"Installing {len(packages)} packages (this may take a few minutes)...")
    cmd = ["apt-get", "install", "-y"] + packages
    success, stdout, stderr = run_command(cmd, sudo=True)
    
    if success:
        print_success("All system packages installed successfully")
        return True
    else:
        print_error(f"Failed to install packages: {stderr}")
        return False

def install_macos_dependencies():
    """Install system dependencies on macOS using Homebrew."""
    print_header("Installing macOS System Dependencies")
    
    if not check_command_exists("brew"):
        print_error("Homebrew not found. Please install Homebrew first:")
        print_info("Visit: https://brew.sh")
        return False
    
    print_success("Homebrew detected")
    
    packages = [
        "python@3.11",
        "pkg-config",
        "cairo",
        "gobject-introspection",
        "gstreamer",
        "gst-plugins-base",
        "gst-plugins-good",
        "gst-plugins-bad",
        "gst-rtsp-server"
    ]
    
    print_info(f"Installing {len(packages)} packages via Homebrew (this may take a while)...")
    
    for package in packages:
        print_info(f"Installing {package}...")
        success, _, stderr = run_command(["brew", "install", package])
        if not success:
            print_warning(f"Failed to install {package}: {stderr}")
            print_info("Continuing with other packages...")
    
    print_success("System packages installation completed")
    return True

def install_windows_dependencies():
    """Provide instructions for Windows dependencies."""
    print_header("Windows System Dependencies")
    
    print_warning("Windows requires manual installation of GStreamer")
    print_info("Please follow these steps:")
    print("1. Download GStreamer from: https://gstreamer.freedesktop.org/download/")
    print("2. Choose 'Complete' installation")
    print("3. Install GStreamer runtime")
    print("4. Add GStreamer to PATH:")
    print("   - Default: C:\\gstreamer\\1.0\\msvc_x86_64\\bin")
    print("   - Add to System Environment Variables → Path")
    print("\n5. Verify installation:")
    print("   gst-launch-1.0 --version")
    
    response = input("\nHave you installed GStreamer? (y/n): ").strip().lower()
    if response != 'y':
        print_warning("Please install GStreamer and run this script again")
        return False
    
    # Verify GStreamer
    if check_command_exists("gst-launch-1.0"):
        print_success("GStreamer detected in PATH")
        return True
    else:
        print_error("GStreamer not found in PATH. Please add it to PATH and try again.")
        return False

def create_venv():
    """Create a virtual environment if it doesn't exist."""
    print_header("Setting Up Virtual Environment")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_info("Virtual environment already exists")
        response = input("Recreate virtual environment? (y/n): ").strip().lower()
        if response == 'y':
            print_info("Removing existing virtual environment...")
            shutil.rmtree(venv_path)
        else:
            print_success("Using existing virtual environment")
            return True
    
    print_info("Creating virtual environment...")
    success, _, stderr = run_command([sys.executable, "-m", "venv", "venv"])
    
    if success:
        print_success("Virtual environment created")
        return True
    else:
        print_error(f"Failed to create virtual environment: {stderr}")
        return False

def get_pip_command():
    """Get the pip command for the virtual environment."""
    system = platform.system()
    if system == "Windows":
        return str(Path("venv/Scripts/pip.exe"))
    else:
        return str(Path("venv/bin/pip"))

def get_python_command():
    """Get the python command for the virtual environment."""
    system = platform.system()
    if system == "Windows":
        return str(Path("venv/Scripts/python.exe"))
    else:
        return str(Path("venv/bin/python"))

def install_python_dependencies():
    """Install Python dependencies from requirements.txt."""
    print_header("Installing Python Dependencies")
    
    pip_cmd = get_pip_command()
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print_error("requirements.txt not found")
        return False
    
    print_info("Upgrading pip...")
    success, _, _ = run_command([pip_cmd, "install", "--upgrade", "pip"])
    if not success:
        print_warning("Failed to upgrade pip, continuing anyway...")
    
    print_info("Installing Python packages from requirements.txt...")
    success, stdout, stderr = run_command([pip_cmd, "install", "-r", str(requirements_file)])
    
    if success:
        print_success("Python dependencies installed successfully")
        return True
    else:
        print_error(f"Failed to install Python dependencies: {stderr}")
        return False

def verify_installation():
    """Verify that all dependencies are installed correctly."""
    print_header("Verifying Installation")
    
    python_cmd = get_python_command()
    all_ok = True
    
    # Check OpenCV
    print_info("Checking OpenCV...")
    success, stdout, _ = run_command([python_cmd, "-c", "import cv2; print(cv2.__version__)"])
    if success:
        version = stdout.strip()
        print_success(f"OpenCV {version} installed")
    else:
        print_error("OpenCV not found")
        all_ok = False
    
    # Check GStreamer (Python)
    print_info("Checking GStreamer (Python bindings)...")
    success, stdout, _ = run_command([
        python_cmd, "-c",
        "import gi; gi.require_version('Gst', '1.0'); from gi.repository import Gst; print('OK')"
    ])
    if success:
        print_success("GStreamer Python bindings installed")
    else:
        print_error("GStreamer Python bindings not found")
        all_ok = False
    
    # Check Flask
    print_info("Checking Flask...")
    success, stdout, _ = run_command([python_cmd, "-c", "import flask; print(flask.__version__)"])
    if success:
        version = stdout.strip()
        print_success(f"Flask {version} installed")
    else:
        print_error("Flask not found")
        all_ok = False
    
    # Check GStreamer command-line tools
    print_info("Checking GStreamer command-line tools...")
    if check_command_exists("gst-launch-1.0"):
        success, stdout, _ = run_command(["gst-launch-1.0", "--version"])
        if success:
            version = stdout.strip().split('\n')[0]
            print_success(f"GStreamer tools available: {version}")
        else:
            print_warning("GStreamer tools found but version check failed")
    else:
        print_warning("GStreamer command-line tools not in PATH (may be OK for Windows)")
    
    if all_ok:
        print_success("\nAll critical dependencies verified!")
        return True
    else:
        print_warning("\nSome dependencies failed verification. Check errors above.")
        return False

def main():
    """Main installation function."""
    print_header("Virtual Camera Server - Dependency Installation")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Detect OS and install system dependencies
    system = platform.system()
    print_info(f"Detected operating system: {system}")
    
    if system == "Linux":
        print_info("Detected Linux (assuming Ubuntu/Debian)")
        response = input("Install system dependencies? This requires sudo. (y/n): ").strip().lower()
        if response == 'y':
            if not install_linux_dependencies():
                print_error("Failed to install system dependencies")
                sys.exit(1)
        else:
            print_warning("Skipping system dependency installation")
    elif system == "Darwin":
        print_info("Detected macOS")
        response = input("Install system dependencies via Homebrew? (y/n): ").strip().lower()
        if response == 'y':
            if not install_macos_dependencies():
                print_error("Failed to install system dependencies")
                sys.exit(1)
        else:
            print_warning("Skipping system dependency installation")
    elif system == "Windows":
        if not install_windows_dependencies():
            print_error("GStreamer installation required")
            sys.exit(1)
    else:
        print_warning(f"Unsupported operating system: {system}")
        print_info("You may need to install dependencies manually")
    
    # Create virtual environment
    if not create_venv():
        print_error("Failed to create virtual environment")
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print_error("Failed to install Python dependencies")
        sys.exit(1)
    
    # Verify installation
    if verify_installation():
        print_header("Installation Complete!")
        print_success("All dependencies installed successfully")
        print_info("\nNext steps:")
        print("1. Activate the virtual environment:")
        if system == "Windows":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Run the application:")
        print("   python src/main.py")
        print("3. Access the web interface at: http://localhost:5000")
    else:
        print_warning("\nInstallation completed with warnings")
        print_info("Some dependencies may need manual installation")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



