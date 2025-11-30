"""Tests for PymordialImage element."""

from unittest.mock import Mock, patch

from PIL import Image
from pymordial.core.elements.pymordial_image import PymordialImage


def test_pymordial_image_init(mock_config):
    """Test image element initialization."""
    # Since the module loads the real config at import time, we expect the value from your config.yaml
    image_elem = PymordialImage(
        label="TestImage", asset_path="test.png", bluestacks_resolution=(1280, 720)
    )

    assert image_elem.label == "testimage"
    assert image_elem.asset_path == "test.png"
    assert image_elem.bluestacks_resolution == (1280, 720)
    assert image_elem.confidence == 0.7  # Matches your config.yaml


def test_pymordial_image_with_custom_confidence(mock_config):
    """Test image with custom confidence."""
    image_elem = PymordialImage(
        label="logo",
        asset_path="logo.png",
        bluestacks_resolution=(1280, 720),
        confidence=0.85,
    )

    assert image_elem.confidence == 0.85


def test_pymordial_image_match_success(mock_config):
    """Test successful image matching."""
    image_elem = PymordialImage(
        label="button", asset_path="button.png", bluestacks_resolution=(1280, 720)
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot
    mock_bs_controller.ref_window_size = (1280, 720)

    mock_haystack = Image.new("RGB", (1280, 720))
    mock_needle = Image.new("RGB", (50, 50))
    mock_image_controller.scale_img_to_screen.return_value = mock_needle

    with patch(
        "pymordial.core.elements.pymordial_image.Image.open", return_value=mock_haystack
    ):
        with patch("pymordial.core.elements.pymordial_image.locate") as mock_locate:
            with patch("pymordial.core.elements.pymordial_image.center") as mock_center:
                mock_locate.return_value = (100, 200, 150, 250)
                mock_center.return_value = (125, 225)

                result = image_elem.match(mock_bs_controller, mock_image_controller)

                assert result == (125, 225)
                mock_locate.assert_called_once()


def test_pymordial_image_match_not_found(mock_config):
    """Test image matching when element not found."""
    image_elem = PymordialImage(
        label="button", asset_path="button.png", bluestacks_resolution=(1280, 720)
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot
    mock_bs_controller.ref_window_size = (1280, 720)

    mock_haystack = Image.new("RGB", (1280, 720))
    mock_needle = Image.new("RGB", (50, 50))
    mock_image_controller.scale_img_to_screen.return_value = mock_needle

    with patch(
        "pymordial.core.elements.pymordial_image.Image.open", return_value=mock_haystack
    ):
        with patch("pymordial.core.elements.pymordial_image.locate") as mock_locate:
            mock_locate.return_value = None

            result = image_elem.match(mock_bs_controller, mock_image_controller)

            assert result is None


def test_pymordial_image_match_with_exception(mock_config):
    """Test image matching with exception during locate."""
    image_elem = PymordialImage(
        label="button", asset_path="button.png", bluestacks_resolution=(1280, 720)
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot
    mock_bs_controller.ref_window_size = (1280, 720)

    mock_haystack = Image.new("RGB", (1280, 720))
    mock_needle = Image.new("RGB", (50, 50))
    mock_image_controller.scale_img_to_screen.return_value = mock_needle

    with patch(
        "pymordial.core.elements.pymordial_image.Image.open", return_value=mock_haystack
    ):
        with patch("pymordial.core.elements.pymordial_image.locate") as mock_locate:
            mock_locate.side_effect = Exception("Locate failed")

            result = image_elem.match(mock_bs_controller, mock_image_controller)

            assert result is None


def test_pymordial_image_match_no_screenshot(mock_config):
    """Test image matching when screenshot capture fails."""
    image_elem = PymordialImage(
        label="button", asset_path="button.png", bluestacks_resolution=(1280, 720)
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()
    mock_bs_controller.capture_screen.return_value = None

    result = image_elem.match(mock_bs_controller, mock_image_controller)

    assert result is None


def test_pymordial_image_match_with_provided_screenshot(mock_config):
    """Test image matching with pre-provided screenshot."""
    image_elem = PymordialImage(
        label="button", asset_path="button.png", bluestacks_resolution=(1280, 720)
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()
    mock_bs_controller.ref_window_size = (1280, 720)

    screenshot = b"provided_screenshot"
    mock_haystack = Image.new("RGB", (1280, 720))
    mock_needle = Image.new("RGB", (50, 50))
    mock_image_controller.scale_img_to_screen.return_value = mock_needle

    with patch(
        "pymordial.core.elements.pymordial_image.Image.open", return_value=mock_haystack
    ):
        with patch("pymordial.core.elements.pymordial_image.locate") as mock_locate:
            mock_locate.return_value = None

            image_elem.match(
                mock_bs_controller, mock_image_controller, screenshot=screenshot
            )

            mock_bs_controller.capture_screen.assert_not_called()
