"""Tests for core abstract base classes and utilities."""

from unittest.mock import MagicMock

import pytest

from pymordial.core.app import PymordialApp
from pymordial.core.controller import PymordialController
from pymordial.core.screen import PymordialScreen
from pymordial.core.state_machine import AppState, StateMachine


class TestPymordialControllerABC:
    """Test PymordialController abstract base class."""

    def test_cannot_instantiate_directly(self):
        """ABC should not be instantiable."""
        with pytest.raises(TypeError, match="abstract"):
            PymordialController()

    def test_has_required_abstract_methods(self):
        """Verify expected abstract methods exist."""
        abstract_methods = PymordialController.__abstractmethods__
        expected = {
            "capture_screen",
            "click_coord",
            "click_element",
            "click_elements",
            "find_element",
            "is_element_visible",
            "open_app",
            "close_app",
            "read_text",
            "check_text",
        }
        assert expected.issubset(abstract_methods)


class TestPymordialAppABC:
    """Test PymordialApp abstract base class."""

    def test_cannot_instantiate_directly(self):
        """ABC should not be instantiable."""
        with pytest.raises(TypeError, match="abstract"):
            PymordialApp("TestApp")

    def test_has_required_abstract_methods(self):
        """Verify expected abstract methods exist."""
        abstract_methods = PymordialApp.__abstractmethods__
        assert "open" in abstract_methods
        assert "close" in abstract_methods


class TestPymordialAppImplementation:
    """Test a concrete implementation of PymordialApp (logic verification)."""

    def test_app_lifecycle_delegation(self, mock_controller, app):
        """Test full app lifecycle delegates to controller correctly."""
        # 1. Registration
        mock_controller.add_app(app)
        assert app.pymordial_controller is mock_controller
        assert "TestApp" in mock_controller.list_apps()

        # 2. Open App delegation
        mock_controller.open_app = MagicMock(return_value=True)
        assert app.open() is True

        mock_controller.open_app.assert_called_once()
        args, kwargs = mock_controller.open_app.call_args
        assert args[0] == "TestApp"
        assert kwargs["package_name"] == "com.test.app"
        assert app.app_state.current_state == AppState.LOADING

        # 3. Close App delegation
        # Manually transition to READY to allow closing (LOADING -> READY -> CLOSED)
        app.app_state.transition_to(AppState.READY)
        mock_controller.close_app = MagicMock(return_value=True)

        assert app.close() is True

        mock_controller.close_app.assert_called_once()
        assert mock_controller.close_app.call_args[1]["package_name"] == "com.test.app"
        assert app.app_state.current_state == AppState.CLOSED

    def test_app_requires_controller(self, app):
        """App methods raise ValueError if controller is missing."""
        with pytest.raises(ValueError, match="controller is not initialized"):
            app.open()

        with pytest.raises(ValueError, match="controller is not initialized"):
            app.close()


class TestStateMachine:
    """Test StateMachine state transitions."""

    def test_initial_state(self):
        """StateMachine starts in correct initial state."""
        sm = StateMachine(
            current_state=AppState.CLOSED,
            transitions=AppState.get_transitions(),
        )
        assert sm.current_state == AppState.CLOSED

    def test_valid_transition(self):
        """Valid transitions should succeed."""
        sm = StateMachine(
            current_state=AppState.CLOSED,
            transitions=AppState.get_transitions(),
        )
        sm.transition_to(AppState.LOADING)
        assert sm.current_state == AppState.LOADING

    def test_invalid_transition_raises(self):
        """Invalid transitions should raise."""
        sm = StateMachine(
            current_state=AppState.CLOSED,
            transitions=AppState.get_transitions(),
        )
        with pytest.raises(ValueError):
            sm.transition_to(AppState.READY)  # Can't go CLOSED -> READY


class TestPymordialScreen:
    """Test PymordialScreen functionality."""

    def test_screen_creation(self):
        """Screen can be created with a name."""
        screen = PymordialScreen(name="MainMenu")
        assert screen.name == "MainMenu"
        assert screen.elements == {}

    def test_add_element(self):
        """Elements can be added to screen."""
        from pymordial.ui.text import PymordialText

        screen = PymordialScreen(name="MainMenu")
        element = PymordialText(label="title", element_text="Play")
        screen.add_element(element)
        assert "title" in screen.elements
        assert screen.elements["title"] is element
        assert screen.elements["title"] is element
