"""Application-wide constants and message templates."""

import re

# ---------------------------------------------------------------------------
# Supported platforms — URL patterns
# ---------------------------------------------------------------------------

PLATFORM_PATTERNS: dict[str, re.Pattern[str]] = {
    "twitter": re.compile(
        r"https?://(?:www\.)?(?:twitter\.com|x\.com)/\w+/status/\d+",
        re.IGNORECASE,
    ),
    # Future platforms:
    # "instagram": re.compile(r"https?://(?:www\.)?instagram\.com/..."),
    # "youtube": re.compile(r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/..."),
    # "reddit": re.compile(r"https?://(?:www\.)?reddit\.com/..."),
    # "tiktok": re.compile(r"https?://(?:www\.)?tiktok\.com/..."),
}

# ---------------------------------------------------------------------------
# Telegram file-size limit (bots can upload up to 50 MB)
# ---------------------------------------------------------------------------

TELEGRAM_MAX_UPLOAD_MB: int = 50

# ---------------------------------------------------------------------------
# User-facing messages
# ---------------------------------------------------------------------------

MSG_START = (
    "👋 *Welcome to Media Downloader Bot!*\n\n"
    "Send me a link from X (Twitter) and I'll download the video for you.\n\n"
    "*Supported platforms:*\n"
    "• X / Twitter\n\n"
    "_More platforms coming soon!_"
)

MSG_HELP = (
    "ℹ️ *How to use this bot:*\n\n"
    "1. Copy a post URL from X (Twitter)\n"
    "2. Paste it here\n"
    "3. Wait for the video to be downloaded and sent back\n\n"
    "*Supported URL formats:*\n"
    "• `https://x.com/user/status/123456`\n"
    "• `https://twitter.com/user/status/123456`\n\n"
    "*Commands:*\n"
    "/start — Show welcome message\n"
    "/help — Show this help message"
)

MSG_PROCESSING = "⏳ Processing your link, please wait..."

MSG_UNSUPPORTED_URL = (
    "❌ *Unsupported URL*\n\n"
    "I currently only support X (Twitter) links.\n"
    "Please send a valid post URL like:\n"
    "`https://x.com/user/status/123456`"
)

MSG_DOWNLOAD_FAILED = (
    "😔 *Download failed*\n\n"
    "I couldn't download the video from that link. "
    "The post might not contain a video, or it may be private."
)

MSG_FILE_TOO_LARGE = (
    "📦 *File too large*\n\n"
    "The video exceeds Telegram's upload limit of {limit_mb} MB."
)

MSG_UPLOAD_FAILED = (
    "😔 *Upload failed*\n\n"
    "I downloaded the video but couldn't send it to you. "
    "Please try again later."
)

MSG_UNEXPECTED_ERROR = (
    "⚠️ *Something went wrong*\n\n"
    "An unexpected error occurred. Please try again later."
)

MSG_NOT_A_URL = (
    "🤔 I didn't recognize that as a URL.\n"
    "Send /help to see how to use this bot."
)
