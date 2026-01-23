"""Abstract base class for Pymordial application lifecycle management."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pymordial.core.state_machine import AppState, StateMachine

if TYPE_CHECKING:
    from pymordial.core.blueprints.element import PymordialElement
    from pymordial.core.controller import PymordialController
    from pymordial.core.screen import PymordialScreen


class PymordialApp(ABC):
    """Abstract base class for application lifecycle management.

    Concrete implementations should handle platform-specific app launching,
    such as Android package management or iOS app bundles.

    Attributes:
        app_name: The display name of the app.
        pymordial_controller: The controller managing this app.
        screens: A dictionary of screens belonging to this app.
        app_state: The state machine managing the app's lifecycle.
        ready_element: Optional element to detect when app is fully loaded.
    """

    def __init__(
        self,
        app_name: str,
        screens: dict[str, "PymordialScreen"] | None = None,
        ready_element: "PymordialElement | None" = None,
    ) -> None:
        """Initializes a PymordialApp.

        Args:
            app_name: The display name of the app.
            screens: Optional dictionary of screens.
            ready_element: Optional element that indicates app is ready.

        Raises:
            ValueError: If app_name is empty.
        """
        if not app_name:
            raise ValueError("app_name must be a non-empty string")

        self.app_name: str = app_name
        self.pymordial_controller: "PymordialController | None" = None
        self.screens: dict[str, "PymordialScreen"] = (
            screens if screens is not None else {}
        )
        self.ready_element: "PymordialElement | None" = ready_element

        self.app_state = StateMachine(
            current_state=AppState.CLOSED,
            transitions=AppState.get_transitions(),
        )

    def add_screen(self, screen: "PymordialScreen") -> None:
        """Adds a screen to the app.

        Args:
            screen: The PymordialScreen instance to add.
        """
        self.screens[screen.name] = screen

    @abstractmethod
    def open(self) -> bool:
        """Opens the application.

        Returns:
            True if the app was opened successfully, False otherwise.
        """
        pass

    @abstractmethod
    def close(self) -> bool:
        """Closes the application.

        Returns:
            True if the app was closed successfully, False otherwise.
        """
        pass

    def is_open(self) -> bool:
        """Checks if the app is in the READY state.

        Returns:
            True if the app state is READY, False otherwise.
        """
        return self.app_state.current_state == AppState.READY

    def is_loading(self) -> bool:
        """Checks if the app is in the LOADING state.

        Returns:
            True if the app state is LOADING, False otherwise.
        """
        return self.app_state.current_state == AppState.LOADING

    def is_closed(self) -> bool:
        """Checks if the app is in the CLOSED state.

        Returns:
            True if the app state is CLOSED, False otherwise.
        """
        return self.app_state.current_state == AppState.CLOSED

    def __repr__(self) -> str:
        """Returns a string representation of the app."""
        return (
            f"{self.__class__.__name__}("
            f"app_name='{self.app_name}', "
            f"state={self.app_state.current_state.name})"
        )
