"""Factory for selecting the appropriate downloader based on URL."""

from app.core.constants import PLATFORM_PATTERNS
from app.core.logger import get_logger
from app.downloaders.base import BaseDownloader
from app.downloaders.twitter import TwitterDownloader

logger = get_logger(__name__)


class DownloaderFactory:
    """Registry that maps platform names to downloader instances.

    New platforms can be added by calling :meth:`register` with a
    platform key and a :class:`BaseDownloader` implementation.  The
    factory is pre-populated with the Twitter downloader.

    Example::

        factory = DownloaderFactory()
        factory.register("instagram", InstagramDownloader())
        downloader = factory.get_downloader("https://x.com/user/status/123")
    """

    def __init__(self) -> None:
        self._registry: dict[str, BaseDownloader] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register the built-in downloaders."""
        self.register("twitter", TwitterDownloader())

    def register(self, platform: str, downloader: BaseDownloader) -> None:
        """Register a downloader for a given platform.

        Args:
            platform: The platform key (must match a key in
                ``PLATFORM_PATTERNS``).
            downloader: The downloader instance to use.
        """
        self._registry[platform.lower()] = downloader
        logger.info("Registered downloader for platform: %s", platform)

    def get_downloader(self, url: str) -> BaseDownloader | None:
        """Return the appropriate downloader for *url*.

        Iterates over registered platform patterns and returns the
        first matching downloader.

        Args:
            url: The media URL.

        Returns:
            A :class:`BaseDownloader` instance, or ``None`` if no
            downloader matches.
        """
        url = url.strip()
        for platform, pattern in PLATFORM_PATTERNS.items():
            if pattern.search(url) and platform in self._registry:
                logger.info("Matched platform '%s' for URL: %s", platform, url)
                return self._registry[platform]

        logger.warning("No downloader found for URL: %s", url)
        return None
