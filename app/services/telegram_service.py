"""Telegram messaging service."""

from pathlib import Path

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from app.core.constants import TELEGRAM_MAX_UPLOAD_MB
from app.core.logger import get_logger
from app.utils.file_utils import get_file_size_mb

logger = get_logger(__name__)


class TelegramService:
    """Handles all communication with the Telegram Bot API.

    This service is responsible *only* for sending messages, videos, and
    photos.  It contains no downloading or business logic.

    Args:
        bot_token: The Telegram bot API token.
    """

    def __init__(self, bot_token: str) -> None:
        self._bot = Bot(token=bot_token)

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = ParseMode.MARKDOWN,
    ) -> None:
        """Send a text message to a Telegram chat.

        Args:
            chat_id: The target chat ID.
            text: The message text (Markdown supported).
            parse_mode: Telegram parse mode (default Markdown).
        """
        try:
            await self._bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
            )
            logger.info("Sent message to chat %s", chat_id)
        except TelegramError as exc:
            logger.error("Failed to send message to chat %s: %s", chat_id, exc)
            raise

    async def send_video(
        self,
        chat_id: int,
        video_path: Path,
        caption: str = "",
    ) -> None:
        """Send a video file to a Telegram chat.

        Checks that the file does not exceed Telegram's upload limit
        before attempting the upload.

        Args:
            chat_id: The target chat ID.
            video_path: Path to the video file.
            caption: Optional caption text.

        Raises:
            ValueError: If the file exceeds Telegram's 50 MB upload limit.
            TelegramError: If the Telegram API rejects the upload.
        """
        file_size = get_file_size_mb(video_path)
        if file_size > TELEGRAM_MAX_UPLOAD_MB:
            raise ValueError(
                f"File size ({file_size:.1f} MB) exceeds Telegram's "
                f"{TELEGRAM_MAX_UPLOAD_MB} MB upload limit."
            )

        try:
            with open(video_path, "rb") as video_file:
                await self._bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    caption=caption or None,
                    read_timeout=120,
                    write_timeout=120,
                    connect_timeout=30,
                )
            logger.info(
                "Sent video to chat %s (%.1f MB)", chat_id, file_size
            )
        except TelegramError as exc:
            logger.error(
                "Failed to send video to chat %s: %s", chat_id, exc
            )
            raise

