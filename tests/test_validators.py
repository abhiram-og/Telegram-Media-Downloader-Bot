"""Tests for URL validation and platform detection."""

import pytest

from app.utils.validators import extract_platform, is_supported_url, is_valid_url


# ---------------------------------------------------------------------------
# is_valid_url
# ---------------------------------------------------------------------------

class TestIsValidUrl:
    """Tests for the is_valid_url function."""

    @pytest.mark.parametrize(
        "url",
        [
            "https://x.com/user/status/123456",
            "https://twitter.com/user/status/123456",
            "http://example.com",
            "https://www.google.com/search?q=test",
        ],
    )
    def test_valid_urls(self, url: str) -> None:
        assert is_valid_url(url) is True

    @pytest.mark.parametrize(
        "text",
        [
            "",
            "hello world",
            "not a url",
            "ftp://files.example.com",
            "just-a-string",
            "x.com/user/status/123456",  # missing scheme
        ],
    )
    def test_invalid_urls(self, text: str) -> None:
        assert is_valid_url(text) is False


# ---------------------------------------------------------------------------
# extract_platform
# ---------------------------------------------------------------------------

class TestExtractPlatform:
    """Tests for the extract_platform function."""

    @pytest.mark.parametrize(
        "url",
        [
            "https://twitter.com/elonmusk/status/1234567890",
            "https://www.twitter.com/user/status/9876543210",
            "https://x.com/user/status/1234567890",
            "https://www.x.com/user/status/9876543210",
            "http://x.com/someone/status/111222333",
        ],
    )
    def test_twitter_urls(self, url: str) -> None:
        assert extract_platform(url) == "twitter"

    @pytest.mark.parametrize(
        "url",
        [
            "https://instagram.com/p/ABC123",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://reddit.com/r/python/comments/abc123",
            "https://www.tiktok.com/@user/video/123",
            "https://example.com",
            "https://twitter.com/user",  # no /status/id
        ],
    )
    def test_unsupported_urls(self, url: str) -> None:
        assert extract_platform(url) is None

    def test_empty_string(self) -> None:
        assert extract_platform("") is None

    def test_whitespace_handling(self) -> None:
        assert extract_platform("  https://x.com/user/status/123  ") == "twitter"


# ---------------------------------------------------------------------------
# is_supported_url
# ---------------------------------------------------------------------------

class TestIsSupportedUrl:
    """Tests for the is_supported_url function."""

    def test_supported_twitter(self) -> None:
        assert is_supported_url("https://x.com/user/status/123456") is True

    def test_unsupported_instagram(self) -> None:
        assert is_supported_url("https://instagram.com/p/ABC123") is False

    def test_random_url(self) -> None:
        assert is_supported_url("https://example.com") is False
