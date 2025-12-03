"""Core application logic for Pymordial."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pymordial.state_machine import AppLifecycleState, StateMachine
from pymordial.utils.config import get_config

if TYPE_CHECKING:
    from pymordial.controller.pymordial_controller import PymordialController
    from pymordial.core.pymordial_screen import PymordialScreen


_CONFIG = get_config()

# --- App Configuration ---
APP_ACTION_TIMEOUT = _CONFIG["app"]["action_timeout"]
APP_ACTION_WAIT_TIME = _CONFIG["app"]["action_wait_time"]


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
    """

    def __init__(
        self,
        app_name: str,
        package_name: str,
        screens: dict[str, PymordialScreen] | None = None,
    ) -> None:
        """Initializes a PymordialApp.

        Args:
            app_name: The display name of the app.
            package_name: The Android package name.
            screens: Optional dictionary of screens.

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
        return result

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
            self, timeout=APP_ACTION_TIMEOUT, wait_time=1
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

    
