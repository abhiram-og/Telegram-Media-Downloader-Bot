"""Abstract base class for all media downloaders."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseDownloader(ABC):
    """Interface that every platform-specific downloader must implement."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the human-readable platform name (e.g. ``'Twitter'``)."""
        ...

    @abstractmethod
    async def download(self, url: str, output_dir: Path) -> Path:
        """Download media from *url* and save it to *output_dir*.

        Args:
            url: The media post URL.
            output_dir: Directory where the downloaded file will be stored.

        Returns:
            The path to the downloaded file.

        Raises:
            DownloadError: If the download fails for any reason.
        """
        ...

    @abstractmethod
    async def validate_url(self, url: str) -> bool:
        """Check whether *url* is valid for this downloader's platform.

        Args:
            url: The URL to validate.

        Returns:
            ``True`` if this downloader can handle the URL.
        """
        ...


class DownloadError(Exception):
    """Raised when a media download fails."""

    def __init__(self, message: str = "Download failed", url: str = "") -> None:
        self.url = url
        super().__init__(message)


class UnsupportedPlatformError(Exception):
    """Raised when no downloader exists for the given URL."""

    def __init__(self, url: str = "") -> None:
        self.url = url
        super().__init__(f"No downloader available for URL: {url}")
