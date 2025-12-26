"""Services package."""
from .camera_manager import CameraManagerService
from .exceptions import (
    AuthenticationError,
    CameraNotFoundError,
    CredentialsExistError,
    CredentialsNotFoundError,
    DuplicateNameError,
    GStreamerError,
    InvalidAuthError,
    InvalidVideoError,
    PortInUseError,
    StorageError,
    StreamError,
    StreamNotFoundError,
    VideoFileError,
    VideoInUseError,
    VideoNotFoundError,
)
from .logger import get_logger, setup_logging
from .rtsp_server import get_rtsp_manager
from .storage import (
    ensure_directories,
    get_cameras_path,
    get_credentials_path,
    get_videos_path,
    read_json,
    write_json,
)
from .utils import generate_id
from .video_library import VideoLibraryService

__all__ = [
    'CameraManagerService',
    'VideoLibraryService',
    'get_rtsp_manager',
    'setup_logging',
    'get_logger',
    'generate_id',
    'ensure_directories',
    'read_json',
    'write_json',
    'get_videos_path',
    'get_cameras_path',
    'get_credentials_path',
    'VideoNotFoundError',
    'CameraNotFoundError',
    'AuthenticationError',
    'StreamError',
    'VideoInUseError',
    'DuplicateNameError',
    'InvalidVideoError',
    'StorageError',
    'PortInUseError',
    'GStreamerError',
    'VideoFileError',
    'StreamNotFoundError',
    'InvalidAuthError',
    'CredentialsNotFoundError',
    'CredentialsExistError',
]

