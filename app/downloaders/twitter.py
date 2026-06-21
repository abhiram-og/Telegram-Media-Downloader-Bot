"""Twitter / X video downloader using yt-dlp."""

import asyncio
from pathlib import Path

import yt_dlp

from app.core.constants import PLATFORM_PATTERNS
from app.core.logger import get_logger
from app.downloaders.base import BaseDownloader, DownloadError
from app.utils.file_utils import generate_temp_filename

logger = get_logger(__name__)


class TwitterDownloader(BaseDownloader):
    """Download videos from X (Twitter) posts using yt-dlp."""

    @property
    def platform_name(self) -> str:
        """Return the platform name."""
        return "Twitter"

    async def validate_url(self, url: str) -> bool:
        """Check whether *url* is a valid Twitter/X post URL.

        Args:
            url: The URL to validate.

        Returns:
            ``True`` if the URL matches Twitter/X patterns.
        """
        pattern = PLATFORM_PATTERNS.get("twitter")
        if pattern is None:
            return False
        return bool(pattern.search(url.strip()))

    async def download(self, url: str, output_dir: Path) -> Path:
        """Download video from a Twitter/X post.

        Uses ``yt-dlp`` to extract and download the best MP4 video.
        The extraction runs in a thread executor to avoid blocking
        the async event loop.

        Args:
            url: The Twitter/X post URL.
            output_dir: Directory to save the downloaded file.

        Returns:
            Path to the downloaded video file.

        Raises:
            DownloadError: If yt-dlp fails to download the video.
        """
        filename = generate_temp_filename(".mp4")
        output_path = output_dir / filename
        output_template = str(output_dir / filename.replace(".mp4", "")) + ".%(ext)s"

        ydl_opts: dict = {
            "format": "best[ext=mp4]/best",
            "outtmpl": output_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30,
            "retries": 3,
        }

        logger.info("Starting download from Twitter: %s", url)

        try:
            downloaded_file = await asyncio.to_thread(
                self._download_sync, url, ydl_opts, output_dir
            )
            logger.info("Download completed: %s", downloaded_file)
            return downloaded_file
        except Exception as exc:
            logger.error("Twitter download failed for %s: %s", url, exc)
            raise DownloadError(
                message=f"Failed to download video from Twitter: {exc}",
                url=url,
            ) from exc

    @staticmethod
    def _download_sync(url: str, ydl_opts: dict, output_dir: Path) -> Path:
        """Run yt-dlp synchronously (called via ``asyncio.to_thread``).

        Args:
            url: The media URL.
            ydl_opts: yt-dlp options dictionary.
            output_dir: Directory where the file is saved.

        Returns:
            Path to the downloaded file.

        Raises:
            DownloadError: If no file was produced by yt-dlp.
        """
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if info is None:
                raise DownloadError(
                    message="yt-dlp returned no info", url=url
                )

            # yt-dlp may change the extension; find the actual file
            filename = ydl.prepare_filename(info)
            downloaded = Path(filename)

            if not downloaded.exists():
                # Try common fallback extensions
                for ext in (".mp4", ".webm", ".mkv"):
                    candidate = downloaded.with_suffix(ext)
                    if candidate.exists():
                        return candidate

                raise DownloadError(
                    message=f"Downloaded file not found at {downloaded}",
                    url=url,
                )

            return downloaded
