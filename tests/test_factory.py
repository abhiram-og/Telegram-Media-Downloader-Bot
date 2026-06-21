"""Tests for DownloaderFactory."""

import pytest

from app.downloaders.base import BaseDownloader
from app.downloaders.factory import DownloaderFactory
from app.downloaders.twitter import TwitterDownloader


class TestDownloaderFactory:
    """Tests for the DownloaderFactory class."""

    def setup_method(self) -> None:
        """Create a fresh factory for each test."""
        self.factory = DownloaderFactory()

    def test_twitter_url_returns_twitter_downloader(self) -> None:
        """Twitter/X URLs should return a TwitterDownloader."""
        urls = [
            "https://twitter.com/user/status/1234567890",
            "https://x.com/user/status/1234567890",
            "https://www.twitter.com/user/status/9876543210",
        ]
        for url in urls:
            downloader = self.factory.get_downloader(url)
            assert downloader is not None, f"No downloader for {url}"
            assert isinstance(downloader, TwitterDownloader)

    def test_unsupported_url_returns_none(self) -> None:
        """Unsupported URLs should return None."""
        urls = [
            "https://instagram.com/p/ABC123",
            "https://youtube.com/watch?v=test",
            "https://example.com",
            "not a url",
        ]
        for url in urls:
            assert self.factory.get_downloader(url) is None

    def test_register_new_downloader(self) -> None:
        """Custom downloaders can be registered and retrieved."""
        from pathlib import Path
        from unittest.mock import AsyncMock

        class FakeDownloader(BaseDownloader):
            @property
            def platform_name(self) -> str:
                return "Fake"

            async def download(self, url: str, output_dir: Path) -> Path:
                return Path("/fake/file.mp4")

            async def validate_url(self, url: str) -> bool:
                return True

        # We need to add the pattern to constants first for the factory
        # to recognize it — this test verifies the register() mechanism.
        from app.core import constants
        import re

        constants.PLATFORM_PATTERNS["fake"] = re.compile(
            r"https?://(?:www\.)?fake\.com/video/\d+"
        )

        fake = FakeDownloader()
        self.factory.register("fake", fake)

        downloader = self.factory.get_downloader("https://fake.com/video/123")
        assert downloader is fake

        # Clean up
        del constants.PLATFORM_PATTERNS["fake"]

    def test_default_registry_has_twitter(self) -> None:
        """The factory should have Twitter registered by default."""
        downloader = self.factory.get_downloader(
            "https://x.com/user/status/123456"
        )
        assert downloader is not None
        assert downloader.platform_name == "Twitter"
