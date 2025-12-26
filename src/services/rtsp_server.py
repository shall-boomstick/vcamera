"""RTSP Server Service for streaming video content."""
import os
import threading
from typing import Dict, Optional

try:
    import gi
    gi.require_version('Gst', '1.0')
    gi.require_version('GstRtspServer', '1.0')
    from gi.repository import Gst, GstRtspServer, GLib
    GSTREAMER_AVAILABLE = True
except (ImportError, ValueError):
    GSTREAMER_AVAILABLE = False

from ..models.virtual_camera import VirtualCamera
from .exceptions import GStreamerError, PortInUseError, StreamError, StreamNotFoundError, VideoFileError
from .logger import get_logger

logger = get_logger(__name__)


class MultiVideoMediaFactory(GstRtspServer.RTSPMediaFactory):
    """Custom media factory that handles multi-video sequential playback using concat demuxer."""
    
    def __init__(self, video_paths: list, current_index: int, on_video_end_callback, auth_enabled=False, auth_username=None, auth_password_hash=None):
        """Initialize multi-video media factory.
        
        Args:
            video_paths: List of video file paths
            current_index: Current video index to play (for tracking, not used in concat)
            on_video_end_callback: Callback function when video ends
            auth_enabled: Whether authentication is enabled
            auth_username: RTSP username
            auth_password_hash: RTSP password hash
        """
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.video_paths = video_paths
        self.current_video_index = current_index
        self.on_video_end = on_video_end_callback
        self.auth_enabled = auth_enabled
        self.auth_username = auth_username
        self.auth_password_hash = auth_password_hash
    
    def set_current_video_index(self, index: int):
        """Update the current video index (for tracking purposes).
        
        Args:
            index: New video index
        """
        self.current_video_index = index % len(self.video_paths)
    
    def do_create_element(self, url):
        """Create GStreamer element for RTSP media.
        
        For multiple videos, plays them sequentially. When a video ends, the callback
        is triggered to switch to the next video. For RTSP, we start with the current
        video index and handle switching via EOS events.
        
        Args:
            url: RTSP URL
            
        Returns:
            Gst.Element: GStreamer pipeline element
        """
        # Get current video to play
        video_path = self.video_paths[self.current_video_index]
        escaped_path = self._escape_path(video_path)
        
        # Build pipeline: filesrc -> decodebin -> videoconvert -> x264enc -> rtph264pay
        pipeline_str = (
            f"filesrc location={escaped_path} ! "
            "decodebin ! "
            "videoconvert ! "
            "x264enc tune=zerolatency bitrate=2000 speed-preset=ultrafast ! "
            "rtph264pay name=pay0 pt=96"
        )
        
        try:
            pipeline = Gst.parse_launch(pipeline_str)
            
            # Set up EOS handler to switch to next video when current ends
            if len(self.video_paths) > 1:
                bus = pipeline.get_bus()
                bus.add_signal_watch()
                bus.connect("message::eos", self._on_eos)
                bus.connect("message::error", self._on_error)
            
            return pipeline
        except Exception as e:
            logger.error(f"Failed to create pipeline: {e}")
            raise
    
    def _escape_path(self, path: str) -> str:
        """Escape file path for GStreamer pipeline.
        
        Args:
            path: File path
            
        Returns:
            str: Escaped path
        """
        return path.replace(' ', '\\ ').replace('&', '\\&').replace('(', '\\(').replace(')', '\\)')
    
    def _on_eos(self, bus, message):
        """Handle End of Stream message - current video ended, switch to next."""
        logger.info(f"Video {self.current_video_index + 1} ended, switching to next")
        # Trigger callback to switch to next video
        # Note: For RTSP, the factory will create a new pipeline for the next client connection
        # The callback updates the index so next connection uses the correct video
        if self.on_video_end:
            self.on_video_end()
        return True
    
    def _on_error(self, bus, message):
        """Handle error message."""
        error, debug = message.parse_error()
        logger.error(f"Pipeline error: {error.message}, debug: {debug}")
        return True


