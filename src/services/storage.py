"""JSON storage utility for reading and writing JSON files."""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import StorageError


def ensure_directories():
    """Ensure required directories exist (videos/ and data/)."""
    directories = ['videos', 'data']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def read_json(file_path: str) -> Any:
    """Read JSON data from a file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data (dict, list, etc.)
        
    Raises:
        StorageError: If file cannot be read or parsed
    """
    try:
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StorageError(f"Invalid JSON in {file_path}: {e}")
    except IOError as e:
        raise StorageError(f"Cannot read {file_path}: {e}")


def write_json(file_path: str, data: Any) -> None:
    """Write JSON data to a file.
    
    Args:
        file_path: Path to JSON file
        data: Data to write (must be JSON-serializable)
        
    Raises:
        StorageError: If file cannot be written
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise StorageError(f"Cannot serialize data to JSON: {e}")
    except IOError as e:
        raise StorageError(f"Cannot write {file_path}: {e}")


def get_videos_path() -> str:
    """Get path to videos.json file.
    
    Returns:
        str: Path to videos.json
    """
    return os.path.join('data', 'videos.json')


def get_cameras_path() -> str:
    """Get path to cameras.json file.
    
    Returns:
        str: Path to cameras.json
    """
    return os.path.join('data', 'cameras.json')


def get_credentials_path() -> str:
    """Get path to credentials.json file.
    
    Returns:
        str: Path to credentials.json
    """
    return os.path.join('data', 'credentials.json')

