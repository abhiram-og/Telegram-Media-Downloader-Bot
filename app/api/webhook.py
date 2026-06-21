"""Telegram webhook endpoint."""

from fastapi import APIRouter, BackgroundTasks, Request, Response

from app.core.config import get_settings
from app.core.constants import (
    MSG_DOWNLOAD_FAILED,
    MSG_FILE_TOO_LARGE,
    MSG_HELP,
    MSG_NOT_A_URL,
    MSG_PROCESSING,
    MSG_START,
    MSG_UNEXPECTED_ERROR,
    MSG_UNSUPPORTED_URL,
    MSG_UPLOAD_FAILED,
    TELEGRAM_MAX_UPLOAD_MB,
)
from app.core.logger import get_logger
from app.downloaders.base import DownloadError, UnsupportedPlatformError
from app.downloaders.factory import DownloaderFactory
from app.services.cleanup_service import CleanupService
from app.services.download_service import DownloadService
from app.services.telegram_service import TelegramService
from app.utils.validators import is_valid_url

logger = get_logger(__name__)
router = APIRouter()

# ---------------------------------------------------------------------------
# Service singletons (initialized at import time)
# ---------------------------------------------------------------------------
_settings = get_settings()
_telegram_service = TelegramService(bot_token=_settings.BOT_TOKEN)
_downloader_factory = DownloaderFactory()
_download_service = DownloadService(
    factory=_downloader_factory,
    temp_dir=_settings.temp_path,
)
_cleanup_service = CleanupService()


# ---------------------------------------------------------------------------
# Background task — download, send, clean up
# ---------------------------------------------------------------------------
async def _process_media_url(chat_id: int, url: str) -> None:
    """Download media, send it to the user, and clean up.

    This function runs as a FastAPI background task so that the
    webhook can respond with 200 immediately.

    Args:
        chat_id: Telegram chat to reply to.
        url: The media URL to process.
    """
    file_path = None
    try:
        # 1. Download
        file_path = await _download_service.download(url)

        # 2. Send video
        await _telegram_service.send_video(
            chat_id=chat_id,
            video_path=file_path,
            caption="🎬 Here's your video!",
        )
        logger.info("Successfully sent video to chat %s", chat_id)

    except UnsupportedPlatformError:
        await _telegram_service.send_message(chat_id, MSG_UNSUPPORTED_URL)

    except DownloadError as exc:
        logger.error("Download error for chat %s: %s", chat_id, exc)
        await _telegram_service.send_message(chat_id, MSG_DOWNLOAD_FAILED)

    except ValueError as exc:
        # File too large for Telegram
        logger.warning("File too large for chat %s: %s", chat_id, exc)
        await _telegram_service.send_message(
            chat_id,
            MSG_FILE_TOO_LARGE.format(limit_mb=TELEGRAM_MAX_UPLOAD_MB),
        )

    except Exception as exc:
        logger.exception("Unexpected error for chat %s: %s", chat_id, exc)
        try:
            await _telegram_service.send_message(chat_id, MSG_UNEXPECTED_ERROR)
        except Exception:
            logger.error("Could not send error message to chat %s", chat_id)

    finally:
        # 3. Clean up
        if file_path is not None:
            _cleanup_service.delete_file(file_path)


# ---------------------------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------------------------
@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
) -> Response:
    """Receive a Telegram webhook update and process it.

    Parses the incoming JSON, handles bot commands (``/start``,
    ``/help``), and queues media URL processing as a background task
    so the endpoint can return ``200 OK`` immediately.
    """
    try:
        data: dict = await request.json()
    except Exception:
        logger.error("Failed to parse webhook JSON")
        return Response(status_code=200)

    logger.info("Webhook received: %s", data.get("update_id", "unknown"))

    # Extract message details
    message: dict | None = data.get("message")
    if message is None:
        # Could be an edited_message, channel_post, etc. — ignore.
        return Response(status_code=200)

    chat_id: int = message["chat"]["id"]
    text: str | None = message.get("text")

    if not text:
        return Response(status_code=200)

    text = text.strip()

    # Handle bot commands
    if text.startswith("/start"):
        background_tasks.add_task(
            _telegram_service.send_message, chat_id, MSG_START
        )
        return Response(status_code=200)

    if text.startswith("/help"):
        background_tasks.add_task(
            _telegram_service.send_message, chat_id, MSG_HELP
        )
        return Response(status_code=200)

    # Check if it's a URL at all
    if not is_valid_url(text):
        background_tasks.add_task(
            _telegram_service.send_message, chat_id, MSG_NOT_A_URL
        )
        return Response(status_code=200)

    # Acknowledge and process in background
    background_tasks.add_task(
        _telegram_service.send_message, chat_id, MSG_PROCESSING
    )
    background_tasks.add_task(_process_media_url, chat_id, text)

    return Response(status_code=200)
