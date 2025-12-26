# Data Model: Virtual Camera Server

**Date**: 2025-12-22  
**Feature**: Virtual Camera Server Application

## Entities

### Video

Represents an uploaded video file stored in the library.

**Attributes**:
- `id` (string): Unique identifier (UUID or filename-based)
- `filename` (string): Original filename from upload
- `file_path` (string): Filesystem path to video file (relative to `videos/` directory)
- `file_size` (integer): File size in bytes
- `duration` (float): Video duration in seconds (extracted via OpenCV)
- `width` (integer): Video frame width in pixels
- `height` (integer): Video frame height in pixels
- `fps` (float): Frames per second
- `format` (string): Video format/codec (e.g., "mp4", "avi")
- `upload_date` (string): ISO 8601 timestamp of upload
- `metadata` (dict): Additional metadata (optional)

**Storage**: Video files stored in `videos/` directory. Metadata stored in `data/videos.json` as JSON array.

**Validation Rules**:
- Filename must be non-empty
- File must exist at file_path
- File size must be > 0
- Duration must be > 0
- Width and height must be > 0
- FPS must be > 0

**Relationships**:
- Can be assigned to zero or more VirtualCamera instances

### VirtualCamera

Represents a virtual camera instance that streams video content via RTSP.

**Attributes**:
- `id` (string): Unique identifier (UUID)
- `name` (string): User-provided name for the camera
- `video_ids` (list of strings): List of Video IDs assigned to this camera (order matters for sequential playback)
- `rtsp_url` (string): RTSP stream URL (e.g., "rtsp://localhost:8554/camera/{id}")
- `rtsp_port` (integer): RTSP server port for this camera
- `auth_enabled` (boolean): Whether RTSP authentication is enabled
- `auth_username` (string, optional): RTSP authentication username (if auth_enabled)
- `auth_password_hash` (string, optional): Hashed RTSP authentication password (if auth_enabled)
- `status` (string): Camera status - "active" (streaming), "inactive" (stopped), "error"
- `current_video_index` (integer): Index in video_ids of currently playing video (for multi-video cameras)
- `created_date` (string): ISO 8601 timestamp of creation
- `last_modified` (string): ISO 8601 timestamp of last modification

**Storage**: Stored in `data/cameras.json` as JSON array.

**Validation Rules**:
- Name must be non-empty and unique
- Must have at least one video_id in video_ids
- All video_ids must reference existing Video entities
- If auth_enabled is true, auth_username and auth_password_hash must be provided
- Status must be one of: "active", "inactive", "error"
- current_video_index must be >= 0 and < len(video_ids)

**State Transitions**:
- `inactive` → `active`: When camera starts streaming
- `active` → `inactive`: When camera stops streaming
- `active` → `error`: When streaming fails
- `error` → `inactive`: When error is cleared
- `error` → `active`: When streaming is retried after error

**Relationships**:
- References one or more Video entities via video_ids
- Independent - cameras don't reference each other

### UserSession

Represents an authenticated user session in the web interface.

**Attributes**:
- `username` (string): Authenticated username
- `session_id` (string): Unique session identifier
- `login_time` (string): ISO 8601 timestamp of login
- `last_activity` (string): ISO 8601 timestamp of last activity

**Storage**: In-memory during application runtime. Not persisted (new session on each app start).

**Validation Rules**:
- Username must match stored credentials
- Session expires after inactivity (configurable timeout)

**Relationships**:
- No persistent relationships (ephemeral session data)

### UserCredentials

Stored authentication credentials for web interface access.

**Attributes**:
- `username` (string): Login username
- `password_hash` (string): Hashed password (using hashlib.sha256)
- `created_date` (string): ISO 8601 timestamp of creation

**Storage**: Stored in `data/credentials.json` as JSON object (single user for MVP).

**Validation Rules**:
- Username must be non-empty
- Password hash must be non-empty (64 character hex string for SHA256)

**Security Notes**:
- Passwords are hashed, never stored in plain text
- For production, consider adding salt (not required for MVP per KISS)

## Data Storage Structure

```
project_root/
├── videos/              # Video files directory
│   ├── video1.mp4
│   ├── video2.avi
│   └── ...
├── data/                  # Metadata directory
│   ├── videos.json        # Video metadata array
│   ├── cameras.json       # Camera configurations array
│   └── credentials.json   # User credentials (single object)
```

### videos.json Structure

```json
[
  {
    "id": "uuid-here",
    "filename": "sample.mp4",
    "file_path": "sample.mp4",
    "file_size": 1048576,
    "duration": 30.5,
    "width": 1920,
    "height": 1080,
    "fps": 30.0,
    "format": "mp4",
    "upload_date": "2025-12-22T10:00:00Z",
    "metadata": {}
  }
]
```

### cameras.json Structure

```json
[
  {
    "id": "uuid-here",
    "name": "Front Door Camera",
    "video_ids": ["video-uuid-1", "video-uuid-2"],
    "rtsp_url": "rtsp://localhost:8554/camera/uuid-here",
    "rtsp_port": 8554,
    "auth_enabled": true,
    "auth_username": "camera_user",
    "auth_password_hash": "hashed-password-here",
    "status": "active",
    "current_video_index": 0,
    "created_date": "2025-12-22T10:00:00Z",
    "last_modified": "2025-12-22T10:05:00Z"
  }
]
```

### credentials.json Structure

```json
{
  "username": "admin",
  "password_hash": "sha256-hash-here",
  "created_date": "2025-12-22T10:00:00Z"
}
```

## Data Operations

### Video Operations
- **Create**: Upload file, extract metadata, save to videos/ and add entry to videos.json
- **Read**: List all videos, get video by ID, read video file
- **Update**: Not supported (videos are immutable after upload)
- **Delete**: Remove file from videos/, remove entry from videos.json, remove references from cameras

### VirtualCamera Operations
- **Create**: Generate ID, validate video_ids, create entry in cameras.json
- **Read**: List all cameras, get camera by ID, get camera by name
- **Update**: Modify name, video_ids, auth settings, status
- **Delete**: Stop streaming, remove entry from cameras.json

### UserCredentials Operations
- **Create**: Hash password, save to credentials.json (first-time setup)
- **Read**: Load from credentials.json for authentication
- **Update**: Change password (re-hash and save)
- **Delete**: Not supported (would lock out user)

## Constraints and Business Rules

1. **Video Deletion**: Cannot delete a video that is assigned to an active camera. Must stop/delete camera first.
2. **Camera Naming**: Camera names must be unique within the system.
3. **Video Assignment**: All videos assigned to a camera must exist. If a video is deleted, cameras referencing it must be updated or deleted.
4. **RTSP URL Uniqueness**: Each camera must have a unique RTSP URL/port combination.
5. **Authentication**: If auth_enabled, both username and password must be provided.

## Migration and Compatibility

- JSON files can be manually edited for debugging
- Video files can be added/removed from videos/ directory (requires metadata update)
- Backup: Copy `videos/` and `data/` directories
- No schema versioning needed for MVP (simple JSON structure)

