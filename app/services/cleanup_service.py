"""File cleanup service."""

import time
from pathlib import Path

from app.core.logger import get_logger

logger = get_logger(__name__)


class CleanupService:
    """Handles deletion of temporary downloaded files."""

    @staticmethod
    def delete_file(file_path: Path) -> None:
        """Delete a single file from disk.

        Logs a warning instead of raising if the file is already gone.

        Args:
            file_path: Path to the file to delete.
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info("Deleted file: %s", file_path)
            else:
                logger.warning("File already removed: %s", file_path)
        except OSError as exc:
            logger.error("Failed to delete file %s: %s", file_path, exc)

    @staticmethod
    def cleanup_old_files(
        directory: Path,
        max_age_seconds: int = 3600,
    ) -> int:
        """Remove files older than *max_age_seconds* from *directory*.

        Only top-level files are considered (sub-directories are skipped).

        Args:
            directory: The directory to scan.
            max_age_seconds: Maximum file age in seconds (default 1 hour).

        Returns:
            The number of files deleted.
        """
        if not directory.exists():
            logger.warning("Cleanup directory does not exist: %s", directory)
            return 0

        now = time.time()
        deleted = 0

        for file_path in directory.iterdir():
            if not file_path.is_file():
                continue

            age = now - file_path.stat().st_mtime
            if age > max_age_seconds:
                try:
                    file_path.unlink()
                    deleted += 1
                    logger.info(
                        "Cleaned up old file: %s (age: %.0fs)", file_path, age
                    )
                except OSError as exc:
                    logger.error(
                        "Failed to clean up %s: %s", file_path, exc
                    )

        logger.info(
            "Cleanup complete: deleted %d file(s) from %s", deleted, directory
        )
        return deleted
