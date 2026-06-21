"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.webhook import router as webhook_router
from app.core.config import get_settings
from app.core.logger import get_logger
from app.services.cleanup_service import CleanupService
from app.utils.file_utils import ensure_directory

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown.

    On startup:
        - Creates the temp directory.
        - Cleans up any leftover files from previous runs.

    On shutdown:
        - Performs a final cleanup of the temp directory.
    """
    settings = get_settings()

    # Startup
    logger.info("Starting Telegram Media Downloader Bot...")
    ensure_directory(settings.temp_path)
    logger.info("Temp directory ready: %s", settings.temp_path)

    # Clean up leftover files from previous runs
    cleanup = CleanupService()
    deleted = cleanup.cleanup_old_files(settings.temp_path, max_age_seconds=0)
    if deleted:
        logger.info("Cleaned up %d leftover file(s) from previous run", deleted)

    logger.info("Bot is ready to receive webhooks at /webhook")

    yield

    # Shutdown
    logger.info("Shutting down — cleaning temp directory...")
    cleanup.cleanup_old_files(settings.temp_path, max_age_seconds=0)
    logger.info("Shutdown complete.")


app = FastAPI(
    title="Telegram Media Downloader Bot",
    description=(
        "A Telegram bot that downloads videos from X (Twitter) "
        "and sends them back as Telegram video messages."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Register routes
app.include_router(webhook_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        A JSON response indicating the service is running.
    """
    return {"status": "ok", "service": "telegram-media-bot"}
