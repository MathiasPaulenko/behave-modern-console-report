"""Console output management for the modern console formatter."""

from __future__ import annotations

from typing import Any

from rich.console import Console

from behave_modern_console_report.config import Config


class ConsoleManager:
    """Wraps a Rich Console configured for the formatter environment."""

    def __init__(self, config: Config, file: Any | None = None) -> None:
        self.config = config
        self.console = Console(
            file=file,
            color_system="auto" if config.colors else None,
            force_terminal=config.colors,
            width=120,
            soft_wrap=True,
            legacy_windows=False,
        )

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print to the underlying console."""
        self.console.print(*args, **kwargs)
