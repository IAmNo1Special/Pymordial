import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from pymordial.core.screen import PymordialScreen

if TYPE_CHECKING:
    from pymordial.core.controller import PymordialController
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
        package_name: The platform-specific package identifier (e.g. bundle ID)
            used when opening or closing the app. Required by open() and close().
        app_state: The state machine managing the app's lifecycle (auto-generated).
        app_id: Unique identifier for this app instance (auto-generated).
    """

    app_name: str
    screens: dict[str, PymordialScreen] = field(default_factory=dict)
    ready_element: PymordialElement | None = None
    package_name: str | None = None
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

        if not isinstance(self.package_name, str | None):
            raise TypeError("package_name must be a string or None")

        if not isinstance(self.app_state, StateMachine):
            raise TypeError("app_state must be a StateMachine")

    def _require_package_name(self) -> str:
        """Returns package_name, or raises if it was never set."""
        if self.package_name is None:
            raise ValueError(
                "package_name must be set before opening or closing "
                f"the '{self.app_name}' app."
            )
        return self.package_name

    def open(
        self,
        controller: "PymordialController",
        timeout: int = 60,
        wait_time: int = 10,
    ) -> bool:
        """Opens the app using the provided controller.

        On success the app state transitions to LOADING (a repeat open
        while already LOADING leaves the state untouched instead of
        raising on an invalid LOADING -> LOADING transition).

        When a ready_element is set, opening also waits for it to become
        visible and transitions to READY. The wait is bounded by the same
        timeout. If the element never appears, the app stays LOADING and
        this method returns False, so a script never treats a
        not-yet-ready app as ready; call wait_until_ready() again later
        to retry without relaunching.

        Args:
            controller: The controller that launches the app on the device.
            timeout: Maximum seconds to wait for launch and for the ready
                element to appear.
            wait_time: Seconds to wait after the launch command.

        Returns:
            True if the app launched and is ready to use (READY, or
            LOADING when no ready element is set). False if the launch
            failed or the ready element never appeared in time.

        Raises:
            ValueError: If package_name was never set.
        """
        result = controller.open_app(
            self.app_name,
            package_name=self._require_package_name(),
            timeout=timeout,
            wait_time=wait_time,
        )
        if result and self.app_state.current_state != AppState.LOADING:
            self.app_state.transition_to(AppState.LOADING)
        if result and self.ready_element is not None:
            return self.wait_until_ready(controller, timeout=timeout)
        return result

    def wait_until_ready(
        self,
        controller: "PymordialController",
        timeout: int = 60,
        interval: float = 0.5,
    ) -> bool:
        """Waits for the app's ready element to appear, then marks it READY.

        Polls controller.is_element_visible(self.ready_element) until the
        element is seen or the timeout expires. This is the step the app
        lifecycle documents between LOADING and READY; without it an app
        can never leave LOADING, even when its ready element is on screen.

        Args:
            controller: The controller that checks element visibility.
            timeout: Maximum seconds to wait for the ready element.
            interval: Seconds to sleep between visibility checks.

        Returns:
            True if the ready element was seen and the app is now READY,
            or if the app was already READY. False if no ready element
            is set, the app is not LOADING, or the timeout expired.
            On timeout the state stays LOADING, so the wait can be
            retried without relaunching.
        """
        if self.ready_element is None:
            return False
        if self.app_state.current_state == AppState.READY:
            return True
        if self.app_state.current_state != AppState.LOADING:
            return False

        deadline = time.monotonic() + timeout
        while True:
            if controller.is_element_visible(self.ready_element, max_tries=1):
                self.app_state.transition_to(AppState.READY)
                return True
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            time.sleep(min(interval, remaining))

    def close(
        self,
        controller: "PymordialController",
        timeout: int = 60,
        wait_time: int = 1,
    ) -> bool:
        """Closes the app using the provided controller.

        On success the app state transitions to CLOSED (a repeat close
        while already CLOSED leaves the state untouched instead of
        raising on an invalid CLOSED -> CLOSED transition).

        Args:
            controller: The controller that closes the app on the device.
            timeout: Maximum seconds to wait for closure.
            wait_time: Seconds to wait after the close command.

        Returns:
            True if the app closed successfully, False otherwise.

        Raises:
            ValueError: If package_name was never set.
        """
        result = controller.close_app(
            package_name=self._require_package_name(),
            timeout=timeout,
            wait_time=wait_time,
        )
        if result and self.app_state.current_state != AppState.CLOSED:
            self.app_state.transition_to(AppState.CLOSED)
        return result

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
