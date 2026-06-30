"""General utility functions for the formatter."""

from __future__ import annotations

import time


def format_duration(seconds: float) -> str:
    """Format a duration in seconds into a human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        A human-readable string such as ``3m42s`` or ``950ms``.
    """
    if seconds < 0.001:
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
