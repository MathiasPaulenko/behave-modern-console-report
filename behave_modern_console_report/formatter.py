"""Behave formatter entry point for the modern console report.

This module exposes ``ModernConsoleFormatter``, which is registered as a Behave
formatter under the name ``modern``. The formatter is intentionally thin: it
forwards Behave events to the Collector and asks the Renderer to produce output.
"""

from __future__ import annotations

from typing import Any

from behave.formatter.base import Formatter
from behave.model import Feature as BehaveFeature
from behave.model import Scenario as BehaveScenario
from behave.model import Step as BehaveStep

from behave_modern_console_report.collector import Collector
from behave_modern_console_report.config import Config, Verbosity
from behave_modern_console_report.console import ConsoleManager
from behave_modern_console_report.renderer import Renderer
from behave_modern_console_report.themes import get_theme


class ModernConsoleFormatter(Formatter):
    """Modern real-time console report formatter for Behave."""

    name = "modern"
    description = "Modern real-time console report with rich output."

    def __init__(self, stream: Any, config: Any) -> None:
        """Initialize the formatter.

        Args:
            stream: Output stream provided by Behave.
            config: Behave configuration object.
        """
        super().__init__(stream, config)
        self._config = Config.from_behave(config)
        self._theme = get_theme(self._config.theme)
        self._console_manager = ConsoleManager(self._config, file=self.stream)
        self._collector = Collector(self._config)
        self._renderer = Renderer(self._config, self._theme)
        self._live: Any | None = None
        self._closed = False

        if self._config.is_interactive:
            from rich.live import Live

            self._live = Live(
                console=self._console_manager.console,
                auto_refresh=True,
                refresh_per_second=2,
                screen=False,
                vertical_overflow="visible",
            )
            self._live.start(refresh=True)
            self._refresh()
        elif self._config.verbosity != Verbosity.MINIMAL:
            self._console_manager.console.print(
                self._renderer.render_header(self._collector.execution)
            )
            self._console_manager.console.file.flush()
            self._renderer._header_rendered = True

    def feature(self, feature: BehaveFeature) -> None:
        """Handle a Behave feature event."""
        self._collector.add_feature(feature)
        self._refresh()

    def scenario(self, scenario: BehaveScenario) -> None:
        """Handle a Behave scenario event."""
        self._collector.add_scenario(scenario)
        self._refresh()

    def step(self, step: BehaveStep) -> None:
        """Handle a Behave step event."""
        self._collector.add_step(step)
        self._refresh()

    def match(self, match: Any) -> None:
        """Handle a Behave step match event."""
        self._collector.set_running(match)
        self._refresh()

    def result(self, step_result: BehaveStep) -> None:
        """Handle a Behave step result event."""
        self._collector.update_result(step_result)
        self._refresh()

    def eof(self) -> None:
        """Handle end-of-feature event."""

    def close(self) -> None:
        """Finalize the report and print the summary."""
        if self._closed:
            return
        self._closed = True
        self._collector.finish()

        if self._live is not None:
            self._live.update(self._renderer.render(self._collector.execution, is_final=True))
            self._live.stop()
        else:
            for line in self._renderer.next_ci_lines(self._collector.execution):
                self._console_manager.console.print(line)
            if self._config.show_progress:
                self._console_manager.console.print(
                    self._renderer.render_progress(self._collector.execution)
                )
            self._console_manager.console.print(
                self._renderer.render_summary(self._collector.execution)
            )
            if self._config.verbosity != Verbosity.MINIMAL:
                self._console_manager.console.print(
                    self._renderer.render_failures(self._collector.execution)
                )

    def _refresh(self) -> None:
        """Refresh the display based on the current execution model."""
        if self._live is not None:
            self._live.update(self._renderer.render(self._collector.execution))
        elif not self._config.is_interactive:
            printed_any = False
            for line in self._renderer.next_ci_lines(self._collector.execution):
                self._console_manager.console.print(line)
                printed_any = True
            if printed_any and self._config.show_progress:
                self._console_manager.console.print(
                    self._renderer.render_progress(self._collector.execution)
                )

    # Optional Behave event hooks provided for completeness.

    def uri(self, uri: str) -> None:
        """Handle a feature URI event."""

    def description(self, description: list[str]) -> None:
        """Handle a feature description event."""
