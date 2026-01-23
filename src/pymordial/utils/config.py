"""Utility for loading the central configuration file.

The configuration is loaded lazily on first import and cached for the
lifetime of the process.
"""

from pathlib import Path
from typing import TypedDict

import yaml

# Paths
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
# Package defaults (tracked in git)
_DEFAULT_CONFIG_PATH = _PACKAGE_ROOT / "configs.yaml"

# User overrides (gitignored, optional)
_USER_CONFIG_PATH = _PROJECT_ROOT / "pymordial_config.yaml"

_CONFIG = None


class AppConfig(TypedDict):
    """Configuration schema for application settings.

    Attributes:
        action_timeout: Max seconds to wait for actions like launch/close.
        action_wait_time: Seconds to wait after performing an action.
        ready_check_max_tries: Max attempts to check if app is ready.
        close_wait_time: Seconds to wait after closing an app.
    """

    action_timeout: int
    action_wait_time: int
    ready_check_max_tries: int
    close_wait_time: int


class ElementConfig(TypedDict):
    """Configuration schema for UI element settings.

    Attributes:
        default_confidence: Default match confidence (0.0 - 1.0) for images.
        pixel_size: Default [width, height] for pixel checks.
    """

    default_confidence: float
    pixel_size: list[int]


class ControllerConfig(TypedDict):
    """Configuration schema for controller interaction settings.

    Attributes:
        default_click_times: Default number of clicks per action.
        default_max_tries: Default attempts to find an element.
        click_coord_times: Number of clicks when clicking coordinates.
    """

    default_click_times: int
    default_max_tries: int
    click_coord_times: int


class PymordialConfig(TypedDict):
    """Root configuration schema.

    Attributes:
        app: Application settings.
        element: Element settings.
        controller: Controller settings.
    """

    app: AppConfig
    element: ElementConfig
    controller: ControllerConfig


def _validate_config(config: dict) -> None:
    """Validates that the configuration contains all required keys.

    Args:
        config: The configuration dictionary to validate.

    Raises:
        ValueError: If a required key is missing.
    """
    required_keys = ["app", "element", "controller"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config section: {key}")


def _load_config() -> PymordialConfig:
    """Loads config from package defaults and optional user overrides.

    Returns:
        The merged configuration dictionary.

    Raises:
        FileNotFoundError: If the package default config file is missing.
        ValueError: If the configuration is invalid.
    """
    global _CONFIG

    # Load package defaults
    if not _DEFAULT_CONFIG_PATH.exists():
        raise FileNotFoundError(f"Package config not found: {_DEFAULT_CONFIG_PATH}")

    with open(_DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # Merge user overrides if present
    if _USER_CONFIG_PATH.exists():
        with open(_USER_CONFIG_PATH, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
            _deep_merge(config, user_config)

    _validate_config(config)
    _CONFIG = config  # type: ignore
    return _CONFIG  # type: ignore


def _deep_merge(base: dict, override: dict) -> None:
    """Recursively merges override dict into base dict.

    Args:
        base: The dictionary to merge into.
        override: The dictionary containing values to merge.
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def get_config() -> PymordialConfig:
    """Retrieves the configuration dictionary.

    Loads package defaults from src/pymordial/configs.yaml
    and merges with user config.yaml at project root if present.

    Returns:
        The configuration dictionary.

    Raises:
        FileNotFoundError: If package config not found.
        ValueError: If the configuration is invalid.
    """
    global _CONFIG
    if _CONFIG is None:
        _load_config()
    return _CONFIG  # type: ignore
