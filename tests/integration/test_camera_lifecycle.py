"""Integration tests for camera lifecycle management."""
import os
import pytest
import tempfile
import cv2
import numpy as np

from src.services.camera_manager import CameraManagerService
from src.services.exceptions import (
    DuplicateNameError,
    VideoNotFoundError,
    CameraNotFoundError
)
from src.services.video_library import VideoLibraryService


class TestCameraLifecycle:
    """Integration tests for camera creation and management."""
    
    def test_create_and_list_camera(self, camera_manager_service, video_library_service):
        """Test creating a camera and listing it."""
        # Create a test video
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            # Create camera
            camera = camera_manager_service.create_camera(
                name='Test Camera',
                video_ids=[video.id]
            )
            
            assert camera is not None
            assert camera.id is not None
            assert camera.name == 'Test Camera'
            assert camera.video_ids == [video.id]
            assert camera.rtsp_url is not None
            assert 'rtsp://' in camera.rtsp_url
            assert camera.status == 'inactive'
            
            # List cameras
            cameras = camera_manager_service.list_cameras()
            assert len(cameras) == 1
            assert cameras[0].id == camera.id
            
            # Get camera
            retrieved = camera_manager_service.get_camera(camera.id)
            assert retrieved.id == camera.id
            assert retrieved.name == camera.name
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_create_camera_duplicate_name(self, camera_manager_service, video_library_service):
        """Test creating cameras with duplicate names."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            camera_manager_service.create_camera('Duplicate Name', [video.id])
            
            with pytest.raises(DuplicateNameError):
                camera_manager_service.create_camera('Duplicate Name', [video.id])
                
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_create_camera_with_auth(self, camera_manager_service, video_library_service):
        """Test creating camera with authentication enabled."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            camera = camera_manager_service.create_camera(
                name='Auth Camera',
                video_ids=[video.id],
                auth_enabled=True,
                auth_username='rtsp_user',
                auth_password='rtsp_pass'
            )
            
            assert camera.auth_enabled is True
            assert camera.auth_username == 'rtsp_user'
            assert camera.auth_password_hash is not None
            assert camera.auth_password_hash != 'rtsp_pass'  # Should be hashed
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_update_camera(self, camera_manager_service, video_library_service):
        """Test updating camera configuration."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            camera = camera_manager_service.create_camera('Original Name', [video.id])
            
            # Update name
            updated = camera_manager_service.update_camera(camera.id, name='Updated Name')
            assert updated.name == 'Updated Name'
            
            # Verify update persisted
            retrieved = camera_manager_service.get_camera(camera.id)
            assert retrieved.name == 'Updated Name'
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_delete_camera(self, camera_manager_service, video_library_service):
        """Test deleting a camera."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            camera = camera_manager_service.create_camera('To Delete', [video.id])
            
            camera_manager_service.delete_camera(camera.id)
            
            with pytest.raises(CameraNotFoundError):
                camera_manager_service.get_camera(camera.id)
            
            cameras = camera_manager_service.list_cameras()
            assert len(cameras) == 0
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

