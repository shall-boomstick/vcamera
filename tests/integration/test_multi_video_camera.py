"""Integration tests for multi-video camera functionality."""
import os
import pytest
import tempfile
import cv2
import numpy as np

from src.services.camera_manager import CameraManagerService
from src.services.exceptions import VideoNotFoundError
from src.services.video_library import VideoLibraryService


class TestMultiVideoCamera:
    """Integration tests for cameras with multiple videos."""
    
    def test_create_camera_with_multiple_videos(self, camera_manager_service, video_library_service):
        """Test creating a camera with multiple videos."""
        # Create multiple test videos
        video_ids = []
        temp_files = []
        
        try:
            for i in range(3):
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                temp_file.close()
                temp_files.append(temp_file.name)
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
                out.write(np.zeros((480, 640, 3), dtype=np.uint8))
                out.release()
                
                video = video_library_service.upload_video(temp_file.name, f'test_{i}.mp4')
                video_ids.append(video.id)
            
            # Create camera with multiple videos
            camera = camera_manager_service.create_camera(
                name='Multi Video Camera',
                video_ids=video_ids
            )
            
            assert camera is not None
            assert len(camera.video_ids) == 3
            assert camera.video_ids == video_ids
            assert camera.current_video_index == 0  # Should start at first video
            
        finally:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def test_camera_current_video_index(self, camera_manager_service, video_library_service):
        """Test that camera tracks current video index."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            # Create camera with single video
            camera = camera_manager_service.create_camera('Single Video', [video.id])
            assert camera.current_video_index == 0
            
            # Create camera with multiple videos
            video2 = video_library_service.upload_video(temp_file.name, 'test2.mp4')
            camera2 = camera_manager_service.create_camera('Multi Video', [video.id, video2.id])
            assert camera2.current_video_index == 0
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_update_camera_video_ids(self, camera_manager_service, video_library_service):
        """Test updating camera with different video IDs."""
        temp_files = []
        video_ids = []
        
        try:
            # Create initial videos
            for i in range(2):
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                temp_file.close()
                temp_files.append(temp_file.name)
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
                out.write(np.zeros((480, 640, 3), dtype=np.uint8))
                out.release()
                
                video = video_library_service.upload_video(temp_file.name, f'test_{i}.mp4')
                video_ids.append(video.id)
            
            # Create camera with first video
            camera = camera_manager_service.create_camera('Test Camera', [video_ids[0]])
            assert len(camera.video_ids) == 1
            
            # Update with both videos
            updated = camera_manager_service.update_camera(camera.id, video_ids=video_ids)
            assert len(updated.video_ids) == 2
            assert set(updated.video_ids) == set(video_ids)
            
        finally:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def test_create_camera_with_invalid_video_in_list(self, camera_manager_service, video_library_service):
        """Test creating camera with mix of valid and invalid video IDs."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            
            # Try to create camera with valid and invalid video IDs
            with pytest.raises(VideoNotFoundError):
                camera_manager_service.create_camera(
                    'Test Camera',
                    [video.id, 'nonexistent-video-id']
                )
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

