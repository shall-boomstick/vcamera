"""Pytest configuration and shared fixtures."""
import os
import shutil
import tempfile
from pathlib import Path

import pytest

# Import services only when needed to avoid import errors if dependencies missing
# Tests will fail gracefully if dependencies aren't installed


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    temp_path = tempfile.mkdtemp(prefix='vcamera_test_')
    # Ensure it exists
    os.makedirs(temp_path, exist_ok=True)
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_data_dir(temp_dir):
    """Create test data directory structure."""
    # Ensure base directory exists
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    
    data_dir = os.path.join(temp_dir, 'data')
    videos_dir = os.path.join(temp_dir, 'videos')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    
    return temp_dir


@pytest.fixture
def video_library_service(test_data_dir, monkeypatch):
    """Create VideoLibraryService with test data directory."""
    from src.services.storage import ensure_directories
    from src.services.video_library import VideoLibraryService
    
    # Store original directory - use a safe fallback
    try:
        original_cwd = os.getcwd()
        if not os.path.exists(original_cwd):
            original_cwd = os.path.expanduser('~')
    except (OSError, FileNotFoundError):
        original_cwd = os.path.expanduser('~')
    
    # Change to test directory
    if not os.path.exists(test_data_dir):
        os.makedirs(test_data_dir, exist_ok=True)
    
    os.chdir(test_data_dir)
    
    # Ensure directories exist
    ensure_directories()
    
    try:
        service = VideoLibraryService()
        yield service
    finally:
        # Restore original directory
        try:
            if os.path.exists(original_cwd):
                os.chdir(original_cwd)
            else:
                # Fallback to home directory if original doesn't exist
                os.chdir(os.path.expanduser('~'))
        except (OSError, FileNotFoundError):
            pass
        # Cleanup test directory
        if os.path.exists(test_data_dir):
            shutil.rmtree(test_data_dir, ignore_errors=True)


@pytest.fixture
def camera_manager_service(video_library_service):
    """Create CameraManagerService with test video library."""
    from src.services.camera_manager import CameraManagerService
    # video_library_service fixture already handles directory changes
    service = CameraManagerService(video_library_service)
    return service


@pytest.fixture
def auth_service(test_data_dir, monkeypatch):
    """Create AuthService with test data directory."""
    from src.services.storage import ensure_directories
    from src.services.auth import AuthService
    
    # Store original directory - use a safe fallback
    try:
        original_cwd = os.getcwd()
        if not os.path.exists(original_cwd):
            original_cwd = os.path.expanduser('~')
    except (OSError, FileNotFoundError):
        original_cwd = os.path.expanduser('~')
    
    # Change to test directory
    if not os.path.exists(test_data_dir):
        os.makedirs(test_data_dir, exist_ok=True)
    
    os.chdir(test_data_dir)
    
    # Ensure directories exist
    ensure_directories()
    
    try:
        service = AuthService()
        yield service
    finally:
        # Restore original directory
        try:
            if os.path.exists(original_cwd):
                os.chdir(original_cwd)
            else:
                # Fallback to home directory if original doesn't exist
                os.chdir(os.path.expanduser('~'))
        except (OSError, FileNotFoundError):
            pass
        # Cleanup test directory
        if os.path.exists(test_data_dir):
            shutil.rmtree(test_data_dir, ignore_errors=True)


@pytest.fixture
def sample_video_file(test_data_dir):
    """Create a minimal test video file (mock)."""
    # For actual tests, we'd need a real video file
    # For now, return a path that can be used
    video_path = os.path.join(test_data_dir, 'test_video.mp4')
    # Create a dummy file
    with open(video_path, 'wb') as f:
        f.write(b'fake video content')
    return video_path
