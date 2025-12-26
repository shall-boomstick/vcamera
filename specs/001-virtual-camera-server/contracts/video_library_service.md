# Video Library Service Contract

**Service**: Video Library Management  
**Purpose**: Handle video upload, storage, retrieval, and metadata management

## Methods

### upload_video(file_path: str, filename: str) -> Video

Uploads a video file to the library.

**Parameters**:
- `file_path` (str): Source file path on user's computer
- `filename` (str): Original filename

**Returns**: Video object with metadata

**Behavior**:
1. Copy file to `videos/` directory
2. Extract video metadata using OpenCV (duration, dimensions, fps, format)
3. Generate unique ID for video
4. Create Video entity with metadata
5. Save metadata to `data/videos.json`
6. Return Video object

**Errors**:
- `FileNotFoundError`: Source file doesn't exist
- `InvalidVideoError`: File is not a valid video or unsupported format
- `StorageError`: Cannot write to videos/ directory

### get_video(video_id: str) -> Video

Retrieves a video by ID.

**Parameters**:
- `video_id` (str): Unique video identifier

**Returns**: Video object

**Errors**:
- `VideoNotFoundError`: Video ID doesn't exist

### list_videos() -> List[Video]

Lists all videos in the library.

**Returns**: List of Video objects

**Behavior**:
- Loads from `data/videos.json`
- Returns empty list if no videos

### delete_video(video_id: str) -> bool

Deletes a video from the library.

**Parameters**:
- `video_id` (str): Unique video identifier

**Returns**: True if deleted, False if not found

**Behavior**:
1. Check if video is assigned to any camera
2. If assigned, raise `VideoInUseError`
3. Delete video file from `videos/` directory
4. Remove entry from `data/videos.json`
5. Return True

**Errors**:
- `VideoNotFoundError`: Video ID doesn't exist
- `VideoInUseError`: Video is assigned to one or more cameras

### get_video_file_path(video_id: str) -> str

Gets the filesystem path to a video file.

**Parameters**:
- `video_id` (str): Unique video identifier

**Returns**: Absolute file path to video file

**Errors**:
- `VideoNotFoundError`: Video ID doesn't exist

