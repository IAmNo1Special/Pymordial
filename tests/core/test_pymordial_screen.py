"""Tests for PymordialScreen."""

from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.pymordial_screen import PymordialScreen


def test_pymordial_screen_init(mock_config):
    """Test screen initialization."""
    screen = PymordialScreen(name="MainScreen")

    assert screen.name == "MainScreen"
    assert screen.elements == {}


def test_pymordial_screen_init_with_elements(mock_config):
    """Test screen initialization with elements."""
    button = PymordialImage(
        label="start", filepath="start.png", og_resolution=(1280, 720), confidence=0.8
    )
    elements = {"start": button}

    screen = PymordialScreen(name="MainScreen", elements=elements)

    assert "start" in screen.elements
    assert screen.elements["start"] == button


def test_add_element(mock_config):
    """Test adding an element to screen."""
    screen = PymordialScreen(name="MainScreen")
    button = PymordialImage(
        label="PlayButton",
        filepath="play.png",
        og_resolution=(1280, 720),
        confidence=0.8,
    )

    screen.add_element(button)

    assert "playbutton" in screen.elements  # Labels are lowercase
    assert screen.elements["playbutton"] == button
    assert screen.elements["playbutton"] == button
