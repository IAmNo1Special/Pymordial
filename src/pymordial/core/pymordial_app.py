"""Core application logic for Pymordial."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pymordial.state_machine import AppLifecycleState, StateMachine
from pymordial.utils.config import get_config

if TYPE_CHECKING:
    from pymordial.controller.pymordial_controller import PymordialController
    from pymordial.core.pymordial_element import PymordialElement
    from pymordial.core.pymordial_screen import PymordialScreen


_CONFIG = get_config()

# --- App Configuration ---
APP_ACTION_TIMEOUT = _CONFIG["app"]["action_timeout"]
APP_ACTION_WAIT_TIME = _CONFIG["app"]["action_wait_time"]
DEFAULT_READY_CHECK_MAX_TRIES = _CONFIG["app"]["ready_check_max_tries"]
APP_CLOSE_WAIT_TIME = _CONFIG["app"]["close_wait_time"]


class PymordialApp:
    """Represents an Android application with lifecycle management.

    The PymordialController reference is automatically set when this app
    is registered with a controller via PymordialController(apps=[...]) or
    controller.add_app(...).

    Attributes:
        app_name: The display name of the app.
        package_name: The Android package name (e.g., com.example.app).
        pymordial_controller: The controller managing this app.
        screens: A dictionary of screens belonging to this app.
        app_state: The state machine managing the app's lifecycle.
        ready_element: Optional element to detect when app is fully loaded.
            When this element becomes visible, app automatically transitions to READY.
    """

    def __init__(
        self,
        app_name: str,
        package_name: str,
        screens: dict[str, PymordialScreen] | None = None,
        ready_element: "PymordialElement | None" = None,
    ) -> None:
        """Initializes a PymordialApp.

        Args:
            app_name: The display name of the app.
            package_name: The Android package name.
            screens: Optional dictionary of screens.
            ready_element: Optional element that indicates app is ready.
                When this element becomes visible after opening the app,
                the state will automatically transition from LOADING to READY.
                Example: main menu button, game title text, etc.

        Raises:
            ValueError: If app_name or package_name are empty.
        """
        if not app_name:
            raise ValueError("app_name must be a non-empty string")
        if not package_name:
            raise ValueError("package_name must be a non-empty string")

        self.app_name: str = app_name
        self.package_name: str = package_name
        self.pymordial_controller: PymordialController | None = None
        self.screens: dict[str, PymordialScreen] = (
            screens if screens is not None else {}
        )
        self.ready_element: "PymordialElement | None" = ready_element

        self.app_state = StateMachine(
            current_state=AppLifecycleState.CLOSED,
            transitions=AppLifecycleState.get_transitions(),
        )

    def add_screen(self, screen: PymordialScreen) -> None:
        """Adds a screen to the app.

        Args:
            screen: The screen to add.
        """
        self.screens[screen.name] = screen

    def open(self) -> bool:
        """Opens the application on the emulator.

        After opening, the app state transitions to LOADING. If a ready_element
        is defined, the framework will automatically transition to READY when
        that element becomes visible. Otherwise, you must manually detect loading
        completion and transition to READY:

            # Without ready_element:
            app.open()
            # Wait and detect your app's loading indicator...
            if controller.is_element_visible(start_button):
                app.app_state.transition_to(AppLifecycleState.READY)

            # With ready_element (automatic):
            app = PymordialApp(
                "MyGame", "com.example.game",
                ready_element=PymordialText(label="title", element_text="Play")
            )
            app.open()  # Auto-transitions to READY when "Play" is visible

        Returns:
            True if the app was opened successfully, False otherwise.

        Raises:
            ValueError: If the controller is not initialized.
        """
        if not self.pymordial_controller:
            raise ValueError(
                f"{self.app_name}'s pymordial_controller is not initialized"
            )
        result = self.pymordial_controller.adb.open_app(
            self, timeout=APP_ACTION_TIMEOUT, wait_time=APP_ACTION_WAIT_TIME
        )
        if result:
            self.app_state.transition_to(AppLifecycleState.LOADING)
            # Auto-check if ready_element is visible
            if self.ready_element:
                self.check_ready()
        return result

    def check_ready(self, max_tries: int = DEFAULT_READY_CHECK_MAX_TRIES) -> bool:
        """Check if ready_element is visible and transition to READY if so.

        This is automatically called after open() if ready_element is defined.
        You can also manually poll this to check loading status.

        Args:
            max_tries: Maximum detection attempts (default: 3).

        Returns:
            True if transitioned to READY, False if still loading.

        Example:
            # Manual polling in a loop
            while app.is_loading():
                if app.check_ready():
                    print("App is ready!")
                    break
                time.sleep(0.5)
        """
        if not self.ready_element or not self.pymordial_controller:
            return False

        if self.app_state.current_state != AppLifecycleState.LOADING:
            return False  # Only transition from LOADING

        # Check if ready element is visible
        try:
            if self.pymordial_controller.is_element_visible(
                self.ready_element, max_tries=max_tries
            ):
                self.app_state.transition_to(AppLifecycleState.READY)
                return True
        except Exception:
            pass  # Element not visible yet

        return False

    def close(self) -> bool:
        """Closes the application on the emulator.

        Returns:
            True if the app was closed successfully, False otherwise.

        Raises:
            ValueError: If the controller is not initialized.
        """
        if not self.pymordial_controller:
            raise ValueError(
                f"{self.app_name}'s pymordial_controller is not initialized"
            )
        result = self.pymordial_controller.adb.close_app(
            self, timeout=APP_ACTION_TIMEOUT, wait_time=APP_CLOSE_WAIT_TIME
        )
        if result:
            self.app_state.transition_to(AppLifecycleState.CLOSED)
        return result

    def is_open(self) -> bool:
        """Checks if the app is in the READY state.

        Returns:
            True if the app is READY, False otherwise.
        """
        return self.app_state.current_state == AppLifecycleState.READY

    def is_loading(self) -> bool:
        """Checks if the app is in the LOADING state.

        Apps remain in LOADING until:
        1. A ready_element becomes visible (automatic transition), or
        2. You manually transition: app.app_state.transition_to(AppLifecycleState.READY)

        Returns:
            True if the app is LOADING, False otherwise.
        """
        return self.app_state.current_state == AppLifecycleState.LOADING

    def is_closed(self) -> bool:
        """Checks if the app is in the CLOSED state.

        Returns:
            True if the app is CLOSED, False otherwise.
        """
        return self.app_state.current_state == AppLifecycleState.CLOSED

    def __repr__(self) -> str:
        """Returns a string representation of the app."""
        return (
            f"PymordialApp("
            f"app_name='{self.app_name}', "
            f"package_name='{self.package_name}', "
            f"state={self.app_state.current_state.name})"
        )
