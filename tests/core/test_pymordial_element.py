"""Tests for PymordialElement abstract base class."""

import pytest

from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.elements.pymordial_pixel import PymordialPixel
from pymordial.core.elements.pymordial_text import PymordialText


def test_pymordial_element_label_lowercase(mock_config):
    """Test that labels are converted to lowercase."""
    image = PymordialImage(
        label="MyButton",
        filepath="test.png",
        confidence=0.8,
    )
    assert image.label == "mybutton"


def test_pymordial_element_label_validation(mock_config):
    """Test label validation."""
    with pytest.raises(ValueError, match="empty"):
        PymordialImage(label="", filepath="test.png", confidence=0.8)

    with pytest.raises(ValueError, match="empty"):
        PymordialImage(label="   ", filepath="test.png", confidence=0.8)


def test_region_property_with_position_and_size(mock_config):
    """Test region property calculation."""
    image = PymordialImage(
        label="test",
        filepath="test.png",
        confidence=0.8,
        position=(100, 200),
        size=(50, 30),
    )
    assert image.region == (100, 200, 150, 230)  # (left, top, right, bottom)


def test_region_property_without_position(mock_config):
    """Test region returns None when position not set."""
    image = PymordialImage(
        label="test",
        filepath="test.png",
        confidence=0.8,
        size=(50, 30),
    )
    assert image.region is None


def test_region_property_without_size(mock_config):
    """Test region returns None when size not set."""
    image = PymordialImage(
        label="test",
        filepath="test.png",
        confidence=0.8,
        position=(100, 200),
    )
    assert image.region is None


def test_center_property_with_position_and_size(mock_config):
    """Test center property calculation."""
    image = PymordialImage(
        label="test",
        filepath="test.png",
        confidence=0.8,
        position=(100, 200),
        size=(50, 30),
    )
    assert image.center == (125, 215)  # (x + w//2, y + h//2)


def test_center_property_with_only_position(mock_config):
    """Test center returns position when size not set."""
    image = PymordialImage(
        label="test",
        filepath="test.png",
        confidence=0.8,
        position=(100, 200),
    )
    assert image.center == (100, 200)


def test_center_property_without_position(mock_config):
    """Test center returns None when position not set."""
    image = PymordialImage(
        label="test",
        filepath="test.png",
        confidence=0.8,
    )
    assert image.center is None


def test_og_resolution_defaults_to_config(mock_config):
    """Test og_resolution defaults from config."""
    image = PymordialImage(
        label="test",
        filepath="test.png",
        confidence=0.8,
    )
    # Should default to config value (1920, 1080)
    assert image.og_resolution == (1920, 1080)


def test_og_resolution_custom(mock_config):
    """Test custom og_resolution."""
    image = PymordialImage(
        label="test",
        filepath="test.png",
        confidence=0.8,
        og_resolution=(1280, 720),
    )
    assert image.og_resolution == (1280, 720)


def test_element_identity(mock_config):
    """Test element identity comparison."""
    image1 = PymordialImage(label="test", filepath="test.png", confidence=0.8)
    image2 = PymordialImage(label="test", filepath="test.png", confidence=0.8)

    # Different instances are not equal (uses identity, not value)
    assert image1 != image2
    assert image1 is not image2

    # Same instance is equal
    assert image1 == image1
    assert image1 is image1
