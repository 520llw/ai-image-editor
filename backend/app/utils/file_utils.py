"""
File utility functions
"""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Tuple


def get_file_hash(file_path: Path, algorithm: str = "md5") -> str:
    """
    Calculate file hash
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (md5, sha1, sha256)
        
    Returns:
        Hex digest of the file hash
    """
    hash_obj = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def get_mime_type(file_path: Path) -> Optional[str]:
    """
    Get MIME type of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string or None
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists
    
    Args:
        path: Directory path
        
    Returns:
        Path object
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and null bytes
    filename = filename.replace("/", "_").replace("\\", "_").replace("\x00", "")
    
    # Remove leading dots
    filename = filename.lstrip(".")
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255 - len(ext)] + ext
    
    return filename or "unnamed"


def get_unique_filename(directory: Path, filename: str) -> str:
    """
    Get a unique filename in the directory
    
    Args:
        directory: Target directory
        filename: Desired filename
        
    Returns:
        Unique filename
    """
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_name = filename
    
    while (directory / unique_name).exists():
        unique_name = f"{base}_{counter}{ext}"
        counter += 1
    
    return unique_name


def cleanup_empty_directories(root_path: Path) -> int:
    """
    Remove empty directories
    
    Args:
        root_path: Root directory to clean
        
    Returns:
        Number of directories removed
    """
    removed = 0
    
    for dirpath, dirnames, filenames in os.walk(str(root_path), topdown=False):
        if not dirnames and not filenames:
            try:
                Path(dirpath).rmdir()
                removed += 1
            except OSError:
                pass
    
    return removed
