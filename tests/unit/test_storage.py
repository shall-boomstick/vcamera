"""Unit tests for storage utilities."""
import json
import os
import pytest
import tempfile
import shutil

from src.services.exceptions import StorageError
from src.services.storage import (
    ensure_directories,
    read_json,
    write_json,
    get_videos_path,
    get_cameras_path,
    get_credentials_path
)


class TestStorageUtilities:
    """Tests for storage utility functions."""
    
    def test_ensure_directories(self, temp_dir):
        """Test directory creation."""
        os.chdir(temp_dir)
        
        ensure_directories()
        
        assert os.path.exists('videos')
        assert os.path.exists('data')
        assert os.path.isdir('videos')
        assert os.path.isdir('data')
    
    def test_write_json(self, temp_dir):
        """Test writing JSON file."""
        os.chdir(temp_dir)
        os.makedirs('data', exist_ok=True)
        
        test_data = {'key': 'value', 'number': 42}
        file_path = os.path.join('data', 'test.json')
        
        write_json(file_path, test_data)
        
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            loaded = json.load(f)
        assert loaded == test_data
    
    def test_read_json(self, temp_dir):
        """Test reading JSON file."""
        os.chdir(temp_dir)
        os.makedirs('data', exist_ok=True)
        
        test_data = {'key': 'value', 'number': 42}
        file_path = os.path.join('data', 'test.json')
        
        write_json(file_path, test_data)
        loaded = read_json(file_path)
        
        assert loaded == test_data
    
    def test_read_json_nonexistent(self, temp_dir):
        """Test reading non-existent JSON file returns None."""
        os.chdir(temp_dir)
        
        result = read_json('nonexistent.json')
        
        assert result is None
    
    def test_write_json_creates_directory(self, temp_dir):
        """Test write_json creates parent directory if needed."""
        os.chdir(temp_dir)
        
        test_data = {'key': 'value'}
        file_path = os.path.join('data', 'subdir', 'test.json')
        
        write_json(file_path, test_data)
        
        assert os.path.exists(file_path)
        assert read_json(file_path) == test_data
    
    def test_read_json_invalid_json(self, temp_dir):
        """Test reading invalid JSON raises StorageError."""
        os.chdir(temp_dir)
        os.makedirs('data', exist_ok=True)
        
        file_path = os.path.join('data', 'invalid.json')
        with open(file_path, 'w') as f:
            f.write('not valid json {')
        
        with pytest.raises(StorageError):
            read_json(file_path)
    
    def test_path_helpers(self):
        """Test path helper functions."""
        videos_path = get_videos_path()
        cameras_path = get_cameras_path()
        credentials_path = get_credentials_path()
        
        assert videos_path == os.path.join('data', 'videos.json')
        assert cameras_path == os.path.join('data', 'cameras.json')
        assert credentials_path == os.path.join('data', 'credentials.json')

