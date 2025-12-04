"""Tests for ImageController."""

from unittest.mock import Mock, patch

import pytest
from PIL import Image

from pymordial.controller.image_controller import ImageController
from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.elements.pymordial_pixel import PymordialPixel


@pytest.fixture
def mock_pymordial_controller():
    """Create a mock PymordialController."""
    controller = Mock()
    controller.adb = Mock()
    controller.bluestacks = Mock()
    controller.adb.capture_screenshot.return_value = b"fake_screenshot"
    return controller


def test_image_controller_init(mock_config, mock_pymordial_controller):
    """Test ImageController initialization."""
    controller = ImageController(mock_pymordial_controller)
    assert controller.pymordial_controller == mock_pymordial_controller


def test_scale_img_to_screen(mock_config, mock_pymordial_controller):
    """Test image scaling to screen."""
    controller = ImageController(mock_pymordial_controller)
    mock_screen = Image.new("RGB", (1280, 720))
    mock_template = Image.new("RGB", (100, 100))

    with patch(
        "pymordial.controller.image_controller.Image.open",
        return_value=mock_template,
    ):
        result = controller.scale_img_to_screen(
            image_path="template.png",
            screen_image=mock_screen,
            bluestacks_resolution=(1280, 720),
        )
        assert isinstance(result, Image.Image)


def test_check_pixel_color_exact_match(mock_config, mock_pymordial_controller):
    """Test pixel color checking with exact match."""
    controller = ImageController(mock_pymordial_controller)

    pixel = PymordialPixel(
        label="test_pixel",
        position=(50, 50),
        pixel_color=(255, 0, 0),
        tolerance=0,
    )

    test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))

    with patch(
        "pymordial.controller.image_controller.Image.open", return_value=test_image
    ):
        result = controller.check_pixel_color(
            pymordial_pixel=pixel,
            screenshot_img_bytes=b"fake_bytes",
        )
        assert result is True


def test_check_pixel_color_no_match(mock_config, mock_pymordial_controller):
    """Test pixel color checking with no match."""
    controller = ImageController(mock_pymordial_controller)

    pixel = PymordialPixel(
        label="test_pixel",
        position=(50, 50),
        pixel_color=(0, 255, 0),  # Green
        tolerance=0,
    )

    test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))  # Red

    with patch(
        "pymordial.controller.image_controller.Image.open", return_value=test_image
    ):
        result = controller.check_pixel_color(
            pymordial_pixel=pixel,
            screenshot_img_bytes=b"fake_bytes",
        )
        assert result is False


def test_check_pixel_color_with_tolerance(mock_config, mock_pymordial_controller):
    """Test pixel color checking with tolerance."""
    controller = ImageController(mock_pymordial_controller)

    pixel = PymordialPixel(
        label="test_pixel",
        position=(50, 50),
        pixel_color=(250, 5, 5),
        tolerance=10,
    )

    test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))

    with patch(
        "pymordial.controller.image_controller.Image.open", return_value=test_image
    ):
        result = controller.check_pixel_color(
            pymordial_pixel=pixel,
            screenshot_img_bytes=b"fake_bytes",
        )
        assert result is True


def test_where_element_not_found(mock_config, mock_pymordial_controller):
    """Test where_element when element not found."""
    controller = ImageController(mock_pymordial_controller)

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
        "pymordial.controller.image_controller.Image.open",
        return_value=mock_template,
    ):
        with patch("pymordial.controller.image_controller.locate", return_value=None):
            result = controller.where_element(
                pymordial_element=image_elem,
                screenshot_img_bytes=mock_screen,
            )
            assert result is None


def test_image_controller_repr(mock_config, mock_pymordial_controller):
    """Test string representation."""
    controller = ImageController(mock_pymordial_controller)
    repr_str = repr(controller)
    assert "ImageController" in repr_str
