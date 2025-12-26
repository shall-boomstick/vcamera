   source venv/bin/activate# RTSP Server Service Contract

**Service**: RTSP Streaming  
**Purpose**: Handle RTSP protocol streaming of video content

## Methods

### start_stream(camera: VirtualCamera) -> bool

Starts an RTSP stream for a camera.

**Parameters**:
- `camera` (VirtualCamera): Camera configuration

**Returns**: True if stream started successfully

**Behavior**:
1. Initialize GStreamer RTSP server on camera's port
2. Configure authentication if camera.auth_enabled is True
3. Create media factory for video playback
4. Set up video source from camera's video files
5. Configure loop playback (restart video when finished)
6. Configure sequential playback if multiple videos
7. Start RTSP server
8. Begin video playback loop

**Errors**:
- `PortInUseError`: RTSP port already in use
- `GStreamerError`: GStreamer initialization failed
- `VideoFileError`: Cannot read video files

### stop_stream(camera_id: str) -> bool

Stops an RTSP stream for a camera.

**Parameters**:
- `camera_id` (str): Camera identifier

**Returns**: True if stopped successfully

**Behavior**:
1. Find active stream for camera
2. Stop video playback
3. Stop RTSP server
4. Clean up resources

**Errors**:
- `StreamNotFoundError`: No active stream for camera

### is_streaming(camera_id: str) -> bool

Checks if a camera is currently streaming.

**Parameters**:
- `camera_id` (str): Camera identifier

**Returns**: True if streaming, False otherwise

### get_stream_url(camera_id: str) -> str

Gets the RTSP URL for a camera's stream.

**Parameters**:
- `camera_id` (str): Camera identifier

**Returns**: RTSP URL string

## Internal Behavior

### Video Playback Loop

For single video:
1. Read video file using OpenCV
2. Encode frames to H.264 via GStreamer
3. Stream frames via RTSP
4. When video ends, restart from beginning
5. Continue until stream stopped

For multiple videos:
1. Play first video in sequence
2. When video ends, move to next video
3. When last video ends, restart from first video
4. Continue until stream stopped

### Authentication

If authentication enabled:
- RTSP server requires credentials on connection
- Validate username/password against camera.auth_username and hashed password
- Reject connections without valid credentials
- Return 401 Unauthorized for invalid credentials

