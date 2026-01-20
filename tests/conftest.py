"""Shared fixtures for Pymordial test suite."""

from unittest.mock import Mock, patch

import pytest
from PIL import Image

from pymordial.controller.adb_device import PymordialAdbDevice
from pymordial.controller.bluestacks_device import PymordialBluestacksDevice
from pymordial.controller.image_controller import ImageController
from pymordial.core.pymordial_app import PymordialApp
from pymordial.core.pymordial_screen import PymordialScreen


@pytest.fixture
def mock_config():
    """Mocks the configuration dictionary."""
    config = {
        "adb": {
            "default_host": "127.0.0.1",
            "default_port": 5555,
            "default_timeout": 10,
            "default_wait_time": 1,
            "keyevents": {
                "home": 3,
                "enter": 66,
                "esc": 111,
                "app_switch": 187,
            },
            "app_start_timeout": 10,
            "stream": {
                "resolution": 720,
                "bitrate": "2M",
                "time_limit": 180,
                "queue_size": 1024,
                "read_timeout": 0.5,
                "start_timeout_iterations": 10,
                "start_wait": 0.5,
                "stop_timeout": 5,
            },
            "monkey_verbosity": 2,
            "app_check_retries": 20,
            "process_wait_timeout": 5,
            "commands": {
                "timeout": 10,
                "read_timeout": 10,
                "transport_timeout": 10,
                "screenrecord": "screenrecord ...",
                "dumpsys_focus": "dumpsys ...",
                "force_stop": "am force-stop ...",
                "screencap": "screencap -p",
                "tap": "input tap ...",
                "text": "input text ...",
                "keyevent": "input keyevent ...",
                "monkey": "monkey ...",
            },
        },
        "bluestacks": {
            "process_name": "HD-Player.exe",
            "window_title": "BlueStacks App Player",
            "default_transport_timeout_s": 30,
            "wait_for_load_timeout": 60,
            "hd_player_exe": "HD-Player.exe",
            "default_resolution": [1280, 720],
            "default_max_retries": 3,
            "default_wait_time": 1,
            "default_timeout": 30,
        },
        "controller": {
            "default_click_times": 1,
            "default_max_tries": 3,
            "click_coord_times": 1,
        },
        "app": {
            "action_timeout": 60,
            "action_wait_time": 10,
        },
        "image_controller": {
            "default_find_ui_retries": 3,
        },
        "element": {
            "default_confidence": 0.9,
            "pixel_size": [10, 10],
        },
        "extract_strategy": {
            "default": {
                "upscale_factor": 2.0,
                "denoise_strength": 10,
                "denoise_template_window": 7,
                "denoise_search_window": 21,
                "threshold_binary_max": 255,
                "inversion_threshold_mean": 127,
                "tesseract_config": "--oem 3 --psm 6",
            },
            "revomon": {
                "padding_value_white": 255,
                "adaptive_thresh_block_size": 11,
                "adaptive_thresh_c": 2,
                "move": {
                    "upscale_factor": 3.0,
                    "crop_left_ratio": 0.1,
                    "crop_bottom_ratio": 0.2,
                    "padding": 5,
                    "whitelist_config": "-c tessedit_char_whitelist=abcdef",
                },
                "level": {
                    "crop_left_ratio": 0.5,
                    "whitelist_config": "-c tessedit_char_whitelist=0123456789",
                },
            },
            "tesseract": {
                "default_config": "--oem 3 --psm 6",
                "base_config": "--oem 3",
                "psm": {"single_word": 8, "single_line": 7, "block": 6},
            },
        },
        "easyocr": {"default_languages": ["en"]},
        "setup": {"installer_name": "bs5_installer.exe"},
    }
    # Patch get_config in multiple locations to ensure it's picked up
    # regardless of when/where it was imported.
    with (
        patch("pymordial.utils.config.get_config", return_value=config),
        patch(
            "pymordial.controller.adb_device.get_config",
            return_value=config,
            create=True,
        ),
        patch(
            "pymordial.controller.bluestacks_device.get_config",
            return_value=config,
            create=True,
        ),
        patch(
            "pymordial.controller.image_controller.get_config",
            return_value=config,
            create=True,
        ),
        patch(
            "pymordial.controller.pymordial_controller.get_config",
            return_value=config,
            create=True,
        ),
    ):
        yield config


@pytest.fixture
def mock_adb_device():
    """Mocks the AdbDeviceTcp class."""
    with patch("pymordial.controller.adb_device.AdbDeviceTcp") as mock:
        device_instance = mock.return_value
        device_instance.connect.return_value = True
        device_instance.shell.return_value = b""
        device_instance.available = True
        yield device_instance


@pytest.fixture
def mock_adb_controller(mock_adb_device, mock_config):
    """Returns an PymordialAdbDevice with a mocked device."""
    controller = PymordialAdbDevice()
    return controller


@pytest.fixture
def mock_image_controller(mock_config):
    """Returns an ImageController with mocked dependencies."""
    mock_adb = Mock()
    controller = ImageController(mock_adb)
    return controller


@pytest.fixture
def mock_bluestacks_controller(mock_adb_controller, mock_image_controller, mock_config):
    """Returns a PymordialBluestacksDevice with mocked dependencies."""
    with patch(
        "pymordial.controller.bluestacks_device.win32gui.GetWindowRect"
    ) as mock_rect:
        # Mock window rect to return a standard size
        mock_rect.return_value = (0, 0, 1280, 720)

        controller = PymordialBluestacksDevice(
            adb_bridge_device=mock_adb_controller,
            image_controller=mock_image_controller,
        )
        return controller


@pytest.fixture
def sample_image():
    """Returns a sample PIL Image."""
    return Image.new("RGB", (100, 100), color="white")


@pytest.fixture
def sample_screenshot_bytes():
    """Returns sample screenshot bytes."""
    return b"fake_screenshot_bytes"


@pytest.fixture
def mock_app():
    """Returns a sample PymordialApp."""
    return PymordialApp(app_name="TestApp", package_name="com.example.test")


@pytest.fixture
def mock_screen():
    """Returns a sample PymordialScreen."""
    return PymordialScreen(name="TestScreen")
