# Quickstart Guide: Virtual Camera Server

**Feature**: Virtual Camera Server Application  
**Date**: 2025-12-22

## Prerequisites

### System Requirements

- Python 3.11 or higher
- GStreamer 1.0+ with RTSP server support
- Linux, Windows, or macOS

### System Dependencies

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    libgstreamer1.0-dev \
    libgstrtspserver-1.0-dev \
    python3-gi \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-rtsp-server-1.0
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

### 1. Clone/Create Project

```bash
cd /path/to/project
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install opencv-python PyGObject
```

**Note**: PyGObject installation may require additional system packages. On Linux, ensure python3-gi is installed (see prerequisites).

### 4. Verify GStreamer Installation

```bash
gst-launch-1.0 --version
```

Should output GStreamer version information.

### 5. Create Project Directories

```bash
mkdir -p videos data
```

## First Run

### 1. Start Application

```bash
python src/main.py
```

The web server will start and display:
```
Starting web server...
Access the application at: http://localhost:5000
```

### 2. Access Web Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

### 3. Create Initial Credentials

On first run, the web interface will prompt you to create credentials:
- Username: (choose a username)
- Password: (choose a password)
- Confirm Password: (re-enter password)

Credentials are stored in `data/credentials.json`.

### 4. Login

Enter the credentials you just created to access the main dashboard.

## Basic Usage

### Upload a Video

1. Navigate to the "Video Library" tab in the web interface
2. Click "Choose File" and select a video file from your computer
3. Click "Upload" button
4. Wait for upload and metadata extraction to complete
5. Video appears in the library table

**Supported Formats**: MP4, AVI, MOV, MKV (any format OpenCV can read)

### Create a Virtual Camera

1. Navigate to the "Virtual Cameras" tab in the web interface
2. Scroll to the "Create New Camera" section
3. Enter a name for the camera
4. Select one or more videos from the library (checkboxes)
5. Optionally enable RTSP authentication and provide credentials
6. Click "Create Camera" button
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

### Using OpenCV (Python)

```python
import cv2

cap = cv2.VideoCapture('rtsp://localhost:8554/camera/{camera-id}')
while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Stream', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()
```

## File Structure

```
project_root/
├── src/              # Source code
├── videos/           # Uploaded video files
├── data/             # Metadata and configuration
│   ├── videos.json
│   ├── cameras.json
│   └── credentials.json
├── venv/             # Virtual environment
├── requirements.txt   # Python dependencies
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

### Viewer Window Blank

**Error**: Viewer opens but shows no video

**Solution**:
- Verify camera is in "active" status
- Check RTSP URL is correct
- Test stream in external client (VLC) first
- Verify GStreamer RTSP server is running

## Next Steps

- Review [data-model.md](./data-model.md) for data structure details
- Review [contracts/](./contracts/) for service interfaces
- See [plan.md](./plan.md) for implementation details

