# Research: Virtual Camera Server Technology Choices

**Date**: 2025-12-22  
**Feature**: Virtual Camera Server Application

## Research Goals

Determine the simplest technology stack that meets requirements while adhering to KISS principle:
- Python web framework (simplest option)
- RTSP server library (simplest option)
- Video processing library (simplest option)
- Authentication approach (simplest option)

## Technology Decisions

### 1. Web Framework

**Decision**: **Flask** (minimal Python web framework)

**Rationale**: 
- Simple, lightweight web framework with minimal dependencies
- Sufficient for basic file upload, forms, and dashboard display
- Widely documented and simple to use
- Cross-platform compatibility - accessible from any device with a web browser
- No platform-specific dependencies (unlike desktop GUI frameworks)
- Better accessibility than desktop GUI applications
- Aligns with KISS principle while providing modern web interface

**Alternatives Considered**:
- **tkinter**: Desktop GUI framework, but requires platform-specific dependencies (python3-tk on Linux) and doesn't provide cross-platform accessibility
- **Django**: Full-featured framework but overkill for this simple application, violates KISS principle
- **FastAPI**: Modern async framework but adds unnecessary complexity for this use case
- **PyQt/PySide**: Desktop GUI with heavy dependencies and licensing complexity. Overkill for this use case.

**Trade-offs**: Flask requires a small dependency but provides better cross-platform accessibility and modern web interface compared to desktop GUI frameworks.

### 2. RTSP Server Implementation

**Decision**: **GStreamer with gst-rtsp-server** (via Python gi bindings)

**Rationale**:
- Industry-standard multimedia framework with robust RTSP support
- Built-in authentication support via RTSPAuth
- Can stream video files directly via pipeline
- Protocol-compliant implementation
- Well-documented for RTSP use cases

**Alternatives Considered**:
- **aiortc**: WebRTC-focused, not ideal for pure RTSP
- **python-rtsp-server**: Lightweight but may lack full protocol compliance
- **Custom RTSP implementation**: Too complex, violates KISS principle

**Trade-offs**: Requires system-level GStreamer installation (not pure Python), but provides robust, tested RTSP server functionality. This complexity is justified as implementing RTSP from scratch would be far more complex.

### 3. Video Processing

**Decision**: **opencv-python** (cv2)

**Rationale**:
- Industry standard for video processing
- Can read video files, extract frames, handle various formats
- Simple API for basic video operations
- Can integrate with GStreamer pipelines
- Well-documented and widely used

**Alternatives Considered**:
- **ffmpeg-python**: Lower-level, more complex API
- **imageio**: Simpler but less control over video processing
- **moviepy**: Higher-level but heavier dependencies

**Trade-offs**: opencv-python is the right balance of simplicity and functionality.

### 4. Authentication

**Decision**: **Python standard library (hashlib + Flask sessions + file-based storage)**

**Rationale**:
- Minimal external dependencies (Flask sessions use standard library)
- Simple username/password hash storage
- Session-based authentication for web interface
- KISS principle - no need for complex auth frameworks
- Flask sessions provide secure session management

**Alternatives Considered**:
- **Flask-Login**: Overkill for single-user application
- **OAuth/JWT**: Unnecessary complexity for basic authentication
- **SQLite user database**: More complex than needed for basic auth

**Trade-offs**: File-based credential storage is simple but less secure than database. Acceptable for single-user application. Flask sessions provide adequate security for this use case.

### 5. Data Storage

**Decision**: **JSON files for metadata, filesystem for videos**

**Rationale**:
- No database dependencies
- Simple file-based storage
- Easy to backup and inspect
- Sufficient for single-user application
- Videos stored as files in dedicated directory

**Alternatives Considered**:
- **SQLite**: More structured but adds complexity
- **PostgreSQL/MySQL**: Enterprise-grade overkill
- **In-memory only**: Doesn't meet persistence requirement

**Trade-offs**: JSON files are simple but don't scale well. Acceptable for MVP and single-user use case.

## Implementation Approach

### RTSP Server Architecture

1. **Video File Reading**: Use OpenCV to read video files frame-by-frame
2. **Frame Encoding**: Encode frames to H.264 via GStreamer pipeline
3. **RTSP Streaming**: Use gst-rtsp-server to serve encoded stream
4. **Loop Playback**: When video ends, restart from beginning
5. **Multiple Videos**: Cycle through assigned videos sequentially

### Web Interface Architecture

1. **Main Dashboard**: Flask template with tabbed interface (Videos/Cameras)
2. **Login Page**: HTML form with username/password
3. **Video Library View**: HTML table listing uploaded videos with upload form
4. **Camera Management**: HTML table listing cameras with start/stop controls
5. **Camera Configuration**: HTML form to name camera and select videos
6. **Stream Viewer**: Embedded video player showing RTSP stream (future enhancement)

### Authentication Flow

1. User accesses web interface → Redirect to login page
2. User enters credentials → Hash password, compare with stored hash
3. Valid credentials → Create Flask session, redirect to dashboard
4. Invalid credentials → Show error message, remain on login page
5. Session validation → Check session on each request, redirect to login if expired

## Dependencies Summary

**Core Dependencies**:
- Python 3.11+ (standard library: hashlib, json)
- Flask (web framework)
- opencv-python (video processing)
- PyGObject (GStreamer Python bindings)

**System Dependencies**:
- GStreamer 1.0+ (RTSP server, video encoding)
- gst-rtsp-server (RTSP server library)
- gst-plugins-base, gst-plugins-good, gst-plugins-bad (GStreamer plugins)

## Installation Notes

GStreamer installation varies by platform:
- **Linux**: `sudo apt-get install gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad libgstreamer1.0-dev libgstrtspserver-1.0-dev python3-gi`
- **Windows**: Install GStreamer runtime from gstreamer.freedesktop.org
- **macOS**: `brew install gstreamer gst-plugins-base gst-plugins-good gst-plugins-bad gst-rtsp-server`

Python dependencies via pip:
- `Flask` (web framework)
- `opencv-python` (video processing)
- `PyGObject` (requires system GStreamer first)

## Complexity Justification

**GStreamer Dependency**: While this adds system-level complexity, implementing RTSP protocol from scratch would be far more complex and error-prone. GStreamer provides a battle-tested, protocol-compliant solution that justifies the installation complexity.

**OpenCV Dependency**: Essential for video file reading and frame processing. No simpler alternative exists that provides the same functionality.

## Remaining Questions

All NEEDS CLARIFICATION items from Technical Context have been resolved through research.

