"""Shared fixtures for Pymordial test suite."""

from unittest.mock import Mock, patch

import pytest
from PIL import Image

from pymordial.core.app import PymordialApp
from pymordial.core.controller import PymordialController
from pymordial.core.screen import PymordialScreen
from pymordial.devices.adb_device import PymordialAdbDevice
from pymordial.devices.bluestacks_device import PymordialBluestacksDevice
from pymordial.devices.ui_device import PymordialUiDevice


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
            "assets": {},
        },
        "bluestacks": {
            "process_name": "HD-Player.exe",
            "window_title": "BlueStacks App Player",
            "default_transport_timeout_s": 30,
            "default_load_timeout": 60,
            "default_load_wait_time": 1,
            "default_ui_load_wait_time": 1,
            "default_process_kill_timeout": 5,
            "hd_player_exe": "HD-Player.exe",
            "default_resolution": [1280, 720],
            "default_open_app_max_retries": 3,
            "default_open_app_wait_time": 1,
            "default_open_app_timeout": 30,
            "ui": {"assets": {}},
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
            "default_wait_time": 1,
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
                "tesseract_cmd": "tesseract",
                "psm": {"single_word": "8", "single_line": "7", "block": "6"},
                "preprocess": {
                    "upscale_factor": 2,
                    "denoise_strength": 10,
                    "denoise_template_window": 7,
                    "denoise_search_window": 21,
                    "threshold_max": 255,
                    "inversion_threshold": 127,
                },
            },
        },
        "setup": {
            "installer_name": "bs5_installer.exe",
            "download_url": "",
            "reg_key": "",
        },
    }
    # Patch get_config in multiple locations to ensure it's picked up
    # regardless of when/where it was imported.
    with (
        patch("pymordial.utils.config.get_config", return_value=config),
        patch(
            "pymordial.devices.adb_device.get_config",
            return_value=config,
            create=True,
        ),
        patch(
            "pymordial.devices.bluestacks_device.get_config",
            return_value=config,
            create=True,
        ),
        patch(
            "pymordial.devices.ui_device.get_config",
            return_value=config,
            create=True,
        ),
        patch(
            "pymordial.core.controller.get_config",
            return_value=config,
            create=True,
        ),
    ):
        yield config


@pytest.fixture
def mock_adb_device():
    """Mocks the AdbDeviceTcp class."""
    with patch("pymordial.devices.adb_device.AdbDeviceTcp") as mock:
        device_instance = mock.return_value
        device_instance.connect.return_value = True
        device_instance.shell.return_value = b""
        device_instance.available = True
        yield device_instance


@pytest.fixture
def mock_adb_controller(mock_adb_device, mock_config):
    """Returns an PymordialAdbDevice with a mocked device."""
    controller = PymordialAdbDevice(config=mock_config["adb"])
    return controller


@pytest.fixture
def mock_vision_device(mock_adb_controller, mock_config):
    """Returns a PymordialUiDevice with mocked dependencies."""
    # UiDevice uses AdbDevice for bridging
    device = PymordialUiDevice(bridge_device=mock_adb_controller, config=mock_config)
    return device


@pytest.fixture
def mock_bluestacks_device(mock_adb_controller, mock_vision_device, mock_config):
    """Returns a PymordialBluestacksDevice with mocked dependencies."""
    with (
        patch("pymordial.devices.bluestacks_device.psutil"),
        patch("pymordial.devices.bluestacks_device.os.path.exists", return_value=True),
        patch("pymordial.devices.bluestacks_device.os.startfile"),
    ):
        device = PymordialBluestacksDevice(
            adb_bridge_device=mock_adb_controller,
            vision_device=mock_vision_device,
            config=mock_config["bluestacks"],
        )
        return device


@pytest.fixture
def mock_controller(mock_adb_controller, mock_vision_device, mock_bluestacks_device):
    """Returns a PymordialController with mocked dependencies."""
    controller = PymordialController()
    controller.adb = mock_adb_controller
    controller.ui = mock_vision_device
    controller.bluestacks = mock_bluestacks_device
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
