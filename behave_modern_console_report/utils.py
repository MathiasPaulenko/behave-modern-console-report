"""General utility functions for the formatter."""

from __future__ import annotations

import codecs
import io
import math
import re
import time
from typing import Any

# C0/C1 control characters except tab and newline, which are legitimate in
# tracebacks and messages. Anything else (ESC, BEL, CR, ...) could inject
# terminal escape sequences or corrupt single-line output.
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b-\x1f\x7f-\x9f]")


def sanitize_terminal_text(text: Any) -> str:
    """Return text safe to write to a terminal.

    Feature, scenario, and step names come from user-controlled Gherkin files
    and error messages from arbitrary exceptions; both can contain ANSI escape
    sequences or control characters that would corrupt the report or inject
    terminal control codes.
    """
    if not isinstance(text, str):
        text = str(text)
    return _CONTROL_CHARS_RE.sub("", text)


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
    except (LookupError, TypeError):
        return stream

    buffer = getattr(stream, "buffer", None)
    if buffer is None:
        # codecs.StreamReaderWriter (used by StreamOpener for -o files) exposes
        # the underlying binary stream via ``.stream``.
        inner = getattr(stream, "stream", None)
        if isinstance(inner, io.IOBase) and not isinstance(inner, io.TextIOBase):
            buffer = inner
    if buffer is None or getattr(buffer, "closed", False):
        # No binary buffer to wrap in UTF-8: degrade unencodable characters
        # at write time instead of crashing.
        return _UnicodeSafeTextStream(stream)

    return io.TextIOWrapper(buffer, encoding="utf-8", errors="replace", write_through=True)


class _UnicodeSafeTextStream:
    """Proxy that replaces characters the wrapped stream cannot encode.

    Used when the stream has a non-UTF-8 encoding but exposes no reachable
    binary buffer, so a ``TextIOWrapper`` cannot be layered on top.
    """

    def __init__(self, stream: Any) -> None:
        self._stream = stream

    def write(self, data: str) -> Any:
        try:
            return self._stream.write(data)
        except UnicodeEncodeError:
            encoding = getattr(self._stream, "encoding", None) or "utf-8"
            safe = data.encode(encoding, errors="replace").decode(encoding)
            return self._stream.write(safe)

    def flush(self) -> None:
        self._stream.flush()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._stream, name)
