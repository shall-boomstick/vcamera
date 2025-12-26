"""Video Library Service for managing video uploads and storage."""
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List

import cv2

from ..models.video import Video
from .exceptions import InvalidVideoError, StorageError, VideoNotFoundError, VideoInUseError
from .storage import ensure_directories, get_videos_path, read_json, write_json
from .utils import generate_id


class VideoLibraryService:
    """Service for managing video library operations."""
    
    def __init__(self):
        """Initialize the video library service."""
        ensure_directories()
        self.videos_path = get_videos_path()
        self.videos_dir = Path('videos')
        self.videos_dir.mkdir(exist_ok=True)
    
    def upload_video(self, file_path: str, filename: str) -> Video:
        """Upload a video file to the library.
        
        Args:
            file_path: Source file path on user's computer
            filename: Original filename
            
        Returns:
            Video: Video object with metadata
            
        Raises:
            FileNotFoundError: Source file doesn't exist
            InvalidVideoError: File is not a valid video or unsupported format
            StorageError: Cannot write to videos/ directory
        """
        # Check source file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Generate unique ID
        video_id = generate_id()
        
        # Resolve paths to absolute paths for comparison
        source_abs = os.path.abspath(file_path)
        dest_path = self.videos_dir / filename
        dest_abs = os.path.abspath(str(dest_path))
        
        # If source and destination are the same file, skip copy
        if source_abs == dest_abs:
            # File is already in videos directory, use it directly
            pass
        else:
            # Copy file to videos directory
            try:
                shutil.copy2(file_path, dest_path)
            except IOError as e:
                raise StorageError(f"Cannot copy file to videos directory: {e}")
        
        # Extract metadata using OpenCV
        try:
            metadata = self._extract_metadata(str(dest_path))
        except Exception as e:
            # Clean up copied file if metadata extraction fails
            os.remove(dest_path)
            raise InvalidVideoError(f"Cannot extract video metadata: {e}")
        
        # Get file size
        file_size = os.path.getsize(dest_path)
        
        # Create Video object
        video = Video(
            id=video_id,
            filename=filename,
            file_path=filename,  # Relative path in videos/ directory
            file_size=file_size,
            duration=metadata['duration'],
            width=metadata['width'],
            height=metadata['height'],
            fps=metadata['fps'],
            format=metadata['format'],
            upload_date=datetime.utcnow().isoformat() + 'Z',
            metadata={}
        )
        
        # Save to videos.json
        videos = self._load_videos()
        videos.append(video.to_dict())
        try:
            write_json(self.videos_path, videos)
        except StorageError as e:
            # Clean up copied file if save fails
            os.remove(dest_path)
            raise StorageError(f"Cannot save video metadata: {e}")
        
        return video
    
    def _extract_metadata(self, video_path: str) -> dict:
        """Extract video metadata using OpenCV.
        
        Args:
            video_path: Path to video file
            
        Returns:
            dict: Metadata containing duration, width, height, fps, format
            
        Raises:
            InvalidVideoError: If video cannot be opened or metadata extracted
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise InvalidVideoError(f"Cannot open video file: {video_path}")
        
        try:
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate duration
            if fps > 0:
                duration = frame_count / fps
            else:
                duration = 0.0
            
            # Get format from file extension
            format_ext = Path(video_path).suffix[1:].lower() if Path(video_path).suffix else 'unknown'
            
            # Validate metadata
            if duration <= 0:
                raise InvalidVideoError("Video duration must be > 0")
            if width <= 0 or height <= 0:
                raise InvalidVideoError("Video dimensions must be > 0")
            if fps <= 0:
                raise InvalidVideoError("Video FPS must be > 0")
            
            return {
                'duration': duration,
                'width': width,
                'height': height,
                'fps': fps,
                'format': format_ext
            }
        finally:
            cap.release()
    
    def get_video(self, video_id: str) -> Video:
        """Retrieve a video by ID.
        
        Args:
            video_id: Unique video identifier
            
        Returns:
            Video: Video object
            
        Raises:
            VideoNotFoundError: Video ID doesn't exist
        """
        videos = self._load_videos()
        for video_data in videos:
            if video_data['id'] == video_id:
                return Video.from_dict(video_data)
        raise VideoNotFoundError(f"Video not found: {video_id}")
    
    def list_videos(self) -> List[Video]:
        """List all videos in the library.
        
        Returns:
            List[Video]: List of Video objects
        """
        videos = self._load_videos()
        return [Video.from_dict(v) for v in videos]
    
    def scan_and_add_missing_videos(self) -> List[Video]:
        """Scan videos directory and add any files that aren't in the library.
        
        This is useful for syncing videos that were manually added to the directory
        or videos that failed to register during upload.
        
        Returns:
            List[Video]: List of newly added Video objects
        """
        added_videos = []
        
        # Get list of videos already in library
        existing_videos = self.list_videos()
        existing_filenames = {v.filename for v in existing_videos}
        
        # Scan videos directory
        if not self.videos_dir.exists():
            return added_videos
        
        # Common video extensions
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}
        
        for file_path in self.videos_dir.iterdir():
            if not file_path.is_file():
                continue
            
            filename = file_path.name
            file_ext = file_path.suffix.lower()
            
            # Skip if not a video file
            if file_ext not in video_extensions:
                continue
            
            # Skip if already in library
            if filename in existing_filenames:
                continue
            
            # Try to add this video to the library
            try:
                video = self.upload_video(str(file_path), filename)
                added_videos.append(video)
            except Exception as e:
                # Log error but continue with other files
                from .logger import get_logger
                logger = get_logger(__name__)
                logger.warning(f"Failed to add video {filename}: {e}")
                continue
        
        return added_videos
    
    def get_video_file_path(self, video_id: str) -> str:
        """Get the filesystem path to a video file.
        
        Args:
            video_id: Unique video identifier
            
        Returns:
            str: Absolute file path to video file
            
        Raises:
            VideoNotFoundError: Video ID doesn't exist
        """
        video = self.get_video(video_id)
        return os.path.abspath(self.videos_dir / video.file_path)
    
    def delete_video(self, video_id: str, camera_manager=None) -> bool:
        """Delete a video from the library.
        
        Args:
            video_id: Unique video identifier
            camera_manager: Optional CameraManagerService to check if video is in use
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            VideoNotFoundError: Video ID doesn't exist
            VideoInUseError: Video is assigned to one or more cameras
        """
        video = self.get_video(video_id)
        
        # Check if video is assigned to any camera
        if camera_manager:
            cameras = camera_manager.list_cameras()
            for camera in cameras:
                if video_id in camera.video_ids:
                    raise VideoInUseError(f"Video {video_id} is assigned to camera {camera.name}")
        
        # Delete video file
        video_file_path = self.videos_dir / video.file_path
        if video_file_path.exists():
            os.remove(video_file_path)
        
        # Remove from videos.json
        videos = self._load_videos()
        videos = [v for v in videos if v['id'] != video_id]
        write_json(self.videos_path, videos)
        
        return True
    
    def _load_videos(self) -> List[dict]:
        """Load videos from JSON file.
        
        Returns:
            List[dict]: List of video dictionaries
        """
        videos = read_json(self.videos_path)
        return videos if videos is not None else []

