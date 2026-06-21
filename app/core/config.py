"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        BOT_TOKEN: Telegram bot API token from @BotFather.
        WEBHOOK_SECRET: Secret token to verify webhook requests from Telegram.
        WEBHOOK_URL: Public URL where Telegram will send webhook updates.
        TEMP_DIRECTORY: Directory for temporary downloaded files.
        MAX_FILE_SIZE_MB: Maximum allowed file size in megabytes.
    """

    BOT_TOKEN: str
    WEBHOOK_SECRET: str
    WEBHOOK_URL: str
    TEMP_DIRECTORY: str = "temp"
    MAX_FILE_SIZE_MB: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def temp_path(self) -> Path:
        """Return the temp directory as an absolute Path."""
        return Path(self.TEMP_DIRECTORY).resolve()

    @property
    def max_file_size_bytes(self) -> int:
        """Return the maximum file size in bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance.

    Returns:
        The application Settings object.
    """
    return Settings()
