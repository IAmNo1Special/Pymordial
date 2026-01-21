"""Tests for PymordialUiDevice (Image functions)."""

from unittest.mock import Mock, patch

import pytest
from PIL import Image

from pymordial.devices.ui_device import PymordialUiDevice
from pymordial.ui.image import PymordialImage
from pymordial.ui.pixel import PymordialPixel


@pytest.fixture
def mock_adb_device():
    """Create a mock PymordialAdbDevice."""
    adb = Mock()
    # Mock is_connected to return True by default so checks pass
    adb.is_connected.return_value = True
    adb.capture_screen.return_value = b"fake_screenshot"
    return adb


def test_ui_device_init(mock_config, mock_adb_device):
    """Test PymordialUiDevice initialization."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)
    assert device._bridge_device == mock_adb_device


def test_scale_img_to_screen(mock_config, mock_adb_device):
    """Test image scaling to screen."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)
    mock_screen = Image.new("RGB", (1280, 720))
    mock_template = Image.new("RGB", (100, 100))

    with patch(
        "pymordial.devices.ui_device.Image.open",
        return_value=mock_template,
    ):
        result = device.scale_img_to_screen(
            image_path="template.png",
            screen_image=mock_screen,
            bluestacks_resolution=(1280, 720),
        )
        assert isinstance(result, Image.Image)


def test_check_pixel_color_exact_match(mock_config, mock_adb_device):
    """Test pixel color checking with exact match."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    pixel = PymordialPixel(
        label="test_pixel",
        position=(50, 50),
        pixel_color=(255, 0, 0),
        tolerance=0,
    )

    test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))

    # We mock Image.open to return our test_image when called with BytesIO
    with patch("pymordial.devices.ui_device.Image.open", return_value=test_image):
        result = device.check_pixel_color(
            pymordial_pixel=pixel,
            pymordial_screenshot=b"fake_bytes",
        )
        assert result is True


def test_check_pixel_color_no_match(mock_config, mock_adb_device):
    """Test pixel color checking with no match."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    pixel = PymordialPixel(
        label="test_pixel",
        position=(50, 50),
        pixel_color=(0, 255, 0),  # Green
        tolerance=0,
    )

    test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))  # Red

    with patch("pymordial.devices.ui_device.Image.open", return_value=test_image):
        result = device.check_pixel_color(
            pymordial_pixel=pixel,
            pymordial_screenshot=b"fake_bytes",
        )
        assert result is False


def test_check_pixel_color_with_tolerance(mock_config, mock_adb_device):
    """Test pixel color checking with tolerance."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    pixel = PymordialPixel(
        label="test_pixel",
        position=(50, 50),
        pixel_color=(250, 5, 5),
        tolerance=10,
    )

    test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))

    with patch("pymordial.devices.ui_device.Image.open", return_value=test_image):
        result = device.check_pixel_color(
            pymordial_pixel=pixel,
            pymordial_screenshot=b"fake_bytes",
        )
        assert result is True


def test_where_element_not_found(mock_config, mock_adb_device):
    """Test where_element when element not found."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    image_elem = PymordialImage(
        label="test",
        filepath="test.png",
        confidence=0.8,
        og_resolution=(1920, 1080),
    )

    # Create test images
    mock_screen = Image.new("RGB", (1920, 1080), color=(0, 0, 0))
    mock_template = Image.new("RGB", (100, 100), color=(255, 255, 255))

    with patch(
        "pymordial.devices.ui_device.Image.open",
        return_value=mock_template,
    ):
        # We need to mock 'locate' to return None
        with patch("pymordial.devices.ui_device.locate", return_value=None):
            result = device.where_element(
                pymordial_element=image_elem,
                pymordial_screenshot=mock_screen,
                max_tries=1,  # Important to avoid infinite loop if max_tries defaults to None/infinite
            )
            assert result is None
