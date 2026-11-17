"""Tests for utility functions."""

import io
from pathlib import Path

from behave_modern_console_report.utils import (
    ensure_unicode_stream,
    format_duration,
    sanitize_terminal_text,
)


def test_format_duration_sub_second() -> None:
    assert format_duration(0.42) == "420ms"


def test_format_duration_seconds() -> None:
    assert format_duration(12.5) == "12.5s"


def test_format_duration_minutes() -> None:
    assert format_duration(222.0) == "3m42s"


def test_format_duration_hours() -> None:
    assert format_duration(3665.0) == "1h01m05s"


def test_format_duration_zero() -> None:
    assert format_duration(0.0) == "0ms"


def test_format_duration_micro() -> None:
    assert format_duration(0.00004) == "0ms"


def test_format_duration_inf() -> None:
    """Regression: format_duration must not crash on float('inf')."""
    assert format_duration(float("inf")) == "0ms"


def test_format_duration_nan() -> None:
    """Regression: format_duration must not crash on float('nan')."""
    assert format_duration(float("nan")) == "0ms"


def test_format_duration_negative() -> None:
    """Negative durations should be treated as zero."""
    assert format_duration(-1.0) == "0ms"


# --- ensure_unicode_stream ---


def test_ensure_unicode_stream_none() -> None:
    assert ensure_unicode_stream(None) is None


def test_ensure_unicode_stream_no_encoding() -> None:
    """Streams without an encoding attribute pass through unchanged."""
    stream = io.StringIO()
    assert ensure_unicode_stream(stream) is stream


def test_ensure_unicode_stream_utf8() -> None:
    """UTF-8 streams pass through unchanged."""
    buffer = io.BytesIO()
    stream = io.TextIOWrapper(buffer, encoding="utf-8")
    assert ensure_unicode_stream(stream) is stream


def test_ensure_unicode_stream_non_string_encoding() -> None:
    """Regression: a non-string encoding must not crash codecs.lookup."""

    class WeirdStream:
        encoding = 123

        def write(self, data: str) -> int:
            return len(data)

    stream = WeirdStream()
    assert ensure_unicode_stream(stream) is stream


def test_ensure_unicode_stream_wraps_binary_buffer() -> None:
    """A cp1252 text stream with a reachable buffer is wrapped in UTF-8."""
    buffer = io.BytesIO()
    stream = io.TextIOWrapper(buffer, encoding="cp1252")
    wrapped = ensure_unicode_stream(stream)
    assert wrapped is not stream
    wrapped.write("✓ ok")
    wrapped.flush()
    assert buffer.getvalue() == "✓ ok".encode()


def test_ensure_unicode_stream_codecs_style_stream(tmp_path: Path) -> None:
    """codecs.open() (used by Behave for -o files) exposes .stream, not .buffer."""
    import codecs

    path = tmp_path / "out.txt"
    with codecs.open(str(path), "w", encoding="cp1252") as stream:
        wrapped = ensure_unicode_stream(stream)
        assert wrapped is not stream
        wrapped.write("✓")
        wrapped.flush()
        assert path.read_bytes() == "✓".encode()


def test_ensure_unicode_stream_no_buffer_uses_safe_proxy() -> None:
    """Regression: non-UTF-8 streams without a buffer must not crash on icons."""

    class Cp1252Stream:
        encoding = "cp1252"

        def __init__(self) -> None:
            self.data = ""

        def write(self, data: str) -> int:
            self.data += data.encode("cp1252").decode("cp1252")
            return len(data)

        def flush(self) -> None:
            pass

    stream = Cp1252Stream()
    wrapped = ensure_unicode_stream(stream)
    assert wrapped is not stream
    # "✓" is not encodable in cp1252 — the proxy degrades it instead of
    # raising UnicodeEncodeError.
    wrapped.write("✓ check")
    assert stream.data == "? check"


def test_ensure_unicode_stream_closed_buffer_uses_safe_proxy() -> None:
    """A closed buffer cannot be wrapped — fall back to the safe proxy."""
    closed_buffer = io.BytesIO()
    closed_buffer.close()

    class FakeTextStream:
        encoding = "cp1252"

        def __init__(self, buffer: io.BytesIO) -> None:
            self.buffer = buffer

        def write(self, data: str) -> int:
            return len(data)

    stream = FakeTextStream(closed_buffer)
    wrapped = ensure_unicode_stream(stream)
    assert wrapped is not stream
    assert wrapped.write("✓") == 1


def test_ensure_unicode_stream_proxy_forwards_attributes() -> None:
    """The safe proxy forwards unknown attributes to the wrapped stream."""

    class Cp1252Stream:
        encoding = "cp1252"
        custom_attr = "value"

        def write(self, data: str) -> int:
            return len(data)

        def flush(self) -> None:
            pass

        def isatty(self) -> bool:
            return False

    wrapped = ensure_unicode_stream(Cp1252Stream())
    assert wrapped.custom_attr == "value"
    assert wrapped.isatty() is False


# --- sanitize_terminal_text ---


def test_sanitize_terminal_text_strips_ansi() -> None:
    """Regression: ANSI escape sequences must not reach the terminal."""
    assert sanitize_terminal_text("evil\x1b[31mname") == "evil[31mname"


def test_sanitize_terminal_text_keeps_tab_and_newline() -> None:
    assert sanitize_terminal_text("a\tb\nc") == "a\tb\nc"


def test_sanitize_terminal_text_strips_carriage_return_and_bell() -> None:
    assert sanitize_terminal_text("a\rb\x07c") == "abc"


def test_sanitize_terminal_text_non_string() -> None:
    assert sanitize_terminal_text(123) == "123"
