"""Integration tests for VideoLibraryService."""
import os
import pytest
import tempfile
import cv2
import numpy as np

from src.services.video_library import VideoLibraryService
from src.services.exceptions import InvalidVideoError, VideoNotFoundError, StorageError


class TestVideoLibraryIntegration:
    """Integration tests for video library operations."""
    
    def test_upload_and_retrieve_video(self, video_library_service):
        """Test uploading a video and retrieving it."""
        # Create a minimal test video file using OpenCV
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            # Create a simple test video
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            
            for i in range(60):  # 3 seconds at 20 fps
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, f'Frame {i}', (50, 240), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                out.write(frame)
            out.release()
            
            # Upload video
            video = video_library_service.upload_video(temp_file.name, 'test_video.mp4')
            
            assert video is not None
            assert video.id is not None
            assert video.filename == 'test_video.mp4'
            assert video.duration > 0
            assert video.width == 640
            assert video.height == 480
            assert video.fps > 0
            
            # Retrieve video
            retrieved = video_library_service.get_video(video.id)
            assert retrieved.id == video.id
            assert retrieved.filename == video.filename
            
            # List videos
            videos = video_library_service.list_videos()
            assert len(videos) == 1
            assert videos[0].id == video.id
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_upload_invalid_file(self, video_library_service):
        """Test uploading an invalid/non-video file."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b'This is not a video file')
        temp_file.close()
        
        try:
            with pytest.raises(InvalidVideoError):
                video_library_service.upload_video(temp_file.name, 'test.txt')
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_get_video_file_path(self, video_library_service):
        """Test getting file path for uploaded video."""
        # Create a minimal test video
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library_service.upload_video(temp_file.name, 'test.mp4')
            file_path = video_library_service.get_video_file_path(video.id)
            
            assert os.path.exists(file_path)
            assert os.path.basename(file_path) == 'test.mp4'
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)

