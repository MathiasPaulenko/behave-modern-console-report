"""Configuration for the modern console formatter.

Configuration values are read from Behave user data (``-D key=value``) and
fall back to environment variables. The formatter automatically detects CI
environments and adjusts defaults accordingly.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Verbosity(Enum):
    """Output verbosity level."""

    MINIMAL = "minimal"
    NORMAL = "normal"
    VERBOSE = "verbose"
    DEBUG = "debug"


class ThemeName(Enum):
    """Built-in theme names."""

    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    MINIMAL = "minimal"
    MONOCHROME = "monochrome"


def _is_ci_environment() -> bool:
    """Return True if running in a known CI environment."""
    ci_vars = [
        "CI",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "CIRCLECI",
        "TRAVIS",
        "JENKINS_URL",
        "BUILDKITE",
        "DRONE",
        "TF_BUILD",
        "APPVEYOR",
        "AZURE_DEVOPS",
    ]
    return any(os.environ.get(var, "").lower() in ("true", "1", "yes") for var in ci_vars)


def _is_interactive(colors: bool) -> bool:
    """Return True if interactive animations should be used."""
    return colors and sys.stdout.isatty() and not _is_ci_environment()


def _str_to_bool(value: str | bool | None, default: bool) -> bool:
    """Convert a string or boolean value to a boolean."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.lower() in ("true", "1", "yes", "on")


def _get_user_data(config: Any) -> dict[str, str]:
    """Extract user data from a Behave configuration object."""
    user_data = getattr(config, "userdata", None) or {}
    return {str(key): str(value) for key, value in user_data.items()}


def _get_option(
    user_data: dict[str, str], env_name: str, data_name: str, default: str
) -> str:
    """Read a configuration option from user data or environment.

    Supports the new ``mcr.*`` naming convention (preferred) as well as the
    legacy ``modern_console_*`` naming. The new ``mcr.*`` keys take precedence.
    """
    mcr_name = data_name.replace("modern_console_", "mcr.")
    mcr_env_name = env_name.replace("MODERN_CONSOLE_", "MCR_")

    value = user_data.get(mcr_name)
    if value is not None:
        return value
    value = user_data.get(data_name)
    if value is not None:
        return value
    value = os.environ.get(mcr_env_name)
    if value is not None:
        return value
    return os.environ.get(env_name, default)


@dataclass
class Config:
    """Formatter configuration."""

    theme: ThemeName = ThemeName.DEFAULT
    verbosity: Verbosity = Verbosity.NORMAL
    colors: bool = True
    compact: bool = False
    show_steps: bool = False
    show_steps_auto: bool = True
    show_durations: bool = True
    show_progress: bool = True
    show_environment: bool = False
    show_traceback: bool = True
    live: bool = True
    is_ci: bool = False
    is_interactive: bool = True

    @classmethod
    def from_behave(cls, config: Any) -> "Config":
        """Create a Config from a Behave configuration object.

        Args:
            config: Behave configuration object with ``userdata`` attribute.

        Returns:
            A fully resolved Config instance.
        """
        user_data = _get_user_data(config)
        is_ci = _is_ci_environment()

        theme_name = _get_option(user_data, "MODERN_CONSOLE_THEME", "modern_console_theme", "default")
        verbosity_name = _get_option(
            user_data, "MODERN_CONSOLE_VERBOSITY", "modern_console_verbosity", "normal"
        )
        colors_value = _get_option(user_data, "MODERN_CONSOLE_COLORS", "modern_console_colors", "auto")
        compact_value = _get_option(user_data, "MODERN_CONSOLE_COMPACT", "modern_console_compact", "false")
        show_steps_value = _get_option(
            user_data, "MODERN_CONSOLE_SHOW_STEPS", "modern_console_show_steps", "auto"
        )
        show_durations_value = _get_option(
            user_data, "MODERN_CONSOLE_SHOW_DURATIONS", "modern_console_show_durations", "true"
        )
        show_progress_value = _get_option(
            user_data, "MODERN_CONSOLE_SHOW_PROGRESS", "modern_console_show_progress", "true"
        )
        show_environment_value = _get_option(
            user_data, "MODERN_CONSOLE_SHOW_ENVIRONMENT", "modern_console_show_environment", "false"
        )
        show_traceback_value = _get_option(
            user_data, "MODERN_CONSOLE_SHOW_TRACEBACK", "modern_console_show_traceback", "true"
        )
        live_value = _get_option(
            user_data, "MODERN_CONSOLE_LIVE", "modern_console_live", "auto"
        )

        colors_auto = colors_value == "auto"
        colors_enabled = _str_to_bool(
            colors_value, default=(not is_ci and sys.stdout.isatty())
        )
        show_steps_auto = show_steps_value == "auto"
        show_steps_enabled = (
            False
            if show_steps_auto
            else _str_to_bool(show_steps_value, default=False)
        )

        live_auto = live_value == "auto"
        live_enabled = _str_to_bool(
            live_value, default=(not is_ci and sys.stdout.isatty())
        )

        return cls(
            theme=ThemeName(theme_name.lower()),
            verbosity=Verbosity(verbosity_name.lower()),
            colors=colors_enabled,
            compact=_str_to_bool(compact_value, default=False),
            show_steps=show_steps_enabled,
            show_steps_auto=show_steps_auto,
            show_durations=_str_to_bool(show_durations_value, default=True),
            show_progress=_str_to_bool(show_progress_value, default=True),
            show_environment=_str_to_bool(show_environment_value, default=False),
            show_traceback=_str_to_bool(show_traceback_value, default=True),
            live=live_enabled,
            is_ci=is_ci,
            is_interactive=live_enabled and colors_enabled and not is_ci,
        )

    def effective_show_steps(self) -> bool:
        """Return whether step-level output should be shown.

        When ``show_steps_auto`` is True, step output is enabled for verbose
        and debug verbosity levels.
        """
        if self.show_steps_auto:
            return self.verbosity in (Verbosity.VERBOSE, Verbosity.DEBUG)
        return self.show_steps
