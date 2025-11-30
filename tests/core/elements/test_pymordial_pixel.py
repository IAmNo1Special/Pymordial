"""Tests for PymordialPixel element."""

from unittest.mock import Mock, patch

from pymordial.core.elements.pymordial_pixel import PymordialPixel


def test_pymordial_pixel_init(mock_config):
    """Test pixel element initialization."""
    with patch("pymordial.core.elements.pymordial_pixel.PIXEL_SIZE", (10, 10)):
        pixel = PymordialPixel(
            label="health_indicator",
            position=(100, 50),
            pixel_color=(255, 0, 0),  # Red
            bluestacks_resolution=(1280, 720),
        )

        assert pixel.label == "health_indicator"
        assert pixel.position == (100, 50)
        assert pixel.pixel_color == (255, 0, 0)
        assert pixel.tolerance == 0
        assert pixel.size == (10, 10)  # From config


def test_pymordial_pixel_with_tolerance(mock_config):
    """Test pixel with color tolerance."""
    pixel = PymordialPixel(
        label="status",
        position=(200, 100),
        pixel_color=(0, 255, 0),  # Green
        bluestacks_resolution=(1280, 720),
        tolerance=15,
    )

    assert pixel.tolerance == 15


def test_pymordial_pixel_match_success(mock_config):
    """Test pixel matching when color matches."""
    pixel = PymordialPixel(
        label="ready",
        position=(100, 50),
        pixel_color=(255, 255, 255),  # White
        bluestacks_resolution=(1280, 720),
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot

    # Mock check_pixel_color to return True
    mock_image_controller.check_pixel_color.return_value = True

    result = pixel.match(mock_bs_controller, mock_image_controller)

    assert result == (100, 50)
    mock_image_controller.check_pixel_color.assert_called_once_with(
        target_coords=(100, 50),
        target_color=(255, 255, 255),
        image=screenshot,
        tolerance=0,
    )


def test_pymordial_pixel_match_failure(mock_config):
    """Test pixel matching when color doesn't match."""
    pixel = PymordialPixel(
        label="inactive",
        position=(100, 50),
        pixel_color=(128, 128, 128),  # Gray
        bluestacks_resolution=(1280, 720),
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot

    # Mock check_pixel_color to return False
    mock_image_controller.check_pixel_color.return_value = False

    result = pixel.match(mock_bs_controller, mock_image_controller)

    assert result is None


def test_pymordial_pixel_match_no_screenshot(mock_config):
    """Test pixel matching when screenshot capture fails."""
    pixel = PymordialPixel(
        label="check",
        position=(50, 50),
        pixel_color=(0, 0, 0),  # Black
        bluestacks_resolution=(1280, 720),
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    mock_bs_controller.capture_screen.return_value = None

    result = pixel.match(mock_bs_controller, mock_image_controller)

    assert result is None


def test_pymordial_pixel_match_with_tolerance(mock_config):
    """Test pixel matching with tolerance parameter."""
    pixel = PymordialPixel(
        label="approx",
        position=(75, 75),
        pixel_color=(200, 200, 200),
        bluestacks_resolution=(1280, 720),
        tolerance=20,
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot
    mock_image_controller.check_pixel_color.return_value = True

    pixel.match(mock_bs_controller, mock_image_controller)

    # Should pass tolerance to check_pixel_color
    mock_image_controller.check_pixel_color.assert_called_once_with(
        target_coords=(75, 75),
        target_color=(200, 200, 200),
        image=screenshot,
        tolerance=20,
    )


def test_pymordial_pixel_center_property(mock_config):
    """Test that pixel center equals position."""
    with patch("pymordial.core.elements.pymordial_pixel.PIXEL_SIZE", (10, 10)):
        pixel = PymordialPixel(
            label="dot",
            position=(150, 200),
            pixel_color=(100, 100, 100),
            bluestacks_resolution=(1280, 720),
        )

        # Center should be calculated from position and size
        assert pixel.center == (155, 205)  # position + size//2