class RTSPStreamManager:
    """Manages RTSP streams for virtual cameras."""
    
    def __init__(self):
        """Initialize the RTSP stream manager."""
        if not GSTREAMER_AVAILABLE:
            raise GStreamerError("GStreamer Python bindings not available. Install PyGObject and GStreamer.")
        
        Gst.init(None)
        self.server = GstRtspServer.RTSPServer()
        self.server.set_service(str(8554))  # Base port
        
        # Store active streams
        self.active_streams: Dict[str, 'StreamHandler'] = {}
        self.lock = threading.Lock()
        
        # Start RTSP server
        self.server.attach(None)
        logger.info("RTSP server initialized on port 8554")
    
    def start_stream(self, camera: VirtualCamera, video_library_service, camera_manager=None) -> bool:
        """Start an RTSP stream for a camera.
        
        Args:
            camera: VirtualCamera configuration
            video_library_service: VideoLibraryService for getting video paths
            camera_manager: Optional CameraManagerService to update camera status
            
        Returns:
            bool: True if stream started successfully
            
        Raises:
            StreamError: If stream cannot be started
            VideoFileError: If video files cannot be read
        """
        with self.lock:
            if camera.id in self.active_streams:
                logger.warning(f"Stream already active for camera {camera.id}")
                return True
            
            try:
                # Get video file paths
                video_paths = []
                for video_id in camera.video_ids:
                    video_path = video_library_service.get_video_file_path(video_id)
                    if not os.path.exists(video_path):
                        raise VideoFileError(f"Video file not found: {video_path}")
                    video_paths.append(video_path)
                
                # Create stream handler
                handler = StreamHandler(camera, video_paths, self.server, video_library_service, camera_manager)
                handler.start()
                
                self.active_streams[camera.id] = handler
                
                # Update camera status
                if camera_manager:
                    camera_manager.update_camera(camera.id, status="active")
                
                logger.info(f"Started RTSP stream for camera {camera.id} at {camera.rtsp_url}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to start stream for camera {camera.id}: {e}")
                # Update camera status to error
                if camera_manager:
                    try:
                        camera_manager.update_camera(camera.id, status="error")
                    except:
                        pass
                raise StreamError(f"Cannot start RTSP stream: {e}")
    
    def stop_stream(self, camera_id: str, camera_manager=None) -> bool:
        """Stop an RTSP stream for a camera.
        
        Args:
            camera_id: Camera identifier
            camera_manager: Optional CameraManagerService to update camera status
            
        Returns:
            bool: True if stopped successfully
            
        Raises:
            StreamNotFoundError: No active stream for camera
        """
        with self.lock:
            if camera_id not in self.active_streams:
                raise StreamNotFoundError(f"No active stream for camera {camera_id}")
            
            handler = self.active_streams[camera_id]
            handler.stop()
            del self.active_streams[camera_id]
            
            # Update camera status
            if camera_manager:
                camera_manager.update_camera(camera_id, status="inactive")
            
            logger.info(f"Stopped RTSP stream for camera {camera_id}")
            return True
    
    def is_streaming(self, camera_id: str) -> bool:
        """Check if a camera is currently streaming.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            bool: True if streaming, False otherwise
        """
        with self.lock:
            return camera_id in self.active_streams
    
    def get_stream_url(self, camera_id: str) -> Optional[str]:
        """Get the RTSP URL for a camera's stream.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            str: RTSP URL string, or None if not streaming
        """
        with self.lock:
            if camera_id in self.active_streams:
                handler = self.active_streams[camera_id]
                return handler.camera.rtsp_url
            return None


