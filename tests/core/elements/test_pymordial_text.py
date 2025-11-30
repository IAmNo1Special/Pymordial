"""Tests for PymordialText element."""

from unittest.mock import Mock

from pymordial.core.elements.pymordial_text import PymordialText
from pymordial.core.extract_strategy import DefaultExtractStrategy


def test_pymordial_text_init(mock_config):
    """Test text element initialization."""
    text_elem = PymordialText(
        label="username", text="Player123", bluestacks_resolution=(1280, 720)
    )

    assert text_elem.label == "username"
    assert text_elem.text == "Player123"
    assert text_elem.bluestacks_resolution == (1280, 720)
    assert text_elem.extract_strategy is None


def test_pymordial_text_with_strategy(mock_config):
    """Test text element with extract strategy."""
    strategy = DefaultExtractStrategy()
    text_elem = PymordialText(
        label="title",
        text="Welcome",
        bluestacks_resolution=(1280, 720),
        extract_strategy=strategy,
    )

    assert text_elem.extract_strategy == strategy


def test_pymordial_text_with_position_and_size(mock_config):
    """Test text element with position and size."""
    text_elem = PymordialText(
        label="score",
        text="1000",
        bluestacks_resolution=(1280, 720),
        position=(100, 50),
        size=(200, 30),
    )

    assert text_elem.position == (100, 50)
    assert text_elem.size == (200, 30)
    assert text_elem.center == (200, 65)


def test_pymordial_text_match_found(mock_config):
    """Test text matching when text is found."""
    text_elem = PymordialText(
        label="title",
        text="Welcome",
        bluestacks_resolution=(1280, 720),
        position=(640, 100),
        size=(200, 50),
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot

    # Mock check_text to return True
    mock_image_controller.check_text.return_value = True

    result = text_elem.match(mock_bs_controller, mock_image_controller)

    assert result == (740, 125)  # Should return center
    mock_image_controller.check_text.assert_called_once_with(
        text_to_find="Welcome", image_path=screenshot, strategy=None
    )


def test_pymordial_text_match_not_found(mock_config):
    """Test text matching when text is not found."""
    text_elem = PymordialText(
        label="error", text="Error", bluestacks_resolution=(1280, 720)
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot

    # Mock check_text to return False
    mock_image_controller.check_text.return_value = False

    result = text_elem.match(mock_bs_controller, mock_image_controller)

    assert result is None


def test_pymordial_text_match_no_screenshot(mock_config):
    """Test text matching when screenshot capture fails."""
    text_elem = PymordialText(
        label="title", text="Welcome", bluestacks_resolution=(1280, 720)
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    mock_bs_controller.capture_screen.return_value = None

    result = text_elem.match(mock_bs_controller, mock_image_controller)

    assert result is None


def test_pymordial_text_match_fallback_to_origin(mock_config):
    """Test text matching fallback when no position set."""
    text_elem = PymordialText(
        label="title",
        text="Welcome",
        bluestacks_resolution=(1280, 720),
        # No position or size
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot
    mock_image_controller.check_text.return_value = True

    result = text_elem.match(mock_bs_controller, mock_image_controller)

    # Should fallback to (0, 0) when no center available
    assert result == (0, 0)


def test_pymordial_text_match_with_strategy(mock_config):
    """Test text matching with strategy."""
    strategy = DefaultExtractStrategy()
    text_elem = PymordialText(
        label="level",
        text="42",
        bluestacks_resolution=(1280, 720),
        extract_strategy=strategy,
    )

    mock_bs_controller = Mock()
    mock_image_controller = Mock()

    screenshot = b"fake_screenshot"
    mock_bs_controller.capture_screen.return_value = screenshot
    mock_image_controller.check_text.return_value = True

    text_elem.match(mock_bs_controller, mock_image_controller)

    # Should pass strategy to check_text
    mock_image_controller.check_text.assert_called_once_with(
        text_to_find="42", image_path=screenshot, strategy=strategy
    )
