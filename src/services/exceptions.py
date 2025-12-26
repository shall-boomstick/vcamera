"""Custom exceptions for the virtual camera server application."""


class VideoNotFoundError(Exception):
    """Raised when a video is not found in the library."""
    pass


class CameraNotFoundError(Exception):
    """Raised when a camera is not found."""
    pass


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class StreamError(Exception):
    """Raised when RTSP streaming fails."""
    pass


class VideoInUseError(Exception):
    """Raised when attempting to delete a video that is assigned to a camera."""
    pass


class DuplicateNameError(Exception):
    """Raised when attempting to create a camera with a name that already exists."""
    pass


class InvalidVideoError(Exception):
    """Raised when a video file is invalid or unsupported."""
    pass


class StorageError(Exception):
    """Raised when storage operations fail."""
    pass


class PortInUseError(Exception):
    """Raised when an RTSP port is already in use."""
    pass


class GStreamerError(Exception):
    """Raised when GStreamer operations fail."""
    pass


class VideoFileError(Exception):
    """Raised when video file operations fail."""
    pass


class StreamNotFoundError(Exception):
    """Raised when a stream is not found."""
    pass


class InvalidAuthError(Exception):
    """Raised when authentication configuration is invalid."""
    pass


class CredentialsNotFoundError(Exception):
    """Raised when credentials file doesn't exist."""
    pass


class CredentialsExistError(Exception):
    """Raised when attempting to create credentials that already exist."""
    pass

