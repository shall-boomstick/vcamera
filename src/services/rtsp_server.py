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
    
    def __init__(self, video_paths: list, current_index: int, on_video_end_callback, auth_enabled=False, auth_username=None, auth_password_rtsp=None):
        """Initialize multi-video media factory.
        
        Args:
            video_paths: List of video file paths
            current_index: Current video index to play (for tracking, not used in concat)
            on_video_end_callback: Callback function when video ends
            auth_enabled: Whether authentication is enabled
            auth_username: RTSP username
            auth_password_rtsp: RTSP password (encrypted)
        """
        GstRtspServer.RTSPMediaFactory.__init__(self)
        self.video_paths = video_paths
        self.current_video_index = current_index
        self.on_video_end = on_video_end_callback
        self.auth_enabled = auth_enabled
        self.auth_username = auth_username
        self.auth_password_rtsp = auth_password_rtsp
        
        # Enable shared media so multiple clients share the same stream
        # and we can handle looping properly
        self.set_shared(True)
    
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

        logger.info(
            f"Creating RTSP pipeline for video {self.current_video_index + 1}/"
            f"{len(self.video_paths)}: {video_path}"
        )

        # Build pipeline - looping is handled via seeking in do_configure
        if len(self.video_paths) == 1:
            # Single video - looping handled via seek on EOS
            source = f"filesrc location={escaped_path}"
        else:
            # Multiple videos - use current video with queue buffer
            source = f"filesrc location={escaped_path} ! queue max-size-buffers=200 max-size-time=2000000000 leaky=downstream"
        
        # Check available encoders
        x264_available = Gst.ElementFactory.find("x264enc") is not None
        
        if x264_available:
            encoder = "x264enc bitrate=2000 speed-preset=ultrafast tune=zerolatency key-int-max=30"
            logger.info("Using x264enc encoder")
        else:
            # Use openh264enc - let it auto-configure without parameters
            # Specifying parameters causes cmInitParaError
            encoder = "openh264enc"
            logger.info("Using openh264enc encoder (x264enc not available) - no parameters to avoid initialization errors")
        
        if x264_available:
            pipeline_str = (
                f"{source} ! "
                "decodebin ! "
                "videoconvert ! "
                "video/x-raw,format=I420 ! "
                f"{encoder} ! "
                "video/x-h264,profile=baseline ! "
                "rtph264pay name=pay0 pt=96 config-interval=1"
            )
        else:
            # Use openh264enc with forced 640x480 resolution to avoid encoder issues
            # Use capsfilter element for better compatibility
            logger.info("Using openh264enc with forced 640x480 resolution")
            pipeline_str = (
                f"{source} ! "
                "decodebin ! "
                "videoconvert ! "
                "videoscale ! "
                "videorate ! "
                "capsfilter caps=video/x-raw,format=I420,width=640,height=480,framerate=25/1 ! "
                "openh264enc ! "
                "h264parse ! "
                "rtph264pay name=pay0 pt=96 config-interval=1"
            )

        try:
            pipeline = Gst.parse_launch(pipeline_str)

            # Set up error handler to catch encoder errors
            bus = pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message::error", self._on_error)
            
            # Set up EOS handler to switch to next video when current ends
            if len(self.video_paths) > 1:
                bus.connect("message::eos", self._on_eos)

            logger.info(
                f"Created pipeline for video {self.current_video_index + 1}/"
                f"{len(self.video_paths)}: {video_path}"
            )
            return pipeline
        except Exception as e:
            logger.error(
                f"Failed to create pipeline for video {video_path}: {e}",
                exc_info=True
            )
            raise GStreamerError(f"Pipeline creation failed: {e}")
    
    def _escape_path(self, path: str) -> str:
        """Escape file path for GStreamer pipeline.

        Args:
            path: File path

        Returns:
            str: Escaped path
        """
        # Escape special characters for GStreamer
        return path.replace(' ', '\\ ').replace('&', '\\&').replace('(', '\\(').replace(')', '\\)').replace('[', '\\[').replace(']', '\\]')
    
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
        
        # Log OpenH264 specific errors with more detail
        if "OpenH264" in str(error.message) or "cmInitParaError" in str(error.message):
            logger.error(
                f"OpenH264 encoder error detected. This may indicate an issue with "
                f"encoder parameters or video format. Debug info: {debug}"
            )
            logger.error(
                "If this error persists, try: "
                "1. Restart the camera stream to pick up new encoder settings "
                "2. Check video file format compatibility "
                "3. Consider installing x264enc for better stability"
            )
        
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
        self.server.set_address("0.0.0.0")  # Bind to all interfaces
        
        # Store active streams
        self.active_streams: Dict[str, 'StreamHandler'] = {}
        self.lock = threading.Lock()
        self.main_context = None
        self.main_loop = None
        self.loop_thread = None
        self.server_ready = threading.Event()
        
        # Start main loop in background thread
        def run_main_loop():
            try:
                # Use the default main context
                self.main_context = GLib.MainContext.default()

                # Create main loop with default context
                self.main_loop = GLib.MainLoop(self.main_context)

                # Attach server to the default context
                source_id = self.server.attach(self.main_context)
                if source_id == 0:
                    logger.error("Failed to attach RTSP server to main context")
                    self.server_ready.set()
                    return

                logger.info(
                    f"RTSP server attached (source_id={source_id}) on port 8554"
                )

                # Signal that server is ready
                self.server_ready.set()

                # Run the main loop (this blocks)
                self.main_loop.run()
            except Exception as e:
                logger.error(f"Error in RTSP server main loop: {e}",
                             exc_info=True)
                import traceback
                logger.error(traceback.format_exc())
                self.server_ready.set()  # Signal even on error

        self.loop_thread = threading.Thread(target=run_main_loop, daemon=True)
        self.loop_thread.start()

        # Wait for server to be ready (with timeout)
        if not self.server_ready.wait(timeout=2.0):
            logger.warning("RTSP server main loop did not start within timeout")
        else:
            logger.info("RTSP server initialized on port 8554 (bound to 0.0.0.0)")
    
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
                # Get video file paths with validation
                video_paths = []
                for video_id in camera.video_ids:
                    try:
                        video_path = video_library_service.get_video_file_path(
                            video_id
                        )
                        if not os.path.exists(video_path):
                            raise VideoFileError(
                                f"Video file not found: {video_path}"
                            )
                        if not os.access(video_path, os.R_OK):
                            raise VideoFileError(
                                f"Video file is not readable: {video_path}"
                            )
                        
                        # Test if GStreamer can open the file
                        try:
                            test_pipeline = (
                                f"filesrc location={video_path} ! "
                                "decodebin ! fakesink"
                            )
                            test_pipe = Gst.parse_launch(test_pipeline)
                            test_pipe.set_state(Gst.State.NULL)
                            del test_pipe
                        except Exception as test_e:
                            logger.warning(
                                f"GStreamer test failed for {video_path}: "
                                f"{test_e}. Will attempt anyway."
                            )
                        
                        video_paths.append(video_path)
                    except VideoNotFoundError as e:
                        logger.error(
                            f"Video {video_id} not found for camera "
                            f"{camera.id}: {e}"
                        )
                        raise StreamError(
                            f"Cannot start stream: video {video_id} not found"
                        )
                    except Exception as e:
                        logger.error(f"Error accessing video {video_id}: {e}")
                        raise VideoFileError(f"Cannot access video file: {e}")
                
                if not video_paths:
                    raise StreamError("No valid video files found for camera")

                # Log video files being used
                logger.info(
                    f"Starting stream with {len(video_paths)} video file(s) "
                    f"for camera {camera.id}"
                )
                for i, video_path in enumerate(video_paths):
                    logger.debug(
                        f"Video {i+1}/{len(video_paths)}: {video_path}"
                    )

                # Create stream handler
                try:
                    handler = StreamHandler(
                        camera, video_paths, self.server,
                        video_library_service, camera_manager,
                        self.main_context
                    )
                    handler.start()
                    
                    # Verify mount point was actually registered
                    mount_path = f"/camera/{camera.id}"
                    mount_points = self.server.get_mount_points()
                    if not mount_points.match(mount_path):
                        raise StreamError(
                            f"Mount point {mount_path} failed to register"
                        )
                    
                except GStreamerError as e:
                    logger.error(
                        f"GStreamer error starting stream for camera "
                        f"{camera.id}: {e}", exc_info=True
                    )
                    raise StreamError(f"GStreamer error: {e}")
                except Exception as e:
                    logger.error(
                        f"Error creating stream handler for camera "
                        f"{camera.id}: {e}", exc_info=True
                    )
                    raise StreamError(f"Failed to create stream handler: {e}")
                
                self.active_streams[camera.id] = handler
                
                # Update camera status only after successful registration
                if camera_manager:
                    try:
                        camera_manager.update_camera(camera.id, status="active")
                    except Exception as e:
                        logger.warning(f"Failed to update camera status: {e}")
                
                logger.info(
                    f"Started RTSP stream for camera {camera.id} at "
                    f"{camera.rtsp_url}"
                )
                return True
                
            except (StreamError, VideoFileError, GStreamerError):
                # Re-raise these specific errors
                raise
            except Exception as e:
                logger.error(f"Failed to start stream for camera {camera.id}: {e}", exc_info=True)
                # Update camera status to error
                if camera_manager:
                    try:
                        camera_manager.update_camera(camera.id, status="error")
                    except Exception as update_error:
                        logger.error(f"Failed to update camera status to error: {update_error}")
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
    
    def get_server_info(self) -> dict:
        """Get RTSP server information.

        Returns:
            dict: Server information including address, port, and active streams
        """
        with self.lock:
            return {
                'address': (
                    self.server.get_address()
                    if hasattr(self.server, 'get_address')
                    else '0.0.0.0'
                ),
                'port': (
                    self.server.get_service()
                    if hasattr(self.server, 'get_service')
                    else '8554'
                ),
                'active_streams': list(self.active_streams.keys()),
                'main_loop_running': (
                    self.main_loop.is_running()
                    if self.main_loop else False
                )
            }
    
    def is_mount_point_registered(self, camera_id: str) -> bool:
        """Check if a camera's mount point is registered.

        Args:
            camera_id: Camera identifier

        Returns:
            bool: True if mount point is registered
        """
        mount_path = f"/camera/{camera_id}"
        mount_points = self.server.get_mount_points()
        return mount_points.match(mount_path) is not None
    
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
    
    def __init__(self, camera: VirtualCamera, video_paths: list, server: GstRtspServer.RTSPServer, video_library_service=None, camera_manager=None, main_context=None):
        """Initialize stream handler.
        
        Args:
            camera: VirtualCamera configuration
            video_paths: List of video file paths
            server: RTSP server instance
            video_library_service: Optional VideoLibraryService for video metadata
            camera_manager: Optional CameraManagerService to update camera status
            main_context: Optional GLib.MainContext for thread-safe operations
        """
        self.camera = camera
        self.video_paths = video_paths
        self.server = server
        self.video_library_service = video_library_service
        self.camera_manager = camera_manager
        self.main_context = main_context
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
                self.camera.auth_password_rtsp
            )
            self.factory.set_shared(True)
        
        # Configure authentication if enabled
        if self.camera.auth_enabled and self.camera.auth_username and self.camera.auth_password_rtsp:
            # Decrypt RTSP password
            import base64
            try:
                rtsp_password = base64.b64decode(self.camera.auth_password_rtsp.encode()).decode()
            except Exception:
                logger.error(f"Failed to decrypt RTSP password for camera {self.camera.id}")
                rtsp_password = None
            
            if rtsp_password:
                auth = GstRtspServer.RTSPAuth()
                token = GstRtspServer.RTSPToken()
                token.set_string('media.factory.role', 'user')
                basic = GstRtspServer.RTSPAuth.make_basic(
                    self.camera.auth_username,
                    rtsp_password  # Plain password for RTSP
                )
                auth.add_basic(basic, token)
                self.factory.set_auth(auth)
                logger.info(f"RTSP authentication enabled for camera {self.camera.id}")
        
        # Mount the factory
        mount_path = f"/camera/{self.camera.id}"
        rtsp_url = f"rtsp://localhost:8554{mount_path}"
        
        # Add factory directly - GStreamer's mount points are thread-safe
        # The GLib.idle_add approach was failing because it was scheduling on the wrong context
        try:
            self.mount_points = self.server.get_mount_points()
            self.mount_points.add_factory(mount_path, self.factory)
            logger.info(f"Stream handler started for camera {self.camera.id}")
            logger.info(f"  Mount point: {mount_path}")
            logger.info(f"  RTSP URL: {rtsp_url}")
            logger.info(f"  Videos: {len(self.video_paths)} video(s), starting at index {self.current_video_index}")
            
            # Verify mount point was added
            if self.mount_points.match(mount_path):
                logger.info(f"Verified mount point {mount_path} is registered")
            else:
                logger.error(f"Mount point {mount_path} registration verification failed")
        except Exception as e:
            logger.error(f"Error adding factory to mount points: {e}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
            raise
        
        self.running = True
    
    def _build_single_video_pipeline(self, video_path: str) -> str:
        """Build GStreamer pipeline for single video with seamless looping.

        Args:
            video_path: Path to video file

        Returns:
            str: GStreamer pipeline string (wrapped in parentheses for RTSP)
        """
        # Escape path for GStreamer
        escaped_path = video_path.replace(' ', '\\ ').replace('&', '\\&').replace('(', '\\(').replace(')', '\\)').replace('[', '\\[').replace(']', '\\]')

        # Pipeline must be wrapped in ( ) for GstRtspServer.set_launch()
        # Check available encoders
        x264_available = Gst.ElementFactory.find("x264enc") is not None
        
        if x264_available:
            encoder = "x264enc bitrate=2000 speed-preset=ultrafast tune=zerolatency key-int-max=30"
            logger.info("Using x264enc encoder for single video pipeline")
            pipeline = (
                f"( filesrc location={escaped_path} ! "
                "decodebin ! "
                "videoconvert ! "
                "video/x-raw,format=I420 ! "
                f"{encoder} ! "
                "video/x-h264,profile=baseline ! "
                "rtph264pay name=pay0 pt=96 config-interval=1 )"
            )
        else:
            # Use decodebin - escape spaces in path with backslash
            safe_path = video_path.replace(' ', '\\ ')
            logger.info(f"Using decodebin pipeline for single video: {video_path}")
            # Use capsfilter element instead of inline caps for better compatibility
            pipeline = (
                f"( filesrc location={safe_path} ! "
                "decodebin ! "
                "videoconvert ! "
                "videoscale ! "
                "videorate ! "
                "capsfilter caps=video/x-raw,format=I420,width=640,height=480,framerate=25/1 ! "
                "openh264enc ! "
                "h264parse ! "
                "rtph264pay name=pay0 pt=96 config-interval=1 )"
            )
        logger.info(f"Pipeline string: {pipeline}")
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

