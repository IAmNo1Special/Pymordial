"""Tests for core abstract base classes and utilities."""

from unittest.mock import MagicMock

import pytest

from pymordial.core.app import PymordialApp
from pymordial.core.controller import PymordialController
from pymordial.core.screen import PymordialScreen
from pymordial.core.state_machine import AppState, StateMachine
from pymordial.ui.element import PymordialElement


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


class TestPymordialApp:
    """Test PymordialApp functionality."""

    def test_instantiation(self):
        """PymordialApp should be instantiable as a dataclass."""
        app = PymordialApp(app_name="TestApp")
        assert app.app_name == "TestApp"
        assert app.screens == {}
        assert app.app_id is not None
        assert app.app_state.current_state == AppState.CLOSED

    def test_validation_empty_name(self):
        """app_name cannot be empty."""
        with pytest.raises(ValueError, match="app_name must be a non-empty string"):
            PymordialApp(app_name="")

    def test_validation_invalid_type(self):
        """app_name must be a string."""
        with pytest.raises(TypeError, match="app_name must be a string"):
            PymordialApp(app_name=123)  # type: ignore

    def test_open_close_on_library_app(self, mock_controller):
        """The library app itself can open and close, no subclass needed."""
        app = PymordialApp(app_name="TestApp", package_name="com.test.app")

        mock_controller.open_app = MagicMock(return_value=True)
        assert app.open(mock_controller) is True
        args, kwargs = mock_controller.open_app.call_args
        assert args[0] == "TestApp"
        assert kwargs["package_name"] == "com.test.app"
        assert app.app_state.current_state == AppState.LOADING

        # Repeat open while LOADING must not raise on LOADING -> LOADING.
        assert app.open(mock_controller) is True
        assert app.app_state.current_state == AppState.LOADING

        mock_controller.close_app = MagicMock(return_value=True)
        assert app.close(mock_controller) is True
        assert mock_controller.close_app.call_args[1]["package_name"] == "com.test.app"
        assert app.app_state.current_state == AppState.CLOSED

        # Repeat close while CLOSED must not raise on CLOSED -> CLOSED.
        assert app.close(mock_controller) is True
        assert app.app_state.current_state == AppState.CLOSED

    def test_open_requires_package_name(self, mock_controller):
        """Opening without a package_name fails loudly, not silently."""
        app = PymordialApp(app_name="TestApp")
        with pytest.raises(ValueError, match="package_name must be set"):
            app.open(mock_controller)
        with pytest.raises(ValueError, match="package_name must be set"):
            app.close(mock_controller)

    def test_failed_open_leaves_state_closed(self, mock_controller):
        """A failed launch must not move the app out of CLOSED."""
        app = PymordialApp(app_name="TestApp", package_name="com.test.app")
        mock_controller.open_app = MagicMock(return_value=False)
        assert app.open(mock_controller) is False
        assert app.app_state.current_state == AppState.CLOSED

    def test_open_with_ready_element_reaches_ready(self, mock_controller):
        """open() waits for the ready element and marks the app READY."""
        ready = PymordialElement(label="Main Menu")
        app = PymordialApp(
            app_name="TestApp", package_name="com.test.app", ready_element=ready
        )
        mock_controller.is_element_visible = MagicMock(return_value=True)
        assert app.open(mock_controller) is True
        assert app.app_state.current_state == AppState.READY
        mock_controller.is_element_visible.assert_called_once_with(ready, max_tries=1)

    def test_open_ready_timeout_stays_loading_and_retries(self, mock_controller):
        """A missing ready element leaves the app LOADING; the wait retries."""
        ready = PymordialElement(label="Main Menu")
        app = PymordialApp(
            app_name="TestApp", package_name="com.test.app", ready_element=ready
        )
        mock_controller.is_element_visible = MagicMock(return_value=False)
        assert app.open(mock_controller, timeout=0) is False
        assert app.app_state.current_state == AppState.LOADING

        # The element shows up later: retry the wait without relaunching.
        mock_controller.is_element_visible = MagicMock(return_value=True)
        assert app.wait_until_ready(mock_controller) is True
        assert app.app_state.current_state == AppState.READY

    def test_open_without_ready_element_never_polls(self, mock_controller):
        """Apps with no ready element behave exactly as before."""
        app = PymordialApp(app_name="TestApp", package_name="com.test.app")
        mock_controller.is_element_visible = MagicMock(return_value=True)
        assert app.open(mock_controller) is True
        assert app.app_state.current_state == AppState.LOADING
        mock_controller.is_element_visible.assert_not_called()

    def test_wait_until_ready_without_ready_element(self, mock_controller):
        """Waiting with no ready element to check returns False."""
        app = PymordialApp(app_name="TestApp", package_name="com.test.app")
        app.app_state.transition_to(AppState.LOADING)
        assert app.wait_until_ready(mock_controller) is False
        assert app.app_state.current_state == AppState.LOADING

    def test_wait_until_ready_already_ready(self, mock_controller):
        """Waiting on an already READY app returns True without polling."""
        ready = PymordialElement(label="Main Menu")
        app = PymordialApp(
            app_name="TestApp", package_name="com.test.app", ready_element=ready
        )
        app.app_state.transition_to(AppState.LOADING)
        app.app_state.transition_to(AppState.READY)
        mock_controller.is_element_visible = MagicMock(return_value=True)
        assert app.wait_until_ready(mock_controller) is True
        mock_controller.is_element_visible.assert_not_called()

    def test_wait_until_ready_from_closed(self, mock_controller):
        """A CLOSED app cannot skip to READY; the wait returns False."""
        ready = PymordialElement(label="Main Menu")
        app = PymordialApp(
            app_name="TestApp", package_name="com.test.app", ready_element=ready
        )
        assert app.wait_until_ready(mock_controller) is False
        assert app.app_state.current_state == AppState.CLOSED

    def test_failed_open_never_waits(self, mock_controller):
        """A failed launch must not wait for the ready element."""
        ready = PymordialElement(label="Main Menu")
        app = PymordialApp(
            app_name="TestApp", package_name="com.test.app", ready_element=ready
        )
        mock_controller.open_app = MagicMock(return_value=False)
        mock_controller.is_element_visible = MagicMock(return_value=True)
        assert app.open(mock_controller) is False
        assert app.app_state.current_state == AppState.CLOSED
        mock_controller.is_element_visible.assert_not_called()


