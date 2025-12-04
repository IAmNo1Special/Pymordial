"""Tests for PymordialPixel element."""

import pytest

from pymordial.core.elements.pymordial_pixel import PymordialPixel


def test_pymordial_pixel_init(mock_config):
    """Test pixel element initialization."""
    pixel = PymordialPixel(
        label="health_indicator",
        position=(100, 50),
        pixel_color=(255, 0, 0),  # Red
    )

    assert pixel.label == "health_indicator"
    assert pixel.position == (100, 50)
    assert pixel.pixel_color == (255, 0, 0)
    assert pixel.tolerance == 0  # Default
    # Size is set from config pixel_size
    assert pixel.size == (1, 1)


def test_pymordial_pixel_with_tolerance(mock_config):
    """Test pixel with color tolerance."""
    pixel = PymordialPixel(
        label="status",
        position=(200, 100),
        pixel_color=(0, 255, 0),  # Green
        tolerance=15,
    )
    assert pixel.tolerance == 15


def test_pymordial_pixel_with_og_resolution(mock_config):
    """Test pixel with custom og_resolution."""
    pixel = PymordialPixel(
        label="indicator",
        position=(50, 50),
        pixel_color=(128, 128, 128),
        og_resolution=(1280, 720),
    )
    assert pixel.og_resolution == (1280, 720)


def test_pymordial_pixel_color_validation(mock_config):
    """Test pixel color validation."""
    # Color values must be 0-255
    with pytest.raises(ValueError, match="between 0 and 255"):
        PymordialPixel(
            label="test",
            position=(0, 0),
            pixel_color=(256, 0, 0),
        )

    with pytest.raises(ValueError, match="between 0 and 255"):
        PymordialPixel(
            label="test",
            position=(0, 0),
            pixel_color=(-1, 0, 0),
        )


def test_pymordial_pixel_color_tuple_length(mock_config):
    """Test pixel color must have 3 values."""
    with pytest.raises(ValueError, match="3 values"):
        PymordialPixel(
            label="test",
            position=(0, 0),
            pixel_color=(255, 0),  # Only 2 values
        )


def test_pymordial_pixel_tolerance_validation(mock_config):
    """Test tolerance validation."""
    with pytest.raises(ValueError, match="between 0 and 255"):
        PymordialPixel(
            label="test",
            position=(0, 0),
            pixel_color=(255, 255, 255),
            tolerance=256,
        )

    with pytest.raises(ValueError, match="between 0 and 255"):
        PymordialPixel(
            label="test",
            position=(0, 0),
            pixel_color=(255, 255, 255),
            tolerance=-1,
        )


def test_pymordial_pixel_repr(mock_config):
    """Test string representation."""
    pixel = PymordialPixel(
        label="dot",
        position=(150, 200),
        pixel_color=(100, 100, 100),
        tolerance=10,
    )
    repr_str = repr(pixel)
    assert "PymordialPixel" in repr_str
    assert "dot" in repr_str
    assert "(100, 100, 100)" in repr_str
    assert "10" in repr_str
