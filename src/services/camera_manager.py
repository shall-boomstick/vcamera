"""Camera Manager Service for managing virtual cameras."""
import hashlib
import base64
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlparse, urlunparse

from ..models.virtual_camera import VirtualCamera
from .exceptions import CameraNotFoundError, DuplicateNameError, InvalidAuthError, VideoNotFoundError
from .storage import ensure_directories, get_cameras_path, read_json, write_json
from .utils import generate_id
from .logger import get_logger

logger = get_logger(__name__)


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
        """Create a new virtual camera."""
        logger.info(f"Creating camera: {name} with {len(video_ids)} video(s)")
        
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
            # Store plain password encrypted for RTSP use (simple base64 encoding)
            auth_password_rtsp = self._encrypt_password(auth_password)
        else:
            auth_password_hash = None
            auth_password_rtsp = None
        
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
            auth_password_rtsp=auth_password_rtsp if auth_enabled else None,
            status="inactive",
            current_video_index=0,
            created_date=now,
            last_modified=now
        )
        
        # Save to cameras.json
        cameras_data = self._load_cameras()
        cameras_data.append(camera.to_dict())
        write_json(self.cameras_path, cameras_data)
        
        logger.info(f"Camera created successfully: {camera.id} ({camera.name})")
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
    
    def _normalize_camera_rtsp_url(self, camera: VirtualCamera) -> VirtualCamera:
        """Normalize camera RTSP URL to use correct port.
        
        Ensures all cameras use port 8554 with their unique mount point.
        
        Args:
            camera: VirtualCamera object
            
        Returns:
            VirtualCamera: Camera with normalized RTSP URL
        """
        # Parse current RTSP URL
        parsed = urlparse(camera.rtsp_url)
        
        # Ensure port is 8554 and path is /camera/{camera_id}
        correct_path = f"/camera/{camera.id}"
        if parsed.port != self.base_rtsp_port or parsed.path != correct_path:
            # Update RTSP URL
            normalized_url = urlunparse((
                parsed.scheme,
                f"{parsed.hostname}:{self.base_rtsp_port}",
                correct_path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            
            # Only update if URL actually changed
            if normalized_url != camera.rtsp_url:
                logger.info(
                    f"Normalizing RTSP URL for camera {camera.id}: "
                    f"{camera.rtsp_url} -> {normalized_url}"
                )
                camera.rtsp_url = normalized_url
                camera.rtsp_port = self.base_rtsp_port
                
                # Save the corrected URL back to storage
                cameras_data = self._load_cameras()
                for i, c in enumerate(cameras_data):
                    if c['id'] == camera.id:
                        cameras_data[i] = camera.to_dict()
                        write_json(self.cameras_path, cameras_data)
                        break
        
        return camera
    
    def list_cameras(self) -> List[VirtualCamera]:
        """List all cameras.
        
        Returns:
            List[VirtualCamera]: List of VirtualCamera objects
        """
        cameras_data = self._load_cameras()
        cameras = []
        for c in cameras_data:
            camera = VirtualCamera.from_dict(c)
            # Normalize RTSP URL to use correct port
            camera = self._normalize_camera_rtsp_url(camera)
            cameras.append(camera)
        return cameras
    
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
                if not auth_username:
                    raise InvalidAuthError("Username required when auth is enabled")
                camera.auth_username = auth_username
                # Only update password if provided (allow keeping current password)
                if auth_password is not None:
                    camera.auth_password_hash = self._hash_password(auth_password)
                    camera.auth_password_rtsp = self._encrypt_password(auth_password)
                # If password not provided and auth was already enabled, keep current password
                elif not camera.auth_password_hash:
                    raise InvalidAuthError("Password required when enabling auth for the first time")
            else:
                camera.auth_username = None
                camera.auth_password_hash = None
                camera.auth_password_rtsp = None
        
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
        logger.info(f"Deleting camera: {camera.id} ({camera.name})")
        
        # Stop camera if active (this will be handled by RTSP server service)
        # For now, just update status
        if camera.status == "active":
            logger.warning(f"Camera {camera.id} is active, status will be updated to inactive")
            camera.status = "inactive"
        
        # Remove from cameras.json
        cameras_data = self._load_cameras()
        cameras_data = [c for c in cameras_data if c['id'] != camera_id]
        write_json(self.cameras_path, cameras_data)
        
        logger.info(f"Camera {camera.id} deleted successfully")
        return True
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA256.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password (hex string)
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _encrypt_password(self, password: str) -> str:
        """Encrypt password for RTSP storage (simple base64 encoding).
        
        Note: This is not secure encryption, just obfuscation for KISS principle.
        For production, use proper encryption with a key.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Encrypted password (base64)
        """
        return base64.b64encode(password.encode()).decode()
    
    def _decrypt_password(self, encrypted: str) -> str:
        """Decrypt password from RTSP storage.
        
        Args:
            encrypted: Encrypted password (base64)
            
        Returns:
            str: Plain text password
        """
        return base64.b64decode(encrypted.encode()).decode()
    
    def _get_next_port(self) -> int:
        """Get the RTSP port for cameras.
        
        All cameras use the same RTSP server port (8554) with different
        mount points (/camera/{camera_id}).
        
        Returns:
            int: Port number (always 8554)
        """
        return self.base_rtsp_port
    
    def _load_cameras(self) -> List[dict]:
        """Load cameras from JSON file.
        
        Returns:
            List[dict]: List of camera dictionaries
        """
        cameras = read_json(self.cameras_path)
        return cameras if cameras is not None else []

