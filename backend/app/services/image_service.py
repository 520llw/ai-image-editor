"""
Image service for handling file operations
"""
import os
import uuid
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import aiofiles

from app.config import settings

logger = logging.getLogger(__name__)


class ImageService:
    """Service for handling image file operations"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.get_allowed_extensions_set()
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create upload and output directories if they don't exist"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Upload directory: {self.upload_dir.absolute()}")
        logger.info(f"Output directory: {self.output_dir.absolute()}")
    
    def validate_file(self, filename: str, content_type: Optional[str] = None) -> Tuple[bool, str]:
        """
        Validate file extension and type
        
        Args:
            filename: Name of the file
            content_type: MIME type of the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check extension
        ext = Path(filename).suffix.lower()
        if ext not in self.allowed_extensions:
            allowed = ", ".join(self.allowed_extensions)
            return False, f"Invalid file extension. Allowed: {allowed}"
        
        # Check content type if provided
        if content_type:
            allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
            if content_type not in allowed_types:
                return False, f"Invalid content type: {content_type}"
        
        return True, ""
    
    def validate_file_size(self, size_bytes: int) -> Tuple[bool, str]:
        """
        Validate file size
        
        Args:
            size_bytes: Size of the file in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if size_bytes > self.max_file_size:
            max_mb = self.max_file_size / (1024 * 1024)
            actual_mb = size_bytes / (1024 * 1024)
            return False, f"File size ({actual_mb:.1f}MB) exceeds maximum allowed ({max_mb:.1f}MB)"
        
        return True, ""
    
    def get_image_info(self, image_path: Path) -> dict:
        """
        Get image information
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with image information
        """
        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "format": img.format.lower() if img.format else "unknown",
                "mode": img.mode
            }
    
    async def save_upload(self, file_data: bytes, filename: str, content_type: Optional[str] = None) -> dict:
        """
        Save uploaded file
        
        Args:
            file_data: File content as bytes
            filename: Original filename
            content_type: MIME type
            
        Returns:
            Dictionary with saved file information
        """
        # Validate file
        is_valid, error_msg = self.validate_file(filename, content_type)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Validate size
        is_valid, error_msg = self.validate_file_size(len(file_data))
        if not is_valid:
            raise ValueError(error_msg)
        
        # Generate unique ID and filename
        image_id = str(uuid.uuid4())
        ext = Path(filename).suffix.lower()
        new_filename = f"{image_id}{ext}"
        file_path = self.upload_dir / new_filename
        
        try:
            # Save file asynchronously
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_data)
            
            # Get image info
            img_info = self.get_image_info(file_path)
            
            logger.info(f"Saved upload: {new_filename} ({len(file_data)} bytes)")
            
            return {
                "image_id": image_id,
                "filename": filename,
                "saved_path": str(file_path),
                "url": f"/uploads/{new_filename}",
                "width": img_info["width"],
                "height": img_info["height"],
                "format": img_info["format"],
                "size_bytes": len(file_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to save upload: {e}")
            # Clean up if file was partially created
            if file_path.exists():
                file_path.unlink()
            raise
    
    async def save_output(self, image: Image.Image, original_id: str, format: str = "png") -> dict:
        """
        Save generated output image
        
        Args:
            image: PIL Image object
            original_id: ID of the source image
            format: Output format
            
        Returns:
            Dictionary with saved file information
        """
        # Generate unique ID
        output_id = str(uuid.uuid4())
        filename = f"{output_id}.{format.lower()}"
        file_path = self.output_dir / filename
        
        try:
            # Save image
            save_kwargs = {}
            if format.lower() in ["jpg", "jpeg"]:
                save_kwargs["quality"] = 95
                save_kwargs["optimize"] = True
            elif format.lower() == "png":
                save_kwargs["optimize"] = True
            
            image.save(file_path, format=format.upper(), **save_kwargs)
            
            # Get file size
            size_bytes = file_path.stat().st_size
            
            logger.info(f"Saved output: {filename} ({size_bytes} bytes)")
            
            return {
                "image_id": output_id,
                "original_id": original_id,
                "saved_path": str(file_path),
                "url": f"/outputs/{filename}",
                "width": image.width,
                "height": image.height,
                "format": format.lower(),
                "size_bytes": size_bytes
            }
            
        except Exception as e:
            logger.error(f"Failed to save output: {e}")
            if file_path.exists():
                file_path.unlink()
            raise
    
    def get_image_path(self, image_id: str, is_output: bool = False) -> Optional[Path]:
        """
        Get path to an image file
        
        Args:
            image_id: Image ID
            is_output: Whether to look in output directory
            
        Returns:
            Path to the image file or None if not found
        """
        search_dir = self.output_dir if is_output else self.upload_dir
        
        # Try common extensions
        for ext in [".png", ".jpg", ".jpeg", ".webp"]:
            file_path = search_dir / f"{image_id}{ext}"
            if file_path.exists():
                return file_path
        
        return None
    
    def get_image(self, image_id: str, is_output: bool = False) -> Optional[Image.Image]:
        """
        Load an image
        
        Args:
            image_id: Image ID
            is_output: Whether to look in output directory
            
        Returns:
            PIL Image object or None if not found
        """
        file_path = self.get_image_path(image_id, is_output)
        if file_path:
            return Image.open(file_path)
        return None
    
    def delete_image(self, image_id: str, is_output: bool = False) -> bool:
        """
        Delete an image file
        
        Args:
            image_id: Image ID
            is_output: Whether to look in output directory
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self.get_image_path(image_id, is_output)
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Deleted image: {file_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete image {image_id}: {e}")
                return False
        return False
    
    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up files older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of files deleted
        """
        from datetime import timedelta
        
        deleted_count = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for directory in [self.upload_dir, self.output_dir]:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    try:
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if mtime < cutoff_time:
                            file_path.unlink()
                            deleted_count += 1
                            logger.info(f"Cleaned up old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to cleanup {file_path}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} old files")
        return deleted_count


# Global image service instance
image_service = ImageService()