class TestPymordialAppImplementation:
    """Test a concrete implementation of PymordialApp (logic verification)."""

    def test_app_lifecycle_delegation(self, mock_controller, app):
        """Test full app lifecycle delegates to controller correctly."""
        # 1. Registration
        mock_controller.add_app(app)
        assert "TestApp" in mock_controller.list_apps()

        # 2. Open App delegation
        mock_controller.open_app = MagicMock(return_value=True)
        assert app.open(mock_controller) is True

        mock_controller.open_app.assert_called_once()
        args, kwargs = mock_controller.open_app.call_args
        assert args[0] == "TestApp"
        assert kwargs["package_name"] == "com.test.app"
        assert app.app_state.current_state == AppState.LOADING

        # 3. Close App delegation
        # Manually transition to READY to allow closing (LOADING -> READY -> CLOSED)
        app.app_state.transition_to(AppState.READY)
        mock_controller.close_app = MagicMock(return_value=True)

        assert app.close(mock_controller) is True

        mock_controller.close_app.assert_called_once()
        assert mock_controller.close_app.call_args[1]["package_name"] == "com.test.app"
        assert app.app_state.current_state == AppState.CLOSED


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
            sm.transition_to(
                AppState.CLOSED
            )  # Can't self-transition explicitly unless in list

    def test_register_handlers_in_separate_calls_keeps_both(self):
        """Registering on_exit after on_enter must not drop on_enter."""
        calls = []
        sm = StateMachine(
            current_state=AppState.CLOSED,
            transitions=AppState.get_transitions(),
        )
        sm.register_handler(AppState.LOADING, on_enter=lambda: calls.append("enter"))
        sm.register_handler(AppState.LOADING, on_exit=lambda: calls.append("exit"))

        sm.transition_to(AppState.LOADING)
        sm.transition_to(AppState.READY)

        assert calls == ["enter", "exit"]

    def test_reregistering_one_handler_keeps_the_other(self):
        """Replacing on_enter must leave the existing on_exit in place."""
        calls = []
        sm = StateMachine(
            current_state=AppState.CLOSED,
            transitions=AppState.get_transitions(),
        )
        sm.register_handler(AppState.LOADING, on_enter=lambda: calls.append("old"))
        sm.register_handler(AppState.LOADING, on_exit=lambda: calls.append("exit"))
        sm.register_handler(AppState.LOADING, on_enter=lambda: calls.append("new"))

        sm.transition_to(AppState.LOADING)
        sm.transition_to(AppState.READY)

        assert calls == ["new", "exit"]

    def test_closed_to_ready_is_invalid(self):
        """CLOSED must go through LOADING; it cannot skip straight to READY."""
        sm = StateMachine(
            current_state=AppState.CLOSED,
            transitions=AppState.get_transitions(),
        )
        with pytest.raises(ValueError):
            sm.transition_to(AppState.READY)

    def test_closed_only_exits_to_loading(self):
        """LOADING is the only allowed exit from CLOSED."""
        assert AppState.get_transitions()[AppState.CLOSED] == [AppState.LOADING]

    def test_full_lifecycle_closed_loading_ready_closed(self):
        """The full lifecycle still works: CLOSED -> LOADING -> READY -> CLOSED."""
        sm = StateMachine(
            current_state=AppState.CLOSED,
            transitions=AppState.get_transitions(),
        )
        sm.transition_to(AppState.LOADING)
        sm.transition_to(AppState.READY)
        sm.transition_to(AppState.CLOSED)
        assert sm.current_state == AppState.CLOSED


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
