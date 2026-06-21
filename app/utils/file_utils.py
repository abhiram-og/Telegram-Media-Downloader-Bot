"""File-system helper utilities."""

import uuid
from pathlib import Path


def ensure_directory(path: Path) -> Path:
    """Create *path* (and parents) if it does not already exist.

    Args:
        path: The directory path to ensure.

    Returns:
        The same *path* for convenience.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size_mb(path: Path) -> float:
    """Return the size of a file in megabytes.

    Args:
        path: Path to the file.

    Returns:
        File size in MB.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    return path.stat().st_size / (1024 * 1024)


def generate_temp_filename(extension: str = ".mp4") -> str:
    """Generate a unique filename using a UUID.

    Args:
        extension: File extension including the leading dot.

    Returns:
        A UUID-based filename string.
    """
    if not extension.startswith("."):
        extension = f".{extension}"
    return f"{uuid.uuid4().hex}{extension}"
