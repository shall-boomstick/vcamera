#!/bin/bash
# Dependency Installation Script for Virtual Camera Server (Linux/macOS)
#
# This script automates the installation of system and Python dependencies
# for the Virtual Camera Server application.
#
# Usage:
#   ./install_dependencies.sh
#   or
#   bash install_dependencies.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    echo "$OS"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    if ! command_exists python3; then
        print_error "Python 3 not found. Please install Python 3.11 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
        print_error "Python 3.11+ required. Found Python $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION detected"
}

# Install Linux dependencies
install_linux_deps() {
    print_header "Installing Linux System Dependencies"
    
    if [ "$EUID" -ne 0 ]; then
        print_info "This requires sudo privileges"
        read -p "Continue with sudo? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "Skipping system dependency installation"
            return 0
        fi
    fi
    
    print_info "Updating package list..."
    sudo apt-get update
    
    print_info "Installing system packages (this may take a few minutes)..."
    sudo apt-get install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        python3-tk \
        pkg-config \
        python3-gi \
        python3-gi-cairo \
        gir1.2-gstreamer-1.0 \
        gir1.2-gst-rtsp-server-1.0 \
        libcairo2-dev \
        libgirepository1.0-dev \
        libgirepository-2.0-dev \
        gobject-introspection \
        gstreamer1.0-tools \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        libgstreamer1.0-dev \
        libgstrtspserver-1.0-dev
    
    print_success "Linux system dependencies installed"
}

# Install macOS dependencies
install_macos_deps() {
    print_header "Installing macOS System Dependencies"
    
    if ! command_exists brew; then
        print_error "Homebrew not found. Please install Homebrew first:"
        print_info "Visit: https://brew.sh"
        exit 1
    fi
    
    print_success "Homebrew detected"
    
    print_info "Installing packages via Homebrew (this may take a while)..."
    brew install \
        python@3.11 \
        pkg-config \
        cairo \
        gobject-introspection \
        gstreamer \
        gst-plugins-base \
        gst-plugins-good \
        gst-plugins-bad \
        gst-rtsp-server
    
    print_success "macOS system dependencies installed"
}

# Create virtual environment
setup_venv() {
    print_header "Setting Up Virtual Environment"
    
    if [ -d "venv" ]; then
        print_info "Virtual environment already exists"
        read -p "Recreate virtual environment? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf venv
        else
            print_success "Using existing virtual environment"
            return 0
        fi
    fi
    
    print_info "Creating virtual environment..."
    python3 -m venv venv
    
    print_success "Virtual environment created"
}

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    print_info "Upgrading pip..."
    venv/bin/pip install --upgrade pip || print_warning "Failed to upgrade pip, continuing..."
    
    print_info "Installing Python packages from requirements.txt..."
    venv/bin/pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"
    
    PYTHON_CMD="venv/bin/python"
    ALL_OK=true
    
    # Check OpenCV
    print_info "Checking OpenCV..."
    if $PYTHON_CMD -c "import cv2; print(cv2.__version__)" 2>/dev/null; then
        VERSION=$($PYTHON_CMD -c "import cv2; print(cv2.__version__)" 2>/dev/null)
        print_success "OpenCV $VERSION installed"
    else
        print_error "OpenCV not found"
        ALL_OK=false
    fi
    
    # Check GStreamer
    print_info "Checking GStreamer (Python bindings)..."
    if $PYTHON_CMD -c "import gi; gi.require_version('Gst', '1.0'); from gi.repository import Gst; print('OK')" 2>/dev/null; then
        print_success "GStreamer Python bindings installed"
    else
        print_error "GStreamer Python bindings not found"
        ALL_OK=false
    fi
    
    # Check Flask
    print_info "Checking Flask..."
    if $PYTHON_CMD -c "import flask; print(flask.__version__)" 2>/dev/null; then
        VERSION=$($PYTHON_CMD -c "import flask; print(flask.__version__)" 2>/dev/null)
        print_success "Flask $VERSION installed"
    else
        print_error "Flask not found"
        ALL_OK=false
    fi
    
    # Check GStreamer tools
    print_info "Checking GStreamer command-line tools..."
    if command_exists gst-launch-1.0; then
        VERSION=$(gst-launch-1.0 --version 2>/dev/null | head -n1)
        print_success "GStreamer tools available: $VERSION"
    else
        print_warning "GStreamer command-line tools not in PATH"
    fi
    
    if [ "$ALL_OK" = true ]; then
        print_success "\nAll critical dependencies verified!"
        return 0
    else
        print_warning "\nSome dependencies failed verification"
        return 1
    fi
}

# Main function
main() {
    print_header "Virtual Camera Server - Dependency Installation"
    
    # Check Python
    check_python
    
    # Detect OS
    OS=$(detect_os)
    print_info "Detected operating system: $OS"
    
    # Install system dependencies
    if [ "$OS" = "linux" ]; then
        install_linux_deps
    elif [ "$OS" = "macos" ]; then
        read -p "Install system dependencies via Homebrew? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_macos_deps
        else
            print_warning "Skipping system dependency installation"
        fi
    else
        print_warning "Unknown OS. Skipping system dependency installation"
    fi
    
    # Setup virtual environment
    setup_venv
    
    # Install Python dependencies
    install_python_deps
    
    # Verify
    if verify_installation; then
        print_header "Installation Complete!"
        print_success "All dependencies installed successfully"
        print_info "\nNext steps:"
        echo "1. Activate the virtual environment:"
        echo "   source venv/bin/activate"
        echo "2. Run the application:"
        echo "   python src/main.py"
        echo "3. Access the web interface at: http://localhost:5000"
    else
        print_warning "\nInstallation completed with warnings"
        print_info "Some dependencies may need manual installation"
        exit 1
    fi
}

# Run main function
main "$@"





