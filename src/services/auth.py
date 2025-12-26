"""Authentication Service for GUI authentication and credential management."""
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional

from ..models.user_session import UserSession
from .exceptions import (
    AuthenticationError,
    CredentialsExistError,
    CredentialsNotFoundError,
    StorageError,
)
from .storage import ensure_directories, get_credentials_path, read_json, write_json
from .utils import generate_id

# Session timeout: 24 hours
SESSION_TIMEOUT_HOURS = 24

# In-memory session storage
_sessions: Dict[str, UserSession] = {}


class AuthService:
    """Service for handling authentication and session management."""
    
    def __init__(self):
        """Initialize the authentication service."""
        ensure_directories()
        self.credentials_path = get_credentials_path()
    
    def authenticate(self, username: str, password: str) -> UserSession:
        """Authenticate a user and create a session.
        
        Args:
            username: Login username
            password: Login password (plain text)
            
        Returns:
            UserSession: UserSession object if successful
            
        Raises:
            AuthenticationError: Invalid username or password
            CredentialsNotFoundError: No credentials file exists (first run)
        """
        credentials = self._load_credentials()
        
        if credentials is None:
            raise CredentialsNotFoundError("No credentials found. Please create credentials first.")
        
        # Hash provided password
        password_hash = self._hash_password(password)
        
        # Compare with stored hash
        if credentials['username'] != username or credentials['password_hash'] != password_hash:
            raise AuthenticationError("Invalid username or password")
        
        # Create session
        session_id = generate_id()
        now = datetime.utcnow().isoformat() + 'Z'
        
        session = UserSession(
            username=username,
            session_id=session_id,
            login_time=now,
            last_activity=now
        )
        
        # Store session in memory
        _sessions[session_id] = session
        
        return session
    
    def create_credentials(self, username: str, password: str) -> bool:
        """Create initial user credentials (first-time setup).
        
        Args:
            username: Username to create
            password: Password to create (plain text)
            
        Returns:
            bool: True if created successfully
            
        Raises:
            CredentialsExistError: Credentials already exist
            StorageError: Cannot write credentials file
        """
        # Check if credentials already exist
        existing = self._load_credentials()
        if existing is not None:
            raise CredentialsExistError("Credentials already exist")
        
        # Validate username
        if not username or not username.strip():
            raise ValueError("Username cannot be empty")
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create credentials object
        credentials = {
            'username': username.strip(),
            'password_hash': password_hash,
            'created_date': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Save to credentials.json
        try:
            write_json(self.credentials_path, credentials)
        except StorageError as e:
            raise StorageError(f"Cannot write credentials file: {e}")
        
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password.
        
        Args:
            username: Username
            old_password: Current password
            new_password: New password (plain text)
            
        Returns:
            bool: True if changed successfully
            
        Raises:
            AuthenticationError: Old password incorrect
            CredentialsNotFoundError: No credentials file
        """
        # Authenticate with old password
        try:
            self.authenticate(username, old_password)
        except AuthenticationError:
            raise AuthenticationError("Old password is incorrect")
        
        # Hash new password
        new_password_hash = self._hash_password(new_password)
        
        # Update credentials
        credentials = self._load_credentials()
        if credentials is None:
            raise CredentialsNotFoundError("No credentials file found")
        
        credentials['password_hash'] = new_password_hash
        write_json(self.credentials_path, credentials)
        
        return True
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if a session is still active.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session is valid, False otherwise
        """
        if session_id not in _sessions:
            return False
        
        session = _sessions[session_id]
        
        # Check if session has expired
        login_time = datetime.fromisoformat(session.login_time.replace('Z', '+00:00'))
        timeout = timedelta(hours=SESSION_TIMEOUT_HOURS)
        
        if datetime.utcnow() - login_time.replace(tzinfo=None) > timeout:
            # Session expired, remove it
            del _sessions[session_id]
            return False
        
        # Update last activity
        session.update_activity(datetime.utcnow().isoformat() + 'Z')
        
        return True
    
    def logout(self, session_id: str) -> bool:
        """Log out a user session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if logged out successfully
        """
        if session_id in _sessions:
            del _sessions[session_id]
        return True
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            UserSession: Session object, or None if not found
        """
        return _sessions.get(session_id)
    
    def credentials_exist(self) -> bool:
        """Check if credentials file exists.
        
        Returns:
            bool: True if credentials exist, False otherwise
        """
        return self._load_credentials() is not None
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA256.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password (hex string)
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _load_credentials(self) -> Optional[dict]:
        """Load credentials from JSON file.
        
        Returns:
            dict: Credentials dictionary, or None if file doesn't exist
        """
        return read_json(self.credentials_path)

