"""Tests for PymordialApp."""

from unittest.mock import Mock, patch

import pytest

from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.elements.pymordial_text import PymordialText
from pymordial.core.pymordial_app import PymordialApp
from pymordial.state_machine import AppLifecycleState


def test_pymordial_app_init_success(mock_config):
    """Test successful app initialization."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")
    assert app.app_name == "TestApp"
    assert app.package_name == "com.test.app"
    assert app.pymordial_controller is None
    assert app.screens == {}
    assert app.app_state.current_state == AppLifecycleState.CLOSED
    assert app.ready_element is None


def test_pymordial_app_init_with_screens(mock_config):
    """Test app initialization with screens."""
    from pymordial.core.pymordial_screen import PymordialScreen

    screens = {"main": PymordialScreen(name="main")}
    app = PymordialApp(app_name="TestApp", package_name="com.test.app", screens=screens)
    assert "main" in app.screens
    assert app.screens["main"].name == "main"


def test_pymordial_app_init_with_ready_element(mock_config):
    """Test app initialization with ready_element."""
    ready_elem = PymordialText(label="ready", element_text="Welcome")
    app = PymordialApp(
        app_name="TestApp",
        package_name="com.test.app",
        ready_element=ready_elem,
    )
    assert app.ready_element == ready_elem


def test_pymordial_app_init_invalid_app_name(mock_config):
    """Test app initialization with empty app name."""
    with pytest.raises(ValueError, match="app_name must be a non-empty string"):
        PymordialApp(app_name="", package_name="com.test.app")


def test_pymordial_app_init_invalid_package_name(mock_config):
    """Test app initialization with empty package name."""
    with pytest.raises(ValueError, match="package_name must be a non-empty string"):
        PymordialApp(app_name="TestApp", package_name="")


def test_add_screen(mock_config):
    """Test adding a screen to the app."""
    from pymordial.core.pymordial_screen import PymordialScreen

    app = PymordialApp(app_name="TestApp", package_name="com.test.app")
    screen = PymordialScreen(name="LoginScreen")
    app.add_screen(screen)
    assert "LoginScreen" in app.screens
    assert app.screens["LoginScreen"] == screen


def test_open_without_controller(mock_config):
    """Test opening app without controller raises ValueError."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")
    with pytest.raises(ValueError, match="pymordial_controller is not initialized"):
        app.open()


def test_open_with_controller(mock_config, mock_adb_controller):
    """Test opening app with controller."""
    from pymordial.controller.pymordial_controller import PymordialController

    app = PymordialApp(app_name="TestApp", package_name="com.test.app")

    controller = Mock(spec=PymordialController)
    controller.adb = mock_adb_controller
    app.pymordial_controller = controller

    with patch.object(controller.adb, "open_app") as mock_open:
        app.open()
        mock_open.assert_called()

    assert app.app_state.current_state == AppLifecycleState.LOADING


def test_close_without_controller(mock_config):
    """Test closing app without controller raises ValueError."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")
    with pytest.raises(ValueError, match="pymordial_controller is not initialized"):
        app.close()


def test_close_with_controller(mock_config, mock_adb_controller):
    """Test closing app with controller."""
    from pymordial.controller.pymordial_controller import PymordialController

    app = PymordialApp(app_name="TestApp", package_name="com.test.app")

    controller = Mock(spec=PymordialController)
    controller.adb = mock_adb_controller
    app.pymordial_controller = controller

    app.app_state.transition_to(AppLifecycleState.LOADING, ignore_validation=True)

    with patch.object(controller.adb, "close_app") as mock_close:
        app.close()
        mock_close.assert_called()

    assert app.app_state.current_state == AppLifecycleState.CLOSED


def test_is_open(mock_config):
    """Test is_open returns correct status."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")
    assert not app.is_open()
    app.app_state.transition_to(AppLifecycleState.LOADING)
    assert not app.is_open()
    app.app_state.transition_to(AppLifecycleState.READY)
    assert app.is_open()


def test_is_loading(mock_config):
    """Test is_loading returns correct status."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")
    assert not app.is_loading()
    app.app_state.transition_to(AppLifecycleState.LOADING)
    assert app.is_loading()


def test_is_closed(mock_config):
    """Test is_closed returns correct status."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")
    assert app.is_closed()
    app.app_state.transition_to(AppLifecycleState.LOADING)
    assert not app.is_closed()


def test_app_repr(mock_config):
    """Test string representation."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")
    repr_str = repr(app)
    assert "PymordialApp" in repr_str
    assert "TestApp" in repr_str
    assert "com.test.app" in repr_str
