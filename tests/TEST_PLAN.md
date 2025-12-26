# Test Plan: Virtual Camera Server (Phases 1-4)

## Overview

This document outlines the test strategy for Phases 1-4 of the Virtual Camera Server application, covering setup, foundational services, MVP functionality, and web interface.

## Test Coverage Summary

### Phase 1: Setup ✅
- **Manual Validation**: Project structure, requirements.txt, README.md, .gitignore
- **No automated tests** (infrastructure setup)

### Phase 2: Foundational ✅
- **Unit Tests**: Storage utilities, exceptions, logging, UUID generation
- **Coverage**: 100% of utility functions

### Phase 3: User Story 1 (MVP) ✅
- **Unit Tests**: Models (Video, VirtualCamera), Services (VideoLibrary, CameraManager)
- **Integration Tests**: Video upload workflow, Camera lifecycle, Service interactions
- **Coverage**: Core functionality paths

### Phase 4: User Story 2 (Web Interface) ✅
- **Unit Tests**: UserSession model, AuthService
- **Integration Tests**: Authentication flow, Session management
- **User Tests**: Web interface workflows, Authentication, Video upload, Camera management

## Test Execution Plan

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test suite
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/user/          # User/End-to-end tests only

# Run specific test file
pytest tests/unit/test_models.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

### Test Categories

#### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation

**Files**:
- `test_models.py` - Data model serialization/deserialization
- `test_storage.py` - JSON storage utilities
- `test_auth_service.py` - Authentication service logic
- `test_video_library_service.py` - Video library service (basic operations)
- `test_camera_manager_service.py` - Camera manager service (basic operations)

**Coverage Goals**:
- All model methods (to_dict, from_dict)
- All service methods (happy paths and error cases)
- Edge cases and validation

#### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test interactions between multiple components

**Files**:
- `test_video_library_integration.py` - Video upload and retrieval workflows
- `test_camera_lifecycle.py` - Camera creation, update, deletion workflows
- `test_auth_integration.py` - Complete authentication workflows

**Coverage Goals**:
- Multi-service interactions
- Data persistence across operations
- Error propagation between services

#### 3. User/End-to-End Tests (`tests/user/`)

**Purpose**: Test complete user workflows through web interface

**Files**:
- `test_web_interface.py` - Web interface workflows

**Coverage Goals**:
- Authentication flow (create credentials → login → logout)
- Video upload through web interface
- Camera management through web interface
- Access control (authentication required)

## Test Scenarios by Feature

### Authentication

**Unit Tests**:
- ✅ Create credentials
- ✅ Authenticate with valid credentials
- ✅ Authenticate with invalid credentials
- ✅ Validate session
- ✅ Logout session
- ✅ Change password

**Integration Tests**:
- ✅ Full authentication workflow
- ✅ Multiple concurrent sessions
- ✅ Session persistence

**User Tests**:
- ✅ Create credentials through web interface
- ✅ Login through web interface
- ✅ Logout through web interface
- ✅ Access control (protected routes)

### Video Library

**Unit Tests**:
- ✅ List videos (empty library)
- ✅ Get video (not found)
- ✅ Scan for missing videos

**Integration Tests**:
- ✅ Upload video and retrieve
- ✅ Upload invalid file (error handling)
- ✅ Get video file path
- ✅ Video metadata extraction

**User Tests**:
- ✅ Upload video through web interface (requires auth)
- ✅ View video library in dashboard

### Camera Management

**Unit Tests**:
- ✅ List cameras (empty)
- ✅ Get camera (not found)
- ✅ Create camera validation (empty video list, invalid video)
- ✅ Create camera with auth (missing credentials)

**Integration Tests**:
- ✅ Create and list camera
- ✅ Create camera with duplicate name
- ✅ Create camera with authentication
- ✅ Update camera configuration
- ✅ Delete camera

**User Tests**:
- ✅ Create camera through web interface (requires auth)
- ✅ View camera list in dashboard
- ✅ Start/stop camera through web interface

## Test Data Management

### Fixtures

All tests use temporary directories via pytest fixtures:
- `temp_dir`: Base temporary directory
- `test_data_dir`: Test data directory with videos/ and data/ subdirectories
- `video_library_service`: VideoLibraryService with test data
- `camera_manager_service`: CameraManagerService with test data
- `auth_service`: AuthService with test data
- `test_client`: Flask test client for web interface tests

### Test Videos

Integration tests create minimal test videos using OpenCV:
- Small test videos (640x480, few frames)
- Created in temporary files
- Cleaned up after tests

## Known Limitations

1. **RTSP Streaming Tests**: Not included (requires GStreamer setup and actual streaming)
2. **Performance Tests**: Not included (concurrent streams, large files)
3. **Browser Tests**: Not included (would require Selenium/Playwright)
4. **Security Tests**: Basic authentication only (no penetration testing)

## Success Criteria

### Test Execution
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All user tests pass
- ✅ No test failures or errors

### Coverage Goals
- **Models**: 100% coverage
- **Services**: >80% coverage (core paths)
- **Web Routes**: >70% coverage (happy paths and error cases)

### Quality Metrics
- Tests are independent and can run in any order
- Tests clean up after themselves (no data pollution)
- Tests are fast (< 5 seconds for full suite)
- Tests are maintainable and well-documented

## Future Test Additions

### Phase 5+ (Not Yet Implemented)
- RTSP streaming integration tests
- Multiple video playback tests
- RTSP viewer window tests
- RTSP authentication tests

### Additional Test Types
- Performance tests (concurrent streams, large uploads)
- Security tests (authentication bypass, session hijacking)
- Browser-based E2E tests (Selenium/Playwright)
- Load tests (multiple concurrent users)

