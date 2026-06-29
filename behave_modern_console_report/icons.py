"""Unicode icon definitions used across the formatter."""

from __future__ import annotations

from behave_modern_console_report.models import Status


class Icons:
    """Icon mapping for execution statuses and concepts."""

    PASSED = "✓"
    FAILED = "✗"
    SKIPPED = "⏭"
    UNDEFINED = "⚠"
    PENDING = "🚧"
    RUNNING = "🚀"
    DURATION = "⏱"
    FEATURE = "📁"
    SCENARIO = "📄"
    STEP = "▸"
    BORDER = "━"

    @classmethod
    def for_status(cls, status: Status) -> str:
        """Return the icon for a given status."""
        mapping = {
            Status.PASSED: cls.PASSED,
            Status.FAILED: cls.FAILED,
            Status.SKIPPED: cls.SKIPPED,
            Status.UNDEFINED: cls.UNDEFINED,
            Status.PENDING: cls.PENDING,
            Status.RUNNING: cls.RUNNING,
            Status.UNTESTED: " ",
        }
        return mapping.get(status, " ")
