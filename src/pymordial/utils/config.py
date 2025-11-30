"""Utility for loading the central configuration file.

The configuration is loaded lazily on first import and cached for the
lifetime of the process.
"""

from pathlib import Path
from typing import TypedDict

import yaml

# Paths
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # f:\Pymordial
_PACKAGE_ROOT = Path(__file__).resolve().parents[1]  # src/pymordial
# Package defaults (tracked in git)
_DEFAULT_CONFIG_PATH = _PACKAGE_ROOT / "configs.yaml"

# User overrides (gitignored, optional)
_USER_CONFIG_PATH = _PROJECT_ROOT / "config.yaml"

_CONFIG = None


class AdbStreamConfig(TypedDict):
    resolution: int
    bitrate: str
    time_limit: int
    queue_size: int
    read_timeout: float
    start_timeout_iterations: int
    start_wait: float
    stop_timeout: int


class AdbKeyEventsConfig(TypedDict):
    home: int
    enter: int
    esc: int
    app_switch: str


class AdbCommandsConfig(TypedDict):
    screenrecord: str
    dumpsys_focus: str
    force_stop: str
    screencap: str
    tap: str
    text: str
    keyevent: str
    monkey: str


class AdbConfig(TypedDict):
    default_ip: str
    default_port: int
    default_max_retries: int
    default_wait_time: int
    default_timeout: int
    process_wait_timeout: int
    app_start_timeout: int
    stream: AdbStreamConfig
    monkey_verbosity: int
    app_check_retries: int
    keyevents: AdbKeyEventsConfig
    commands: AdbCommandsConfig


class BluestacksUiConfig(TypedDict):
    loading_img_label: str
    loading_text: str
    my_games_button_label: str
    my_games_text: str
    store_search_input_label: str
    store_search_text: str
    store_button_label: str
    playstore_search_input_label: str
    loading_screen_img_label: str
    adb_screenshot_img_label: str


class BluestacksConfig(TypedDict):
    resolution: list[int]
    default_max_retries: int
    default_wait_time: int
    default_timeout: int
    default_transport_timeout_s: float
    wait_for_load_timeout: int
    hd_player_exe: str
    window_title: str
    ui: BluestacksUiConfig


class ImageControllerConfig(TypedDict):
    default_find_ui_retries: int


class AppConfig(TypedDict):
    action_timeout: int
    action_wait_time: int


class ElementConfig(TypedDict):
    default_confidence: float
    pixel_size: list[int]


class ExtractStrategyDefaultConfig(TypedDict):
    upscale_factor: int
    denoise_strength: int
    denoise_template_window: int
    denoise_search_window: int
    threshold_binary_max: int
    inversion_threshold_mean: int
    tesseract_config: str


class RevomonMoveConfig(TypedDict):
    upscale_factor: int
    crop_left_ratio: float
    crop_bottom_ratio: float
    padding: int
    whitelist_config: str


class RevomonLevelConfig(TypedDict):
    crop_left_ratio: float
    whitelist_config: str


class RevomonConfig(TypedDict):
    move: RevomonMoveConfig
    level: RevomonLevelConfig
    padding_value_white: int
    adaptive_thresh_block_size: int
    adaptive_thresh_c: int


class TesseractPsmConfig(TypedDict):
    single_word: str
    single_line: str
    block: str


class TesseractPreprocessConfig(TypedDict):
    upscale_factor: int
    denoise_strength: int
    denoise_template_window: int
    denoise_search_window: int
    threshold_max: int
    inversion_threshold: int


class TesseractConfig(TypedDict):
    base_config: str
    default_config: str
    tesseract_cmd: str
    preprocess: TesseractPreprocessConfig
    psm: TesseractPsmConfig


class ExtractStrategyConfig(TypedDict):
    default: ExtractStrategyDefaultConfig
    revomon: RevomonConfig
    tesseract: TesseractConfig


class EasyOcrConfig(TypedDict):
    default_languages: list[str]


class SetupConfig(TypedDict):
    installer_name: str
    download_url: str
    reg_key: str


class AssetsConfig(TypedDict):
    bluestacks_loading_img: str
    bluestacks_my_games_button: str
    bluestacks_store_search_input: str
    bluestacks_store_button: str
    bluestacks_playstore_search_input: str
    bluestacks_loading_screen_img: str
    adb_screenshot_img: str


class ControllerConfig(TypedDict):
    default_click_times: int
    default_max_tries: int
    click_coord_times: int


class PymordialConfig(TypedDict):
    adb: AdbConfig
    bluestacks: BluestacksConfig
    image_controller: ImageControllerConfig
    app: AppConfig
    element: ElementConfig
    extract_strategy: ExtractStrategyConfig
    easyocr: EasyOcrConfig
    setup: SetupConfig
    assets: AssetsConfig
    controller: ControllerConfig


def _validate_config(config: dict) -> None:
    """Validates that the configuration contains all required keys.

    Args:
        config: The configuration dictionary to validate.

    Raises:
        ValueError: If a required key is missing.
    """
    required_keys = [
        "adb",
        "bluestacks",
        "image_controller",
        "app",
        "element",
        "extract_strategy",
        "easyocr",
        "setup",
        "assets",
        "controller",
    ]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config section: {key}")

    # Basic nested validation (can be expanded)
    if "ui" not in config["bluestacks"]:
        raise ValueError("Missing required config section: bluestacks.ui")
    if "commands" not in config["adb"]:
        raise ValueError("Missing required config section: adb.commands")
    if "assets" not in config:
        raise ValueError("Missing required config section: assets")


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
