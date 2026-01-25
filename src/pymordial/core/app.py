from dataclasses import dataclass, field
from uuid import uuid4

from pymordial.core.screen import PymordialScreen
from pymordial.core.state_machine import AppState, StateMachine
from pymordial.ui.element import PymordialElement
from pymordial.utils.exceptions import ScreenNotFoundError


@dataclass(eq=False)
class PymordialApp:
    """Represents an application.

    Attributes:
        app_name: The display name of the app.
        screens: A dictionary of screens belonging to this app.
        ready_element: Optional element to detect when app is fully loaded.
        app_state: The state machine managing the app's lifecycle (auto-generated).
        app_id: Unique identifier for this app instance (auto-generated).
    """

    app_name: str
    screens: dict[str, PymordialScreen] = field(default_factory=dict)
    ready_element: PymordialElement | None = None
    app_state: StateMachine = field(
        default_factory=lambda: StateMachine(
            current_state=AppState.CLOSED,
            transitions=AppState.get_transitions(),
        ),
        init=False,
    )
    app_id: str = field(default_factory=lambda: str(uuid4()), init=False)

    def __post_init__(self) -> None:
        """Initializes a PymordialApp.

        Raises:
            TypeError: If app_name is not a string.
            ValueError: If app_name is empty.
            TypeError: If screens is not a dictionary.
            TypeError: If ready_element is not a PymordialElement or None.
            TypeError: If app_state is not a StateMachine.
        """
        if not isinstance(self.app_name, str):
            raise TypeError("app_name must be a string")
        if not self.app_name:
            raise ValueError("app_name must be a non-empty string")

        if not isinstance(self.screens, dict):
            raise TypeError("screens must be a dictionary")

        if not isinstance(self.ready_element, PymordialElement | None):
            raise TypeError("ready_element must be a PymordialElement or None")

        if not isinstance(self.app_state, StateMachine):
            raise TypeError("app_state must be a StateMachine")

    def add_screen(self, screen: PymordialScreen) -> None:
        """Adds a screen to the app.

        Args:
            screen: The PymordialScreen instance to add.
        """
        self.screens[screen.name] = screen

    def get_screen(self, name: str) -> PymordialScreen:
        """Retrieves a screen by its name.

        Args:
            name: The name of the screen to retrieve.

        Returns:
            The PymordialScreen instance.

        Raises:
            ScreenNotFoundError: If the screen is not found.
        """
        try:
            return self.screens[name]
        except KeyError as e:
            raise ScreenNotFoundError(
                f"Screen '{name}' not found within the '{self.app_name}' app."
            ) from e

    def remove_screen(self, name: str) -> PymordialScreen:
        """Removes a screen by its name.

        Args:
            name: The name of the screen to remove.

        Returns:
            The removed PymordialScreen instance.

        Raises:
            ScreenNotFoundError: If the screen is not found.
        """
        try:
            return self.screens.pop(name)
        except KeyError as e:
            raise ScreenNotFoundError(
                f"Screen '{name}' not found within the '{self.app_name}' app."
            ) from e

    def __hash__(self) -> int:
        """Returns hash based on unique app_id."""
        return hash(self.app_id)

    def __eq__(self, other) -> bool:
        """Compares apps by their unique app_id."""
        if not isinstance(other, PymordialApp):
            return NotImplemented
        return self.app_id == other.app_id
