"""Download orchestration service."""

from pathlib import Path

from app.core.logger import get_logger
from app.downloaders.base import BaseDownloader, DownloadError, UnsupportedPlatformError
from app.downloaders.factory import DownloaderFactory
from app.utils.file_utils import ensure_directory
from app.utils.validators import is_supported_url, is_valid_url

logger = get_logger(__name__)


class DownloadService:
    """Orchestrates the download workflow.

    Responsibilities:
        1. Validate the incoming URL.
        2. Obtain the correct downloader from the factory.
        3. Download the media to a local temp directory.
        4. Return the local file path.

    This class contains business logic only — no Telegram or HTTP
    concerns.

    Args:
        factory: A :class:`DownloaderFactory` for obtaining downloaders.
        temp_dir: The directory to store downloaded files.
    """

    def __init__(self, factory: DownloaderFactory, temp_dir: Path) -> None:
        self._factory = factory
        self._temp_dir = temp_dir

    async def download(self, url: str) -> Path:
        """Execute the full download pipeline.

        Args:
            url: The media URL to download.

        Returns:
            Path to the downloaded file.

        Raises:
            UnsupportedPlatformError: If the URL doesn't match any
                registered platform.
            DownloadError: If the download itself fails.
        """
        url = url.strip()

        # Step 1 — basic URL format check
        if not is_valid_url(url):
            logger.warning("Invalid URL format: %s", url)
            raise UnsupportedPlatformError(url=url)

        # Step 2 — platform support check
        if not is_supported_url(url):
            logger.warning("Unsupported platform for URL: %s", url)
            raise UnsupportedPlatformError(url=url)

        # Step 3 — get the appropriate downloader
        downloader: BaseDownloader | None = self._factory.get_downloader(url)
        if downloader is None:
            raise UnsupportedPlatformError(url=url)

        logger.info(
            "Using %s downloader for: %s", downloader.platform_name, url
        )

        # Step 4 — ensure temp directory exists and download
        ensure_directory(self._temp_dir)
        file_path = await downloader.download(url, self._temp_dir)

        logger.info("Download service completed: %s", file_path)
        return file_path
