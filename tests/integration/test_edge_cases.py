"""Integration tests for edge cases and error handling."""
import os
import pytest
import tempfile
import cv2
import numpy as np

from src.services.camera_manager import CameraManagerService
from src.services.exceptions import VideoNotFoundError, CameraNotFoundError
from src.services.video_library import VideoLibraryService


class TestEdgeCases:
    """Integration tests for edge cases and error handling."""
    
    def test_delete_video_used_by_camera(self, camera_manager_service, video_library_service):
        """Test that deleting a video used by a camera raises an error."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            camera = camera_manager_service.create_camera('Test Camera', [video.id])
            
            # Try to delete video that's used by camera
            with pytest.raises(Exception):  # Should raise VideoInUseError or similar
                video_library_service.delete_video(video.id, camera_manager_service)
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_delete_video_not_used_by_camera(self, camera_manager_service, video_library_service):
        """Test that deleting a video not used by any camera succeeds."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            # Delete video (not used by any camera)
            video_library_service.delete_video(video.id, camera_manager_service)
            
            # Verify video is deleted
            with pytest.raises(VideoNotFoundError):
                video_library_service.get_video(video.id)
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_delete_camera_then_video(self, camera_manager_service, video_library_service):
        """Test deleting camera then video."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            camera = camera_manager_service.create_camera('Test Camera', [video.id])
            
            # Delete camera first
            camera_manager_service.delete_camera(camera.id)
            
            # Now video should be deletable
            video_library_service.delete_video(video.id, camera_manager_service)
            
            # Verify both are deleted
            with pytest.raises(CameraNotFoundError):
                camera_manager_service.get_camera(camera.id)
            with pytest.raises(VideoNotFoundError):
                video_library_service.get_video(video.id)
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_create_camera_with_empty_video_list(self, camera_manager_service):
        """Test creating camera with empty video list."""
        with pytest.raises(ValueError, match="At least one video_id is required"):
            camera_manager_service.create_camera('Test Camera', [])
    
    def test_update_camera_with_empty_video_list(self, camera_manager_service, video_library_service):
        """Test updating camera with empty video list."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            camera = camera_manager_service.create_camera('Test Camera', [video.id])
            
            # Try to update with empty video list
            with pytest.raises(ValueError, match="At least one video_id is required"):
                camera_manager_service.update_camera(camera.id, video_ids=[])
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_get_camera_after_deletion(self, camera_manager_service, video_library_service):
        """Test getting camera after it's been deleted."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            camera = camera_manager_service.create_camera('Test Camera', [video.id])
            camera_id = camera.id
            
            # Delete camera
            camera_manager_service.delete_camera(camera_id)
            
            # Try to get deleted camera
            with pytest.raises(CameraNotFoundError):
                camera_manager_service.get_camera(camera_id)
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_list_cameras_after_deletion(self, camera_manager_service, video_library_service):
        """Test listing cameras after deletion."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            camera = camera_manager_service.create_camera('Test Camera', [video.id])
            
            # List cameras (should have 1)
            cameras = camera_manager_service.list_cameras()
            assert len(cameras) == 1
            
            # Delete camera
            camera_manager_service.delete_camera(camera.id)
            
            # List cameras (should be empty)
            cameras = camera_manager_service.list_cameras()
            assert len(cameras) == 0
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)



