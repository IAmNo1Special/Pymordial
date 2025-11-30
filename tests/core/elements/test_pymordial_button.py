"""Tests for PymordialButton element."""

from unittest.mock import patch

from pymordial.core.elements.pymordial_button import PymordialButton


def test_pymordial_button_init(mock_config):
    """Test button initialization."""
    button = PymordialButton(
        label="StartButton",
        asset_path="assets/start.png",
        bluestacks_resolution=(1280, 720),
    )

    assert button.label == "startbutton"  # Labels are lowercase
    assert button.asset_path == "assets/start.png"
    assert button.bluestacks_resolution == (1280, 720)


def test_pymordial_button_with_position_and_size(mock_config):
    """Test button with position and size."""
    button = PymordialButton(
        label="play",
        asset_path="play.png",
        bluestacks_resolution=(1280, 720),
        position=(100, 200),
        size=(50, 30),
    )

    assert button.position == (100, 200)
    assert button.size == (50, 30)
    assert button.center == (125, 215)


def test_pymordial_button_with_confidence(mock_config):
    """Test button with custom confidence."""
    button = PymordialButton(
        label="confirm",
        asset_path="confirm.png",
        bluestacks_resolution=(1280, 720),
        confidence=0.95,
    )

    assert button.confidence == 0.95


def test_pymordial_button_default_confidence(mock_config):
    """Test button uses default confidence from config."""
    # Button inherits from Image, so we patch the Image constant
    with patch("pymordial.core.elements.pymordial_image.DEFAULT_CONFIDENCE", 0.9):
        button = PymordialButton(
            label="cancel", asset_path="cancel.png", bluestacks_resolution=(1280, 720)
        )

        # Should use default from config (0.9)
        assert button.confidence == 0.9


def test_pymordial_button_inherits_from_image(mock_config):
    """Test that PymordialButton inherits from PymordialImage."""
    from pymordial.core.elements.pymordial_image import PymordialImage

    button = PymordialButton(
        label="test", asset_path="test.png", bluestacks_resolution=(1280, 720)
    )

    assert isinstance(button, PymordialImage)
