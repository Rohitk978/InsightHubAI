
import re
from urllib.parse import urlparse


def validate_text_input(text, max_length=50000):
    """
    Validate text input for emptiness and length.
    """
    if not isinstance(text, str):
        return False

    text = text.strip()

    if not text:
        return False

    if len(text) > max_length:
        return False

    return True


def validate_url(url):
    """
    Validate URL format.
    """
    if not isinstance(url, str):
        return False

    url = url.strip()

    if not url or any(char.isspace() for char in url):
        return False

    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.hostname or "." not in parsed.hostname:
            return False

        if re.search(r"[^a-zA-Z0-9.-]", parsed.hostname):
            return False

        return True

    except (ValueError, TypeError):
        return False


def validate_file_extension(filename, allowed_extensions=None):
    """
    Validate file extension.
    """
    if allowed_extensions is None:
        allowed_extensions = [".pdf", ".txt"]

    if not isinstance(filename, str) or not filename.strip():
        return False

    filename = filename.strip().lower()

    return any(
        filename.endswith(ext.lower())
        for ext in allowed_extensions
    )
