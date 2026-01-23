"""Main controller for the Pymordial automation framework."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable

from pymordial.core.app import PymordialApp
from pymordial.core.blueprints.extract_strategy import PymordialExtractStrategy
from pymordial.core.plugin import PymordialPlugin
from pymordial.ui.element import PymordialElement

logger = logging.getLogger(__name__)


class PymordialController(ABC):
    """Abstract base controller that orchestrates device interaction.

    The controller acts as the central coordinator for:
    - Managing registered applications (`PymordialApp`).
    - Delegating UI interactions (clicks, finds, text reading) to the device.
    - Handling plugin resolution.

    Attributes:
        apps: Dictionary of registered PymordialApp instances, keyed by sanitized name.
    """

    def __init__(
        self,
        apps: list[PymordialApp] | None = None,
    ):
        """Initializes the PymordialController.

        Args:
            apps: Optional list of PymordialApp instances to register immediately.
        """
        self._apps: dict[str, PymordialApp] = {}

        if apps:
            for app in apps:
                self.add_app(app)

    @abstractmethod
    def _resolve_plugin(
        self,
        name: str,
        default_factory: Callable[[], PymordialPlugin],
        configure_found_plugin: Callable[[PymordialPlugin], None] | None = None,
    ) -> PymordialPlugin:
        """Resolves a plugin from the registry or falls back to a default.

        Args:
            name: The name of the plugin to look up.
            default_factory: Factory function to create a default instance if not found.
            configure_found_plugin: Optional callback to configure the plugin if found.

        Returns:
            The resolved or default plugin instance.
        """
        pass

    def __getattr__(self, name: str) -> PymordialApp:
        """Enables dot-notation access to registered apps.

        Args:
            name: The name of the app to retrieve (sanitized).

        Returns:
            The registered PymordialApp instance.

        Raises:
            AttributeError: If the app name is not registered.
        """
        if name in self._apps:
            return self._apps[name]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'. "
            f"Available apps: {list(self._apps.keys())}"
        )

    # --- Convenience Methods (delegate to sub-controllers) ---
    ## --- App Management ---
    def add_app(self, app: PymordialApp) -> None:
        """Registers a PymordialApp instance with this controller.

        This method adds the app to the internal registry using a sanitized name.
        If an app with the same sanitized name already exists, it will be overwritten.

        Args:
            app: The PymordialApp instance to register.
        """
        # Sanitize app_name for attribute access
        sanitized_name = app.app_name.replace("-", "_").replace(" ", "_")

        # Store in registry
        self._apps[sanitized_name] = app

    def list_apps(self) -> list[str]:
        """Returns a list of registered app names.

        Returns:
            A list of strings representing the names of registered apps.
        """
        return list(self._apps.keys())

    @property
    def apps(self) -> dict[str, PymordialApp]:
        """Returns the dictionary of registered apps.

        Returns:
            A dictionary mapping sanitized app names to PymordialApp instances.
        """
        return self._apps

    @abstractmethod
    def capture_screen(self) -> bytes | None:
        """Captures the current screen.

        Returns:
            The raw image bytes of the screenshot, or None if capture failed.
        """
        pass

    # --- Click Methods ---
    @abstractmethod
    def click_coord(self, coords: tuple[int, int], times: int = 1) -> bool:
        """Clicks specific coordinates on the screen.

        Args:
            coords: A tuple of (x, y) integer coordinates.
            times: The number of times to click. Defaults to 1.

        Returns:
            True if the click action was successful, False otherwise.
        """
        pass

    @abstractmethod
    def click_element(
        self,
        pymordial_element: "PymordialElement",
        times: int = 1,
        screenshot_img_bytes: bytes | None = None,
        max_tries: int = 1,
    ) -> bool:
        """Clicks a UI element on the screen.

        Args:
            pymordial_element: The element blueprint to find and click.
            times: The number of times to click. Defaults to 1.
            screenshot_img_bytes: Optional pre-captured screenshot to optimize finding.
            max_tries: Maximum number of attempts to find the element. Defaults to 1.

        Returns:
            True if the element was found and clicked, False otherwise.
        """
        pass

    @abstractmethod
    def click_elements(
        self,
        pymordial_elements: list["PymordialElement"],
        screenshot_img_bytes: bytes | None = None,
        max_tries: int = 1,
    ) -> bool:
        """Clicks any of the elements in the list.

        Iterates through the list and clicks the first element found.

        Args:
            pymordial_elements: List of element blueprints to search for.
            screenshot_img_bytes: Optional pre-captured screenshot.
            max_tries: Maximum attempts to find any element.

        Returns:
            True if any element from the list was clicked, False otherwise.
        """
        pass

    @abstractmethod
    def find_element(
        self,
        pymordial_element: "PymordialElement",
        pymordial_screenshot: bytes | None = None,
        max_tries: int = 1,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of a UI element on the screen.

        Args:
            pymordial_element: The element blueprint to search for.
            pymordial_screenshot: Optional pre-captured screenshot.
            max_tries: Maximum number of search attempts. Defaults to 1.

        Returns:
            A tuple of (x, y) coordinates if found, None otherwise.
        """
        pass

    @abstractmethod
    def is_element_visible(
        self,
        pymordial_element: "PymordialElement",
        pymordial_screenshot: bytes | None = None,
        max_tries: int | None = None,
    ) -> bool:
        """Checks if a UI element is visible on the screen.

        Args:
            pymordial_element: The element blueprint to check.
            pymordial_screenshot: Optional pre-captured screenshot.
            max_tries: Maximum number of checks. If None, defaults to 1.

        Returns:
            True if the element is visible, False otherwise.
        """
        pass

    # --- App Lifecycle Methods ---
    @abstractmethod
    def open_app(
        self,
        app_name: str,
        package_name: str,
        timeout: int,
        wait_time: int,
    ) -> bool:
        """Opens an app on the device.

        Args:
            app_name: The display name of the app.
            package_name: The platform-specific package identifier (e.g. bundle ID).
            timeout: Maximum seconds to wait for launch.
            wait_time: Seconds to wait after launch command.

        Returns:
            True if the app launched successfully, False otherwise.
        """
        pass

    @abstractmethod
    def close_app(
        self,
        package_name: str,
        timeout: int,
        wait_time: int,
    ) -> bool:
        """Closes an app on the device.

        Args:
            package_name: The platform-specific package identifier.
            timeout: Maximum seconds to wait for closure.
            wait_time: Seconds to wait after close command.

        Returns:
            True if the app closed successfully, False otherwise.
        """
        pass

    @abstractmethod
    def read_text(
        self,
        image_path: "Path | bytes | str",
        case_sensitive: bool = False,
        strategy: "PymordialExtractStrategy | None" = None,
    ) -> list[str]:
        """Read text from an image using OCR.

        Args:
            image_path: Path to image file, raw bytes, or base64 string.
            case_sensitive: Whether OCR should respect case. Defaults to False.
            strategy: Optional extraction strategy to preprocess image.

        Returns:
            A list of strings containing the read text lines.
        """
        pass

    @abstractmethod
    def check_text(
        self,
        text_to_find: str,
        image_path: "Path | bytes | str",
        case_sensitive: bool = False,
        strategy: "PymordialExtractStrategy | None" = None,
    ) -> bool:
        """Check if specific text exists in an image.

        Args:
            text_to_find: The string to search for.
            image_path: Path to image file, raw bytes, or base64 string.
            case_sensitive: Whether to perform case-sensitive matching.
            strategy: Optional extraction strategy.

        Returns:
            True if the text is found, False otherwise.
        """
        pass

    def __repr__(self) -> str:
        """Returns a string representation of the PymordialController."""
        return f"PymordialController(apps={len(self._apps)})"
