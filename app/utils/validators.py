"""URL validation and platform detection utilities."""

import re
from urllib.parse import urlparse

from app.core.constants import PLATFORM_PATTERNS


def is_valid_url(text: str) -> bool:
    """Check whether *text* looks like a valid HTTP(S) URL.

    Args:
        text: The string to validate.

    Returns:
        ``True`` if *text* is a well-formed URL with an HTTP(S) scheme.
    """
    try:
        result = urlparse(text.strip())
        return result.scheme in ("http", "https") and bool(result.netloc)
    except (ValueError, AttributeError):
        return False


def extract_platform(url: str) -> str | None:
    """Determine which supported platform a URL belongs to.

    Args:
        url: The URL to inspect.

    Returns:
        The platform name (e.g. ``"twitter"``) or ``None`` if unsupported.
    """
    url = url.strip()
    for platform, pattern in PLATFORM_PATTERNS.items():
        if pattern.search(url):
            return platform
    return None


def is_supported_url(url: str) -> bool:
    """Check whether *url* matches any supported platform.

    Args:
        url: The URL to validate.

    Returns:
        ``True`` if the URL belongs to a supported platform.
    """
    return extract_platform(url) is not None
