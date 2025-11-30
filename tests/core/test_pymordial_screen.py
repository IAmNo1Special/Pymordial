"""Tests for PymordialScreen."""

from pymordial.core.elements.pymordial_button import PymordialButton
from pymordial.core.pymordial_screen import PymordialScreen


def test_pymordial_screen_init(mock_config):
    """Test screen initialization."""
    screen = PymordialScreen(name="MainScreen")

    assert screen.name == "MainScreen"
    assert screen.elements == {}


def test_pymordial_screen_init_with_elements(mock_config):
    """Test screen initialization with elements."""
    button = PymordialButton(
        label="start", asset_path="start.png", bluestacks_resolution=(1280, 720)
    )
    elements = {"start": button}

    screen = PymordialScreen(name="MainScreen", elements=elements)

    assert "start" in screen.elements
    assert screen.elements["start"] == button


def test_add_element(mock_config):
    """Test adding an element to screen."""
    screen = PymordialScreen(name="MainScreen")
    button = PymordialButton(
        label="PlayButton", asset_path="play.png", bluestacks_resolution=(1280, 720)
    )

    screen.add_element(button)

    assert "playbutton" in screen.elements  # Labels are lowercase
    assert screen.elements["playbutton"] == button
    assert screen.elements["playbutton"] == button
