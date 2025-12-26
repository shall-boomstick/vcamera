# Installation Guide - Virtual Camera Server

This guide provides detailed installation instructions for the Virtual Camera Server application.

## Prerequisites

### System Requirements

- Python 3.11 or higher
- GStreamer 1.0+ with RTSP server support
- Linux, Windows, or macOS

## Step-by-Step Installation

### Step 1: Install System Dependencies

**⚠️ CRITICAL**: These must be installed BEFORE creating the virtual environment and installing Python packages.

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
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
```

#### macOS

```bash
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
```

#### Windows

1. Download GStreamer runtime from https://gstreamer.freedesktop.org/download/
2. Install GStreamer runtime (choose "Complete" installation)
3. Add GStreamer bin directory to PATH:
   - Default location: `C:\gstreamer\1.0\msvc_x86_64\bin`
   - Add to System Environment Variables → Path

### Step 2: Create Virtual Environment

```bash
cd /path/to/vcamera
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Troubleshooting PyGObject Installation**:

If you see errors about missing `pkg-config` or `cairo`:

1. **Linux**: Ensure all system packages from Step 1 are installed
   ```bash
   # Verify pkg-config is installed
   pkg-config --version
   
   # Verify cairo is available
   pkg-config --exists cairo && echo "Cairo found" || echo "Cairo missing"
   ```

2. **macOS**: Ensure Homebrew packages are installed and linked
   ```bash
   brew list | grep cairo
   brew list | grep gobject
   ```

3. **Windows**: Ensure GStreamer is properly installed and in PATH
   ```bash
   gst-launch-1.0 --version
   ```

### Step 4: Verify Installation

```bash
# Verify GStreamer
gst-launch-1.0 --version

# Verify Python can import GStreamer
python3 -c "import gi; gi.require_version('Gst', '1.0'); from gi.repository import Gst; print('GStreamer OK')"

# Verify OpenCV
python3 -c "import cv2; print(f'OpenCV {cv2.__version__}')"
```

### Step 5: Run the Application

```bash
python src/main.py
```

## Common Installation Issues

### Issue: "pkg-config not found"

**Solution**: Install pkg-config
- Linux: `sudo apt-get install pkg-config`
- macOS: `brew install pkg-config`
- Windows: Included with GStreamer installation

### Issue: "Dependency lookup for cairo failed"

**Solution**: Install Cairo development libraries
- Linux: `sudo apt-get install libcairo2-dev`
- macOS: `brew install cairo`
- Windows: Included with GStreamer

### Issue: "gir1.2-gstreamer-1.0 not found"

**Solution**: Install GObject Introspection packages
- Linux: `sudo apt-get install gir1.2-gstreamer-1.0 gir1.2-gst-rtsp-server-1.0 python3-gi`
- macOS: `brew install gobject-introspection`
- Windows: Included with GStreamer

### Issue: PyGObject builds from source (slow)

**Solution**: Install pre-built packages if available
- Linux: Use `python3-gi` from apt (already installed in Step 1)
- If pip still tries to build, ensure system packages are installed first

## Alternative: Use System Python GObject

On Linux, you can use the system-installed PyGObject instead of installing via pip:

1. Skip PyGObject in requirements.txt (comment it out)
2. Ensure `python3-gi` is installed: `sudo apt-get install python3-gi`
3. The system package will be available in the venv

However, this may cause version compatibility issues. The recommended approach is to install system dependencies first, then use pip.

