# Camera Manager Service Contract

**Service**: Virtual Camera Lifecycle Management  
**Purpose**: Create, configure, start, stop, and manage virtual cameras

## Methods

### create_camera(name: str, video_ids: List[str], auth_enabled: bool = False, auth_username: str = None, auth_password: str = None) -> VirtualCamera

Creates a new virtual camera.

**Parameters**:
- `name` (str): User-provided camera name (must be unique)
- `video_ids` (List[str]): List of video IDs to assign (order matters)
- `auth_enabled` (bool): Whether to enable RTSP authentication
- `auth_username` (str, optional): RTSP username if auth enabled
- `auth_password` (str, optional): RTSP password if auth enabled

**Returns**: VirtualCamera object

**Behavior**:
1. Validate name is unique
2. Validate all video_ids exist
3. Generate unique camera ID
4. Generate RTSP URL and port
5. Hash password if auth enabled
6. Create VirtualCamera entity with status "inactive"
7. Save to `data/cameras.json`
8. Return VirtualCamera object

**Errors**:
- `DuplicateNameError`: Camera name already exists
- `VideoNotFoundError`: One or more video_ids don't exist
- `InvalidAuthError`: Auth enabled but username/password missing

### get_camera(camera_id: str) -> VirtualCamera

Retrieves a camera by ID.

**Parameters**:
- `camera_id` (str): Unique camera identifier

**Returns**: VirtualCamera object

**Errors**:
- `CameraNotFoundError`: Camera ID doesn't exist

### list_cameras() -> List[VirtualCamera]

Lists all cameras.

**Returns**: List of VirtualCamera objects

### update_camera(camera_id: str, name: str = None, video_ids: List[str] = None, auth_enabled: bool = None, auth_username: str = None, auth_password: str = None) -> VirtualCamera

Updates camera configuration.

**Parameters**:
- `camera_id` (str): Camera to update
- `name` (str, optional): New name
- `video_ids` (List[str], optional): New video IDs
- `auth_enabled` (bool, optional): New auth setting
- `auth_username` (str, optional): New username
- `auth_password` (str, optional): New password

**Returns**: Updated VirtualCamera object

**Behavior**:
- Only updates provided parameters
- Validates name uniqueness if name changed
- Validates video_ids exist if changed
- Updates last_modified timestamp
- If camera is active, changes take effect on next restart

**Errors**:
- `CameraNotFoundError`: Camera ID doesn't exist
- `DuplicateNameError`: New name already exists
- `VideoNotFoundError`: New video_ids don't exist

### start_camera(camera_id: str) -> bool

Starts streaming from a camera.

**Parameters**:
- `camera_id` (str): Camera to start

**Returns**: True if started successfully

**Behavior**:
1. Load camera configuration
2. Initialize RTSP server for this camera
3. Start video playback loop (first video or current_video_index)
4. Set status to "active"
5. Update cameras.json

**Errors**:
- `CameraNotFoundError`: Camera ID doesn't exist
- `StreamError`: Cannot start RTSP stream (port in use, etc.)
- `VideoNotFoundError`: Assigned videos don't exist

### stop_camera(camera_id: str) -> bool

Stops streaming from a camera.

**Parameters**:
- `camera_id` (str): Camera to stop

**Returns**: True if stopped successfully

**Behavior**:
1. Stop RTSP server for this camera
2. Stop video playback
3. Set status to "inactive"
4. Update cameras.json

**Errors**:
- `CameraNotFoundError`: Camera ID doesn't exist

### delete_camera(camera_id: str) -> bool

Deletes a camera.

**Parameters**:
- `camera_id` (str): Camera to delete

**Returns**: True if deleted, False if not found

**Behavior**:
1. Stop camera if active
2. Remove entry from `data/cameras.json`
3. Return True

**Errors**:
- `CameraNotFoundError`: Camera ID doesn't exist

### get_camera_rtsp_url(camera_id: str) -> str

Gets the RTSP URL for a camera.

**Parameters**:
- `camera_id` (str): Camera identifier

**Returns**: RTSP URL string (e.g., "rtsp://localhost:8554/camera/{id}")

**Errors**:
- `CameraNotFoundError`: Camera ID doesn't exist

