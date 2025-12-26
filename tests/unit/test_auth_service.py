"""Unit tests for AuthService."""
import pytest
import os
import time

from src.services.auth import AuthService
from src.services.exceptions import (
    AuthenticationError,
    CredentialsExistError,
    CredentialsNotFoundError
)


class TestAuthService:
    """Tests for AuthService."""
    
    def test_create_credentials(self, auth_service):
        """Test creating initial credentials."""
        auth_service.create_credentials('testuser', 'testpass')
        
        assert auth_service.credentials_exist()
    
    def test_create_credentials_duplicate(self, auth_service):
        """Test creating credentials when they already exist."""
        auth_service.create_credentials('testuser', 'testpass')
        
        with pytest.raises(CredentialsExistError):
            auth_service.create_credentials('testuser', 'testpass')
    
    def test_authenticate_success(self, auth_service):
        """Test successful authentication."""
        auth_service.create_credentials('testuser', 'testpass')
        session = auth_service.authenticate('testuser', 'testpass')
        
        assert session is not None
        assert session.username == 'testuser'
        assert session.session_id is not None
        assert len(session.session_id) > 0
    
    def test_authenticate_invalid_username(self, auth_service):
        """Test authentication with invalid username."""
        auth_service.create_credentials('testuser', 'testpass')
        
        with pytest.raises(AuthenticationError):
            auth_service.authenticate('wronguser', 'testpass')
    
    def test_authenticate_invalid_password(self, auth_service):
        """Test authentication with invalid password."""
        auth_service.create_credentials('testuser', 'testpass')
        
        with pytest.raises(AuthenticationError):
            auth_service.authenticate('testuser', 'wrongpass')
    
    def test_authenticate_no_credentials(self, auth_service):
        """Test authentication when no credentials exist."""
        with pytest.raises(CredentialsNotFoundError):
            auth_service.authenticate('testuser', 'testpass')
    
    def test_validate_session_valid(self, auth_service):
        """Test validating a valid session."""
        auth_service.create_credentials('testuser', 'testpass')
        session = auth_service.authenticate('testuser', 'testpass')
        
        assert auth_service.validate_session(session.session_id) is True
    
    def test_validate_session_invalid(self, auth_service):
        """Test validating an invalid session."""
        assert auth_service.validate_session('nonexistent-session') is False
    
    def test_logout(self, auth_service):
        """Test logging out a session."""
        auth_service.create_credentials('testuser', 'testpass')
        session = auth_service.authenticate('testuser', 'testpass')
        
        assert auth_service.validate_session(session.session_id) is True
        auth_service.logout(session.session_id)
        assert auth_service.validate_session(session.session_id) is False
    
    def test_change_password(self, auth_service):
        """Test changing password."""
        auth_service.create_credentials('testuser', 'oldpass')
        
        auth_service.change_password('testuser', 'oldpass', 'newpass')
        
        # Old password should fail
        with pytest.raises(AuthenticationError):
            auth_service.authenticate('testuser', 'oldpass')
        
        # New password should work
        session = auth_service.authenticate('testuser', 'newpass')
        assert session is not None
    
    def test_change_password_wrong_old(self, auth_service):
        """Test changing password with wrong old password."""
        auth_service.create_credentials('testuser', 'oldpass')
        
        with pytest.raises(AuthenticationError):
            auth_service.change_password('testuser', 'wrongpass', 'newpass')
    
    def test_credentials_exist(self, auth_service):
        """Test checking if credentials exist."""
        assert auth_service.credentials_exist() is False
        
        auth_service.create_credentials('testuser', 'testpass')
        assert auth_service.credentials_exist() is True

