"""Integration tests for RTSP authentication."""
import os
import pytest
import tempfile
import cv2
import numpy as np

from src.services.camera_manager import CameraManagerService
from src.services.exceptions import InvalidAuthError
from src.services.video_library import VideoLibraryService


class TestRTSPAuthentication:
    """Integration tests for RTSP stream authentication."""
    
    def test_create_camera_with_auth_credentials(self, camera_manager_service, video_library_service):
        """Test creating camera with RTSP authentication credentials."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            camera = camera_manager_service.create_camera(
                name='Secure Camera',
                video_ids=[video.id],
                auth_enabled=True,
                auth_username='admin',
                auth_password='secure123'
            )
            
            assert camera.auth_enabled is True
            assert camera.auth_username == 'admin'
            assert camera.auth_password_hash is not None
            assert camera.auth_password_hash != 'secure123'  # Should be hashed
            # Password should not be stored in plain text
            assert 'secure123' not in str(camera.__dict__)
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_create_camera_auth_enabled_missing_username(self, camera_manager_service, video_library_service):
        """Test creating camera with auth enabled but missing username."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            with pytest.raises(InvalidAuthError):
                camera_manager_service.create_camera(
                    name='Test Camera',
                    video_ids=[video.id],
                    auth_enabled=True,
                    auth_username=None,
                    auth_password='password'
                )
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_create_camera_auth_enabled_missing_password(self, camera_manager_service, video_library_service):
        """Test creating camera with auth enabled but missing password."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            with pytest.raises(InvalidAuthError):
                camera_manager_service.create_camera(
                    name='Test Camera',
                    video_ids=[video.id],
                    auth_enabled=True,
                    auth_username='user',
                    auth_password=None
                )
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_update_camera_auth_settings(self, camera_manager_service, video_library_service):
        """Test updating camera authentication settings."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            # Create camera without auth
            camera = camera_manager_service.create_camera('Test Camera', [video.id])
            assert camera.auth_enabled is False
            
            # Enable auth
            updated = camera_manager_service.update_camera(
                camera.id,
                auth_enabled=True,
                auth_username='newuser',
                auth_password='newpass'
            )
            assert updated.auth_enabled is True
            assert updated.auth_username == 'newuser'
            assert updated.auth_password_hash is not None
            
            # Disable auth
            updated2 = camera_manager_service.update_camera(
                camera.id,
                auth_enabled=False
            )
            assert updated2.auth_enabled is False
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_camera_auth_password_hashing(self, camera_manager_service, video_library_service):
        """Test that passwords are properly hashed and not stored in plain text."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            password = 'my_secret_password'
            camera = camera_manager_service.create_camera(
                name='Secure Camera',
                video_ids=[video.id],
                auth_enabled=True,
                auth_username='user',
                auth_password=password
            )
            
            # Password should be hashed
            assert camera.auth_password_hash != password
            assert len(camera.auth_password_hash) > len(password)  # Hash is typically longer
            
            # Serialize and deserialize to ensure hash persists
            camera_dict = camera.to_dict()
            assert 'auth_password' not in camera_dict  # Plain password should not be in dict
            assert 'auth_password_hash' in camera_dict
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

