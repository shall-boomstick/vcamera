"""Unit tests for CameraManagerService."""
import os
import pytest

from src.services.exceptions import (
    CameraNotFoundError,
    DuplicateNameError,
    VideoNotFoundError,
    InvalidAuthError
)
from src.services.camera_manager import CameraManagerService


class TestCameraManagerService:
    """Tests for CameraManagerService."""
    
    def test_list_cameras_empty(self, camera_manager_service):
        """Test listing cameras when none exist."""
        cameras = camera_manager_service.list_cameras()
        
        assert isinstance(cameras, list)
        assert len(cameras) == 0
    
    def test_get_camera_not_found(self, camera_manager_service):
        """Test getting a non-existent camera."""
        with pytest.raises(CameraNotFoundError):
            camera_manager_service.get_camera('nonexistent-id')
    
    def test_create_camera_no_videos(self, camera_manager_service):
        """Test creating camera with empty video list."""
        with pytest.raises(ValueError, match="At least one video_id is required"):
            camera_manager_service.create_camera('Test Camera', [])
    
    def test_create_camera_invalid_video(self, camera_manager_service):
        """Test creating camera with invalid video ID."""
        with pytest.raises(VideoNotFoundError):
            camera_manager_service.create_camera('Test Camera', ['nonexistent-video'])
    
    def test_create_camera_auth_missing_credentials(self, camera_manager_service, video_library_service):
        """Test creating camera with auth enabled but missing credentials."""
        # Create a minimal test video using OpenCV
        import tempfile
        import cv2
        import numpy as np
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            # Create a simple test video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            with pytest.raises(InvalidAuthError, match="Username and password required"):
                camera_manager_service.create_camera(
                    'Test Camera',
                    [video.id],
                    auth_enabled=True,
                    auth_username=None,
                    auth_password=None
                )
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_get_camera_rtsp_url_not_found(self, camera_manager_service):
        """Test getting RTSP URL for non-existent camera."""
        with pytest.raises(CameraNotFoundError):
            camera_manager_service.get_camera_rtsp_url('nonexistent-id')
    
    def test_update_camera_not_found(self, camera_manager_service):
        """Test updating a non-existent camera."""
        with pytest.raises(CameraNotFoundError):
            camera_manager_service.update_camera('nonexistent-id', name='New Name')
    
    def test_delete_camera_not_found(self, camera_manager_service):
        """Test deleting a non-existent camera."""
        with pytest.raises(CameraNotFoundError):
            camera_manager_service.delete_camera('nonexistent-id')