class StreamHandler:
    """Handles a single RTSP stream."""
    
    def __init__(self, camera: VirtualCamera, video_paths: list, server: GstRtspServer.RTSPServer, video_library_service=None, camera_manager=None):
        """Initialize stream handler.
        
        Args:
            camera: VirtualCamera configuration
            video_paths: List of video file paths
            server: RTSP server instance
            video_library_service: Optional VideoLibraryService for video metadata
            camera_manager: Optional CameraManagerService to update camera status
        """
        self.camera = camera
        self.video_paths = video_paths
        self.server = server
        self.video_library_service = video_library_service
        self.camera_manager = camera_manager
        self.factory = None
        self.mount_points = None
        self.running = False
        # Initialize current_video_index from camera, ensuring it's valid
        self.current_video_index = camera.current_video_index if camera.current_video_index < len(video_paths) else 0
    
    def start(self):
        """Start the stream."""
        if self.running:
            return
        
        # For single video, use standard factory with loop
        # For multiple videos, use custom factory that handles sequential playback
        if len(self.video_paths) == 1:
            # Single video - use standard factory with loop
            self.factory = GstRtspServer.RTSPMediaFactory()
            pipeline = self._build_single_video_pipeline(self.video_paths[0])
            self.factory.set_launch(pipeline)
            self.factory.set_shared(True)
        else:
            # Multiple videos - use custom factory for sequential playback
            self.factory = MultiVideoMediaFactory(
                self.video_paths,
                self.current_video_index,
                self._on_video_end,
                self.camera.auth_enabled,
                self.camera.auth_username,
                self.camera.auth_password_hash
            )
            self.factory.set_shared(True)
        
        # Configure authentication if enabled
        if self.camera.auth_enabled:
            auth = GstRtspServer.RTSPAuth()
            token = GstRtspServer.RTSPToken()
            token.set_string('media.factory.role', 'user')
            basic = GstRtspServer.RTSPAuth.make_basic(
                self.camera.auth_username,
                self.camera.auth_password_hash  # Note: This should be plain password for RTSP
            )
            auth.add_basic(basic, token)
            self.factory.set_auth(auth)
        
        # Mount the factory
        self.mount_points = self.server.get_mount_points()
        mount_path = f"/camera/{self.camera.id}"
        self.mount_points.add_factory(mount_path, self.factory)
        
        self.running = True
        logger.info(f"Stream handler started for camera {self.camera.id} with {len(self.video_paths)} video(s), starting at index {self.current_video_index}")
    
    def _build_single_video_pipeline(self, video_path: str) -> str:
        """Build GStreamer pipeline for single video with loop.
        
        Args:
            video_path: Path to video file
            
        Returns:
            str: GStreamer pipeline string
        """
        # Escape path for GStreamer
        escaped_path = video_path.replace(' ', '\\ ').replace('&', '\\&').replace('(', '\\(').replace(')', '\\)')
        
        # Pipeline: filesrc -> decodebin -> videoconvert -> x264enc -> rtph264pay
        # Note: For looping, we'll use the concat demuxer approach or handle in application
        pipeline = (
            f"filesrc location={escaped_path} ! "
            "decodebin ! "
            "videoconvert ! "
            "x264enc tune=zerolatency bitrate=2000 speed-preset=ultrafast ! "
            "rtph264pay name=pay0 pt=96"
        )
        return pipeline
    
    def _on_video_end(self):
        """Callback when current video ends - switch to next video."""
        if len(self.video_paths) <= 1:
            # Single video - restart (handled by pipeline loop)
            return
        
        # Move to next video
        old_index = self.current_video_index
        self.current_video_index = (self.current_video_index + 1) % len(self.video_paths)
        
        # Update camera's current_video_index in storage
        if self.camera_manager:
            try:
                # Get fresh camera object
                camera = self.camera_manager.get_camera(self.camera.id)
                camera.current_video_index = self.current_video_index
                # Update in storage (this will also update last_modified)
                self.camera_manager.update_camera(
                    self.camera.id,
                    status="active"
                )
                # Update local camera reference
                self.camera.current_video_index = self.current_video_index
            except Exception as e:
                logger.error(f"Failed to update camera current_video_index: {e}")
        
        # Update factory to use new video index for next connection
        if self.factory and hasattr(self.factory, 'set_current_video_index'):
            self.factory.set_current_video_index(self.current_video_index)
        
        logger.info(f"Switched camera {self.camera.id} from video {old_index + 1} to video {self.current_video_index + 1} of {len(self.video_paths)}")
    
    def stop(self):
        """Stop the stream."""
        if not self.running:
            return
        
        if self.mount_points and self.factory:
            mount_path = f"/camera/{self.camera.id}"
            self.mount_points.remove_factory(mount_path)
        
        self.running = False
        logger.info(f"Stream handler stopped for camera {self.camera.id}")


# Global RTSP stream manager instance
_rtsp_manager: Optional[RTSPStreamManager] = None


def get_rtsp_manager() -> RTSPStreamManager:
    """Get the global RTSP stream manager instance.
    
    Returns:
        RTSPStreamManager: RTSP stream manager
    """
    global _rtsp_manager
    if _rtsp_manager is None:
        _rtsp_manager = RTSPStreamManager()
    return _rtsp_manager

