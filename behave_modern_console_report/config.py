"""Per-formatter configuration.

Each formatter has its own ``mcr.<formatter>.*`` user-data namespace. When a
formatter-specific key is missing, the global ``mcr.*`` key is used as a
fallback.
"""

from __future__ import annotations

from typing import Any


class FormatterConfig:
    """Configuration for a single formatter instance."""

    def __init__(self, formatter_name: str, behave_config: Any) -> None:
        """Load configuration from Behave user data.

        Args:
            formatter_name: Name of the formatter (e.g. ``modern``).
            behave_config: Behave configuration object.
        """
        self.formatter_name = formatter_name
        self._user_data = getattr(behave_config, "userdata", {}) or {}

        self.colors = self._bool("colors", True)
        self.show_steps = self._bool("show_steps", True)
        self.show_traceback = self._bool("show_traceback", True)
        self.show_progress = self._bool_formatter_specific("show_progress", True)

    def _get(self, key: str, default: Any | None) -> Any | None:
        """Return formatter-specific value, falling back to global ``mcr.*``."""
        value = self._user_data.get(f"mcr.{self.formatter_name}.{key}")
        if value is None:
            value = self._user_data.get(f"mcr.{key}")
        return value if value is not None else default

    def _get_formatter_specific(self, key: str, default: Any | None) -> Any | None:
        """Return only the formatter-specific value, no global fallback."""
        value = self._user_data.get(f"mcr.{self.formatter_name}.{key}")
        return value if value is not None else default

    def _bool(self, key: str, default: bool) -> bool:
        value = self._get(key, None)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"true", "1", "yes", "on"}

    def _bool_formatter_specific(self, key: str, default: bool) -> bool:
        value = self._get_formatter_specific(key, None)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).lower() in {"true", "1", "yes", "on"}
