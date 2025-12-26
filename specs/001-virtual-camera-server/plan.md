# Implementation Plan: Virtual Camera Server Application

**Branch**: `001-virtual-camera-server` | **Date**: 2025-12-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-virtual-camera-server/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a Python-based web application that allows users to upload videos, create a library, and stream them as virtual cameras via RTSP. The application uses Flask for the web interface (minimal dependencies, cross-platform), OpenCV for video processing, and GStreamer with gst-rtsp-server for RTSP streaming. File-based storage (JSON + filesystem) keeps the architecture simple. Basic authentication protects the web interface, and RTSP streams support optional authentication. Each virtual camera can stream one or more videos on repeat, simulating real camera behavior for testing and development purposes. The web interface is accessible from any platform with a web browser, improving cross-platform compatibility.

## Technical Context

**Language/Version**: Python 3.11+ (standard library + minimal dependencies)  
**Primary Dependencies**: Flask (web framework), opencv-python (video processing), PyGObject (GStreamer bindings), gst-rtsp-server (RTSP streaming)  
**Storage**: File-based storage for videos (local filesystem in `videos/` directory), JSON files for metadata (camera configs, library index in `data/` directory)  
**Testing**: pytest (unit tests), manual integration testing for RTSP streams  
**Target Platform**: Linux (primary), Windows/Mac (secondary - requires GStreamer installation)  
**Project Type**: single (web application with embedded RTSP server)  
**Performance Goals**: 10 concurrent RTSP streams, <1% frame drops, <2s viewer latency, video uploads up to 2GB  
**Constraints**: Must run in VENV, KISS principle (simplest working solution), web interface must be functional not polished, requires system GStreamer installation  
**Scale/Scope**: Single-user web application, 10-50 virtual cameras, video library with 100s of videos, accessible from any platform with a web browser

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**KISS Principle**: ✅ YES - Single web application, file-based storage (JSON + filesystem), minimal abstractions. Using Flask (minimal web framework) for web interface - simple option with minimal dependencies. No microservices, no complex architecture patterns. File-based storage instead of database. Using existing GStreamer RTSP server rather than implementing protocol from scratch.

**Python Web Application**: ✅ YES - Python application with Flask web framework (minimal dependencies). Provides cross-platform accessibility through web browser, simpler than platform-specific GUI frameworks. Meets all requirements while improving accessibility.

**VENV Isolation**: ✅ YES - All dependencies in requirements.txt (opencv-python, PyGObject), setup documented in quickstart.md, all development in VENV.

**Complexity Justification**: 
- **GStreamer system dependency**: While this adds system-level installation complexity, implementing RTSP protocol from scratch would be far more complex and error-prone. GStreamer provides battle-tested, protocol-compliant RTSP server that justifies the installation step. This is documented in research.md.
- **OpenCV dependency**: Essential for video file reading and frame processing. No simpler alternative provides the same functionality.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── video.py          # Video entity/model
│   ├── virtual_camera.py # VirtualCamera entity/model
│   └── user_session.py   # UserSession entity/model
├── services/
│   ├── video_library.py  # Video upload, storage, retrieval
│   ├── rtsp_server.py    # RTSP streaming service
│   ├── auth.py           # Basic authentication
│   └── camera_manager.py # Virtual camera lifecycle management
├── web/
│   ├── app.py            # Flask application factory
│   ├── routes/           # Web routes (auth, dashboard, API)
│   │   ├── auth.py       # Authentication routes
│   │   ├── dashboard.py  # Dashboard routes
│   │   └── api.py        # API endpoints
│   ├── templates/        # HTML templates
│   │   ├── base.html     # Base template
│   │   ├── auth/         # Authentication templates
│   │   └── dashboard/    # Dashboard templates
│   └── static/           # Static files (CSS, JS)
└── main.py               # Application entry point (starts Flask server)

tests/
├── unit/
│   ├── test_models.py
│   └── test_services.py
└── integration/
    └── test_rtsp_streams.py

videos/                    # Video library storage (created at runtime)
data/                      # Metadata storage (JSON/SQLite)
venv/                      # Virtual environment
requirements.txt           # Python dependencies
README.md                  # Setup and usage documentation
```

**Structure Decision**: Single project structure with clear separation: models (data), services (business logic), web (user interface). Videos stored in dedicated directory, metadata in data directory. Simple flat structure following KISS principle - no unnecessary nesting or abstractions.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
