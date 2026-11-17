"""Base formatter shared by all formatters in this package."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from behave.formatter.base import Formatter
from rich.console import Console

from behave_modern_console_report.collector import Collector
from behave_modern_console_report.config import FormatterConfig
from behave_modern_console_report.utils import ensure_unicode_stream

if TYPE_CHECKING:
    from behave.model import Feature as BehaveFeature
    from behave.model import Scenario as BehaveScenario
    from behave.model import Step as BehaveStep


class BaseFormatter(Formatter):  # type: ignore[misc]
    """Shared base for all MCR formatters."""

    name: str = "base"
    description: str = "Shared base formatter"

    def __init__(self, stream: Any, config: Any) -> None:
        """Initialize the formatter with a stream and Behave configuration."""
        super().__init__(stream, config)
        # Behave opens the output stream lazily: stream_opener.stream is None
        # until open() is called. Without this call, `-o file` output is
        # silently redirected to sys.stdout (Console defaults to it on None).
        self._stream = ensure_unicode_stream(self.open())
        self.formatter_config = FormatterConfig(self.name, config)
        self._collector = Collector(self.formatter_config)
        self._closed = False
        self._console = Console(
            file=self._stream,
            no_color=None if self.formatter_config.colors else True,
            # All output is built as Rich Text objects; markup parsing stays
            # off so user-controlled names/messages can never be parsed as
            # markup (crash) or silently lose bracketed text.
            markup=False,
            highlight=False,
        )

    def feature(self, feature: BehaveFeature) -> None:
        """Handle a Behave feature event."""
        self._collector.add_feature(feature)
        self.on_result()

    def scenario(self, scenario: BehaveScenario) -> None:
        """Handle a Behave scenario event."""
        self._collector.add_scenario(scenario)
        self.on_result()

    def step(self, step: BehaveStep) -> None:
        """Handle a Behave step event."""
        self._collector.add_step(step)
        self.on_result()

    def match(self, match: Any) -> None:
        """Handle a Behave step match event."""
        self._collector.set_running(match)
        self.on_result()

    def result(self, result: BehaveStep) -> None:
        """Handle a Behave step result event."""
        self._collector.update_result(result)
        self.on_result()

    def eof(self) -> None:
        """Handle end-of-feature event."""
        self.on_result()

    def close(self) -> None:
        """Finalize the report."""
        if self._closed:
            return
        self._closed = True
        self._collector.finish()
        try:
            self.on_close()
        finally:
            # Let Behave close the output stream it opened (no-op for
            # sys.stdout and pre-opened streams). Runs even if rendering
            # fails so `-o` files are never left open.
            self.close_stream()

    def on_result(self) -> None:
        """Hook called after every model change event. Override in subclasses."""

    def on_close(self) -> None:
        """Hook called once at the end of the execution. Override in subclasses."""
