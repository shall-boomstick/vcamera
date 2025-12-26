"""Unit tests for VideoLibraryService."""
import os
import pytest
import tempfile
import shutil

from src.services.exceptions import InvalidVideoError, VideoNotFoundError
from src.services.video_library import VideoLibraryService


class TestVideoLibraryService:
    """Tests for VideoLibraryService."""
    
    def test_list_videos_empty(self, video_library_service):
        """Test listing videos when library is empty."""
        videos = video_library_service.list_videos()
        
        assert isinstance(videos, list)
        assert len(videos) == 0
    
    def test_get_video_not_found(self, video_library_service):
        """Test getting a non-existent video."""
        with pytest.raises(VideoNotFoundError):
            video_library_service.get_video('nonexistent-id')
    
    def test_get_video_file_path_not_found(self, video_library_service):
        """Test getting file path for non-existent video."""
        with pytest.raises(VideoNotFoundError):
            video_library_service.get_video_file_path('nonexistent-id')
    
    def test_scan_and_add_missing_videos_empty(self, video_library_service):
        """Test scanning when no videos exist."""
        added = video_library_service.scan_and_add_missing_videos()
        
        assert isinstance(added, list)
        assert len(added) == 0
    
    def test_scan_and_add_missing_videos_no_directory(self, video_library_service, temp_dir):
        """Test scanning when videos directory doesn't exist."""
        os.chdir(temp_dir)
        # Remove videos directory if it exists
        if os.path.exists('videos'):
            shutil.rmtree('videos')
        
        added = video_library_service.scan_and_add_missing_videos()
        
        assert isinstance(added, list)
        assert len(added) == 0

