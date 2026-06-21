"""Tests for DownloadService."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.downloaders.base import BaseDownloader, DownloadError, UnsupportedPlatformError
from app.downloaders.factory import DownloaderFactory
from app.services.download_service import DownloadService


class TestDownloadService:
    """Tests for the DownloadService class."""

    def setup_method(self) -> None:
        """Create a DownloadService with a mocked factory."""
        self.factory = MagicMock(spec=DownloaderFactory)
        self.temp_dir = Path("/tmp/test-downloads")
        self.service = DownloadService(
            factory=self.factory,
            temp_dir=self.temp_dir,
        )

    @pytest.mark.asyncio
    async def test_successful_download(self) -> None:
        """A valid URL should go through the full pipeline."""
        mock_downloader = AsyncMock(spec=BaseDownloader)
        mock_downloader.platform_name = "Twitter"
        expected_path = Path("/tmp/test-downloads/video.mp4")
        mock_downloader.download.return_value = expected_path

        self.factory.get_downloader.return_value = mock_downloader

        with patch("app.services.download_service.is_valid_url", return_value=True), \
             patch("app.services.download_service.is_supported_url", return_value=True), \
             patch("app.services.download_service.ensure_directory"):

            result = await self.service.download(
                "https://x.com/user/status/123456"
            )

        assert result == expected_path
        mock_downloader.download.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_url_raises(self) -> None:
        """An invalid URL should raise UnsupportedPlatformError."""
        with patch("app.services.download_service.is_valid_url", return_value=False):
            with pytest.raises(UnsupportedPlatformError):
                await self.service.download("not-a-url")

    @pytest.mark.asyncio
    async def test_unsupported_platform_raises(self) -> None:
        """A valid but unsupported URL should raise UnsupportedPlatformError."""
        with patch("app.services.download_service.is_valid_url", return_value=True), \
             patch("app.services.download_service.is_supported_url", return_value=False):
            with pytest.raises(UnsupportedPlatformError):
                await self.service.download("https://unsupported.com/video/123")

    @pytest.mark.asyncio
    async def test_no_downloader_found_raises(self) -> None:
        """If factory returns None, UnsupportedPlatformError should be raised."""
        self.factory.get_downloader.return_value = None

        with patch("app.services.download_service.is_valid_url", return_value=True), \
             patch("app.services.download_service.is_supported_url", return_value=True):
            with pytest.raises(UnsupportedPlatformError):
                await self.service.download("https://x.com/user/status/123456")

    @pytest.mark.asyncio
    async def test_download_failure_propagates(self) -> None:
        """A DownloadError from the downloader should propagate up."""
        mock_downloader = AsyncMock(spec=BaseDownloader)
        mock_downloader.platform_name = "Twitter"
        mock_downloader.download.side_effect = DownloadError(
            message="yt-dlp failed", url="https://x.com/user/status/123"
        )

        self.factory.get_downloader.return_value = mock_downloader

        with patch("app.services.download_service.is_valid_url", return_value=True), \
             patch("app.services.download_service.is_supported_url", return_value=True), \
             patch("app.services.download_service.ensure_directory"):

            with pytest.raises(DownloadError):
                await self.service.download(
                    "https://x.com/user/status/123456"
                )

    @pytest.mark.asyncio
    async def test_url_whitespace_is_stripped(self) -> None:
        """Leading/trailing whitespace in the URL should be stripped."""
        mock_downloader = AsyncMock(spec=BaseDownloader)
        mock_downloader.platform_name = "Twitter"
        mock_downloader.download.return_value = Path("/tmp/video.mp4")

        self.factory.get_downloader.return_value = mock_downloader

        with patch("app.services.download_service.is_valid_url", return_value=True), \
             patch("app.services.download_service.is_supported_url", return_value=True), \
             patch("app.services.download_service.ensure_directory"):

            await self.service.download(
                "  https://x.com/user/status/123456  "
            )

        # Factory should receive the stripped URL
        self.factory.get_downloader.assert_called_once_with(
            "https://x.com/user/status/123456"
        )
