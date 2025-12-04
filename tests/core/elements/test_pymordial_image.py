"""Tests for PymordialImage element."""

from pathlib import Path

import pytest

from pymordial.core.elements.pymordial_image import PymordialImage


def test_pymordial_image_init(mock_config):
    """Test image element initialization."""
    image = PymordialImage(
        label="TestImage",
        filepath="test.png",
        confidence=0.8,
    )

    assert image.label == "testimage"  # Labels are lowercase
    assert image.filepath == Path("test.png").resolve()
    assert image.confidence == 0.8
    assert image.og_resolution == (1920, 1080)  # Default from config


def test_pymordial_image_with_custom_confidence(mock_config):
    """Test image with custom confidence."""
    image = PymordialImage(
        label="logo",
        filepath="logo.png",
        confidence=0.85,
    )
    assert image.confidence == 0.85


def test_pymordial_image_with_og_resolution(mock_config):
    """Test image with custom og_resolution."""
    image = PymordialImage(
        label="button",
        filepath="button.png",
        confidence=0.8,
        og_resolution=(1280, 720),
    )
    assert image.og_resolution == (1280, 720)


def test_pymordial_image_with_position_and_size(mock_config):
    """Test image with position and size."""
    image = PymordialImage(
        label="icon",
        filepath="icon.png",
        confidence=0.9,
        position=(100, 200),
        size=(50, 50),
    )
    assert image.position == (100, 200)
    assert image.size == (50, 50)
    assert image.center == (125, 225)
    assert image.region == (100, 200, 150, 250)


def test_pymordial_image_with_image_text(mock_config):
    """Test image with optional image_text field."""
    image = PymordialImage(
        label="button",
        filepath="button.png",
        confidence=0.8,
        image_text="Click Me",
    )
    assert image.image_text == "click me"  # Lowercase


def test_pymordial_image_confidence_validation(mock_config):
    """Test confidence must be between 0 and 1."""
    with pytest.raises(ValueError, match="between 0 and 1"):
        PymordialImage(
            label="test",
            filepath="test.png",
            confidence=1.5,
        )

    with pytest.raises(ValueError, match="between 0 and 1"):
        PymordialImage(
            label="test",
            filepath="test.png",
            confidence=-0.1,
        )


def test_pymordial_image_repr(mock_config):
    """Test string representation."""
    image = PymordialImage(
        label="button",
        filepath="button.png",
        confidence=0.8,
        position=(100, 200),
        size=(50, 30),
    )
    repr_str = repr(image)
    assert "PymordialImage" in repr_str
    assert "button" in repr_str
    assert "0.8" in repr_str
