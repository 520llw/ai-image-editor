"""
Custom exceptions for the application
"""


class AppException(Exception):
    """Base application exception"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        super().__init__(self.message)


class ValidationError(AppException):
    """Validation error"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class ImageNotFoundError(AppException):
    """Image not found error"""
    def __init__(self, image_id: str):
        super().__init__(f"Image not found: {image_id}", "IMAGE_NOT_FOUND")


class TaskNotFoundError(AppException):
    """Task not found error"""
    def __init__(self, task_id: str):
        super().__init__(f"Task not found: {task_id}", "TASK_NOT_FOUND")


class GenerationError(AppException):
    """Image generation error"""
    def __init__(self, message: str):
        super().__init__(message, "GENERATION_ERROR")


class ModelLoadError(AppException):
    """Model loading error"""
    def __init__(self, model_id: str, reason: str = ""):
        message = f"Failed to load model: {model_id}"
        if reason:
            message += f" ({reason})"
        super().__init__(message, "MODEL_LOAD_ERROR")


class FileSizeError(AppException):
    """File size error"""
    def __init__(self, size: int, max_size: int):
        size_mb = size / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        super().__init__(
            f"File size ({size_mb:.1f}MB) exceeds maximum ({max_mb:.1f}MB)",
            "FILE_TOO_LARGE"
        )


class FileTypeError(AppException):
    """File type error"""
    def __init__(self, extension: str, allowed: list):
        super().__init__(
            f"Invalid file type: {extension}. Allowed: {', '.join(allowed)}",
            "INVALID_FILE_TYPE"
        )
