"""Tests for PymordialText element."""

import pytest

from pymordial.core.elements.pymordial_text import PymordialText
from pymordial.ocr.extract_strategy import DefaultExtractStrategy


def test_pymordial_text_init(mock_config):
    """Test text element initialization."""
    text_elem = PymordialText(
        label="username",
        element_text="Player123",
    )

    assert text_elem.label == "username"
    assert text_elem.element_text == "player123"  # Lowercase
    assert text_elem.og_resolution == (1920, 1080)  # Default from config
    assert text_elem.extract_strategy is None
    assert text_elem.filepath is None


def test_pymordial_text_with_strategy(mock_config):
    """Test text element with extract strategy."""
    strategy = DefaultExtractStrategy()
    text_elem = PymordialText(
        label="title",
        element_text="Welcome",
        extract_strategy=strategy,
    )
    assert text_elem.extract_strategy == strategy


def test_pymordial_text_with_position_and_size(mock_config):
    """Test text element with position and size."""
    text_elem = PymordialText(
        label="score",
        element_text="1000",
        position=(100, 50),
        size=(200, 30),
    )

    assert text_elem.position == (100, 50)
    assert text_elem.size == (200, 30)
    assert text_elem.center == (200, 65)


def test_pymordial_text_with_filepath(mock_config):
    """Test text element with filepath for image saving."""
    from pathlib import Path

    text_elem = PymordialText(
        label="label",
        element_text="Score",
        filepath="output/score.png",
    )
    assert text_elem.filepath == Path("output/score.png").resolve()


def test_pymordial_text_with_og_resolution(mock_config):
    """Test text element with custom og_resolution."""
    text_elem = PymordialText(
        label="title",
        element_text="Hello",
        og_resolution=(1280, 720),
    )
    assert text_elem.og_resolution == (1280, 720)


def test_pymordial_text_element_text_validation(mock_config):
    """Test element_text type validation."""
    with pytest.raises(TypeError, match="string"):
        PymordialText(
            label="test",
            element_text=123,  # Should be string
        )


def test_pymordial_text_strategy_validation(mock_config):
    """Test extract_strategy type validation."""
    with pytest.raises(TypeError, match="PymordialExtractStrategy"):
        PymordialText(
            label="test",
            element_text="hello",
            extract_strategy="invalid",  # Should be strategy object
        )


def test_pymordial_text_repr(mock_config):
    """Test string representation."""
    text_elem = PymordialText(
        label="score",
        element_text="1000",
        position=(100, 50),
        size=(200, 30),
    )
    repr_str = repr(text_elem)
    assert "PymordialText" in repr_str
    assert "score" in repr_str
    assert "1000" in repr_str


def test_pymordial_text_center_without_position(mock_config):
    """Test center returns None when position not set."""
    text_elem = PymordialText(
        label="title",
        element_text="Hello",
    )
    assert text_elem.center is None


def test_pymordial_text_region(mock_config):
    """Test region property."""
    text_elem = PymordialText(
        label="title",
        element_text="Hello",
        position=(100, 200),
        size=(50, 30),
    )
    assert text_elem.region == (100, 200, 150, 230)
