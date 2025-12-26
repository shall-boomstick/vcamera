# Virtual Camera Server Application

A Python-based GUI application that allows users to upload videos, create a library, and stream them as virtual cameras via RTSP. Each virtual camera can stream one or more videos on repeat, simulating real camera behavior for testing and development purposes.

## Features

- Upload videos to create a video library
- Create multiple virtual camera instances
- Stream videos via RTSP protocol
- Play videos on continuous repeat
- Support for multiple videos per camera (sequential playback)
- Built-in RTSP stream viewer
- RTSP authentication support
- Simple GUI interface with basic authentication

## Prerequisites

### System Requirements

- Python 3.11 or higher
- GStreamer 1.0+ with RTSP server support
- Linux, Windows, or macOS

### System Dependencies (INSTALL THESE FIRST!)

**⚠️ IMPORTANT**: Install system dependencies BEFORE creating venv and running `pip install`.

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    pkg-config \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-rtsp-server-1.0 \
    libcairo2-dev \
    libgirepository1.0-dev \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    libgstreamer1.0-dev \
    libgstrtspserver-1.0-dev
```

**macOS**:
```bash
brew install gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-rtsp-server python@3.11
```

**Windows**:
1. Download GStreamer runtime from https://gstreamer.freedesktop.org/download/
2. Install GStreamer runtime
3. Add GStreamer bin directory to PATH

## Setup

### 1. Install System Dependencies (REQUIRED FIRST!)

**⚠️ CRITICAL**: PyGObject requires system-level packages. You MUST install these BEFORE creating the venv and running `pip install`.

**Linux (Ubuntu/Debian)** - Run this command:
```bash
sudo apt-get update && sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
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

**Important Notes**:
- `python3-tk` is required for tkinter (GUI framework) - it's a system package, not installable via pip
- `libgirepository-2.0-dev` is required for PyGObject to find `girepository-2.0` via pkg-config

**macOS**:
```bash
brew install pkg-config cairo gobject-introspection gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-rtsp-server
```

**Windows**:
Install GStreamer runtime from https://gstreamer.freedesktop.org/download/ and ensure it's in PATH.

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Troubleshooting**: If PyGObject installation fails with "pkg-config not found" or "cairo not found", you need to install the system dependencies from Step 1 first. See [INSTALL.md](INSTALL.md) for detailed troubleshooting.

### 3. Verify GStreamer Installation

```bash
gst-launch-1.0 --version
```

Should output GStreamer version information.

### 4. Run Application

```bash
python src/main.py
```

## First Run

On first run, the application will prompt you to create credentials:
- Username: (choose a username)
- Password: (choose a password)

Credentials are stored in `data/credentials.json`.

## Usage

### Upload a Video

1. Click "Upload Video" button
2. Select a video file from your computer
3. Wait for upload and metadata extraction to complete
4. Video appears in library list

**Supported Formats**: MP4, AVI, MOV, MKV (any format OpenCV can read)

### Create a Virtual Camera

1. Click "Create Camera" button
2. Enter a name for the camera (e.g., "Front Door")
3. Select one or more videos from the library
4. (Optional) Enable RTSP authentication:
   - Check "Enable Authentication"
   - Enter username and password
5. Click "Create"
6. Camera appears in camera list with status "inactive"

### Start Streaming

1. Select a camera from the list
2. Click "Start" button
3. Camera status changes to "active"
4. RTSP URL is displayed (e.g., `rtsp://localhost:8554/camera/{id}`)

### View Stream

1. With camera active, click "View Stream" button
2. Viewer window opens showing the RTSP stream
3. Video plays in loop (or cycles through multiple videos)

### Stop Streaming

1. Select active camera
2. Click "Stop" button
3. Camera status changes to "inactive"
4. RTSP stream stops

## Testing RTSP Stream

### Using VLC

1. Start a virtual camera
2. Copy the RTSP URL
3. Open VLC Media Player
4. Media → Open Network Stream
5. Paste RTSP URL
6. If authentication enabled, enter username/password
7. Click Play

### Using ffplay

```bash
ffplay rtsp://localhost:8554/camera/{camera-id}
```

If authentication enabled:
```bash
ffplay rtsp://username:password@localhost:8554/camera/{camera-id}
```

## Project Structure

```
project_root/
├── src/              # Source code
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   └── gui/          # GUI components
├── videos/           # Uploaded video files
├── data/             # Metadata and configuration
│   ├── videos.json
│   ├── cameras.json
│   └── credentials.json
├── venv/             # Virtual environment
├── requirements.txt  # Python dependencies
└── README.md
```

## Troubleshooting

### GStreamer Not Found

**Error**: `ModuleNotFoundError: No module named 'gi'` or GStreamer errors

**Solution**: Install system GStreamer packages (see Prerequisites)

### Port Already in Use

**Error**: `PortInUseError` when starting camera

**Solution**: 
- Stop other cameras using the port
- Or modify camera configuration to use different port

### Video Won't Play

**Error**: Video uploads but won't stream

**Solution**:
- Verify video file is not corrupted
- Check video format is supported by OpenCV
- Verify GStreamer plugins are installed

### Authentication Fails

**Error**: Cannot connect to RTSP stream with credentials

**Solution**:
- Verify username/password are correct
- Check camera has authentication enabled
- Ensure RTSP client supports authentication

## Development

This project follows the KISS (Keep It Simple, Stupid) principle:
- Simple file-based storage (JSON + filesystem)
- Minimal dependencies
- Functional GUI (not polished)
- Single-user desktop application

## License

[Add license information]

