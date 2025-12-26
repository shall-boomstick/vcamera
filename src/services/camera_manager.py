"""Camera Manager Service for managing virtual cameras."""
import hashlib
from datetime import datetime
from typing import List, Optional

from ..models.virtual_camera import VirtualCamera
from .exceptions import CameraNotFoundError, DuplicateNameError, InvalidAuthError, VideoNotFoundError
from .storage import ensure_directories, get_cameras_path, read_json, write_json
from .utils import generate_id


class CameraManagerService:
    """Service for managing virtual camera lifecycle."""
    
    def __init__(self, video_library_service):
        """Initialize the camera manager service.
        
        Args:
            video_library_service: VideoLibraryService instance for validating videos
        """
        ensure_directories()
        self.cameras_path = get_cameras_path()
        self.video_library = video_library_service
        self.base_rtsp_port = 8554
        self.port_counter = 0
    
    def create_camera(
        self,
        name: str,
        video_ids: List[str],
        auth_enabled: bool = False,
        auth_username: Optional[str] = None,
        auth_password: Optional[str] = None
    ) -> VirtualCamera:
        """Create a new virtual camera.
        
        Args:
            name: User-provided camera name (must be unique)
            video_ids: List of video IDs to assign (order matters)
            auth_enabled: Whether to enable RTSP authentication
            auth_username: RTSP username if auth enabled
            auth_password: RTSP password if auth enabled (plain text)
            
        Returns:
            VirtualCamera: VirtualCamera object
            
        Raises:
            DuplicateNameError: Camera name already exists
            VideoNotFoundError: One or more video_ids don't exist
            InvalidAuthError: Auth enabled but username/password missing
        """
        # Validate name is unique
        cameras = self.list_cameras()
        for camera in cameras:
            if camera.name == name:
                raise DuplicateNameError(f"Camera name already exists: {name}")
        
        # Validate all video_ids exist
        if not video_ids:
            raise ValueError("At least one video_id is required")
        
        for video_id in video_ids:
            try:
                self.video_library.get_video(video_id)
            except VideoNotFoundError:
                raise VideoNotFoundError(f"Video not found: {video_id}")
        
        # Validate auth configuration
        if auth_enabled:
            if not auth_username or not auth_password:
                raise InvalidAuthError("Username and password required when auth is enabled")
            auth_password_hash = self._hash_password(auth_password)
        else:
            auth_password_hash = None
        
        # Generate unique camera ID
        camera_id = generate_id()
        
        # Generate RTSP URL and port
        rtsp_port = self._get_next_port()
        rtsp_url = f"rtsp://localhost:{rtsp_port}/camera/{camera_id}"
        
        # Create VirtualCamera object
        now = datetime.utcnow().isoformat() + 'Z'
        camera = VirtualCamera(
            id=camera_id,
            name=name,
            video_ids=video_ids,
            rtsp_url=rtsp_url,
            rtsp_port=rtsp_port,
            auth_enabled=auth_enabled,
            auth_username=auth_username if auth_enabled else None,
            auth_password_hash=auth_password_hash if auth_enabled else None,
            status="inactive",
            current_video_index=0,
            created_date=now,
            last_modified=now
        )
        
        # Save to cameras.json
        cameras_data = self._load_cameras()
        cameras_data.append(camera.to_dict())
        write_json(self.cameras_path, cameras_data)
        
        return camera
    
    def get_camera(self, camera_id: str) -> VirtualCamera:
        """Retrieve a camera by ID.
        
        Args:
            camera_id: Unique camera identifier
            
        Returns:
            VirtualCamera: VirtualCamera object
            
        Raises:
            CameraNotFoundError: Camera ID doesn't exist
        """
        cameras = self.list_cameras()
        for camera in cameras:
            if camera.id == camera_id:
                return camera
        raise CameraNotFoundError(f"Camera not found: {camera_id}")
    
    def list_cameras(self) -> List[VirtualCamera]:
        """List all cameras.
        
        Returns:
            List[VirtualCamera]: List of VirtualCamera objects
        """
        cameras_data = self._load_cameras()
        return [VirtualCamera.from_dict(c) for c in cameras_data]
    
    def get_camera_rtsp_url(self, camera_id: str) -> str:
        """Get the RTSP URL for a camera.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            str: RTSP URL string
            
        Raises:
            CameraNotFoundError: Camera ID doesn't exist
        """
        camera = self.get_camera(camera_id)
        return camera.rtsp_url
    
    def update_camera(
        self,
        camera_id: str,
        name: Optional[str] = None,
        video_ids: Optional[List[str]] = None,
        auth_enabled: Optional[bool] = None,
        auth_username: Optional[str] = None,
        auth_password: Optional[str] = None,
        status: Optional[str] = None
    ) -> VirtualCamera:
        """Update camera configuration.
        
        Args:
            camera_id: Camera to update
            name: New name
            video_ids: New video IDs
            auth_enabled: New auth setting
            auth_username: New username
            auth_password: New password (plain text)
            
        Returns:
            VirtualCamera: Updated VirtualCamera object
            
        Raises:
            CameraNotFoundError: Camera ID doesn't exist
            DuplicateNameError: New name already exists
            VideoNotFoundError: New video_ids don't exist
        """
        camera = self.get_camera(camera_id)
        cameras = self.list_cameras()
        
        # Update name if provided
        if name is not None:
            # Check for duplicate name (excluding current camera)
            for c in cameras:
                if c.id != camera_id and c.name == name:
                    raise DuplicateNameError(f"Camera name already exists: {name}")
            camera.name = name
        
        # Update video_ids if provided
        if video_ids is not None:
            if not video_ids:
                raise ValueError("At least one video_id is required")
            # Validate all video_ids exist
            for video_id in video_ids:
                try:
                    self.video_library.get_video(video_id)
                except VideoNotFoundError:
                    raise VideoNotFoundError(f"Video not found: {video_id}")
            camera.video_ids = video_ids
            # Reset current_video_index if it's out of bounds
            if camera.current_video_index >= len(video_ids):
                camera.current_video_index = 0
        
        # Update auth settings if provided
        if auth_enabled is not None:
            camera.auth_enabled = auth_enabled
            if auth_enabled:
                if not auth_username or not auth_password:
                    raise InvalidAuthError("Username and password required when auth is enabled")
                camera.auth_username = auth_username
                camera.auth_password_hash = self._hash_password(auth_password)
            else:
                camera.auth_username = None
                camera.auth_password_hash = None
        
        # Update status if provided
        if status is not None:
            if status not in ["active", "inactive", "error"]:
                raise ValueError(f"Invalid status: {status}")
            camera.status = status
        
        # Update last_modified
        camera.last_modified = datetime.utcnow().isoformat() + 'Z'
        
        # Save to cameras.json
        cameras_data = self._load_cameras()
        for i, c in enumerate(cameras_data):
            if c['id'] == camera_id:
                cameras_data[i] = camera.to_dict()
                break
        write_json(self.cameras_path, cameras_data)
        
        return camera
    
    def delete_camera(self, camera_id: str) -> bool:
        """Delete a camera.
        
        Args:
            camera_id: Camera to delete
            
        Returns:
            bool: True if deleted, False if not found
            
        Raises:
            CameraNotFoundError: Camera ID doesn't exist
        """
        camera = self.get_camera(camera_id)
        
        # Stop camera if active (this will be handled by RTSP server service)
        # For now, just update status
        if camera.status == "active":
            camera.status = "inactive"
        
        # Remove from cameras.json
        cameras_data = self._load_cameras()
        cameras_data = [c for c in cameras_data if c['id'] != camera_id]
        write_json(self.cameras_path, cameras_data)
        
        return True
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA256.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password (hex string)
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _get_next_port(self) -> int:
        """Get the next available RTSP port.
        
        Returns:
            int: Port number
        """
        # Simple port allocation: base port + camera count
        cameras = self.list_cameras()
        return self.base_rtsp_port + len(cameras)
    
    def _load_cameras(self) -> List[dict]:
        """Load cameras from JSON file.
        
        Returns:
            List[dict]: List of camera dictionaries
        """
        cameras = read_json(self.cameras_path)
        return cameras if cameras is not None else []

