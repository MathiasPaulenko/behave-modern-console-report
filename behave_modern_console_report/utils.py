"""General utility functions for the formatter."""

from __future__ import annotations

import codecs
import io
import math
import time
from typing import Any


def format_duration(seconds: float) -> str:
    """Format a duration in seconds into a human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        A human-readable string such as ``3m42s`` or ``950ms``.
    """
    if not math.isfinite(seconds) or seconds < 0.001:
        return "0ms"
    if seconds < 1.0:
        return f"{int(seconds * 1000)}ms"
    if seconds < 60.0:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    if minutes < 60:
        return f"{minutes}m{remaining_seconds:02d}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h{remaining_minutes:02d}m{remaining_seconds:02d}s"


def now() -> float:
    """Return the current monotonic time."""
    return time.monotonic()


def ensure_unicode_stream(stream: Any) -> Any:
    """Wrap a text stream so it can write arbitrary Unicode characters.

    Behave hands the formatter a stream that may use a locale encoding such as
    cp1252 (e.g. redirected ``sys.stdout`` on Windows, or ``-o`` files opened
    with the console encoding). Writing icons like ``✓`` or ``█`` to such a
    stream raises ``UnicodeEncodeError``. When the underlying binary buffer is
    reachable, a UTF-8 ``TextIOWrapper`` is layered on top so output never
    crashes on non-ASCII characters.

    Args:
        stream: The text stream provided by Behave (or ``None``).

    Returns:
        A stream safe for Unicode output — the original stream when it is
        already UTF-8 or cannot be wrapped (e.g. ``StringIO`` in tests).
    """
    if stream is None:
        return None

    encoding = getattr(stream, "encoding", None)
    if not encoding:
        return stream
    try:
        if codecs.lookup(encoding).name == "utf-8":
            return stream
    except LookupError:
        return stream

    buffer = getattr(stream, "buffer", None)
    if buffer is None:
        # codecs.StreamReaderWriter (used by StreamOpener for -o files) exposes
        # the underlying binary stream via ``.stream``.
        inner = getattr(stream, "stream", None)
        if isinstance(inner, io.IOBase) and not isinstance(inner, io.TextIOBase):
            buffer = inner
    if buffer is None or getattr(buffer, "closed", False):
        return stream

    return io.TextIOWrapper(buffer, encoding="utf-8", errors="replace", write_through=True)
