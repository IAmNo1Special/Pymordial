"""Main controller for the Pymordial automation framework."""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from pathlib import Path

    from pymordial.core.app import PymordialApp
    from pymordial.core.blueprints.element import PymordialElement
    from pymordial.core.blueprints.extract_strategy import PymordialExtractStrategy
    from pymordial.core.plugin import PymordialPlugin

logger = logging.getLogger(__name__)


class PymordialController(ABC):
    """Abstract base controller that orchestrates device interaction.

    Attribute:
        apps: Dictionary of registered PymordialApp instances.
    """

    def __init__(
        self,
        apps: list["PymordialApp"] | None = None,
    ):
        """Initializes the PymordialController.

        Args:
            apps: Optional list of PymordialApp instances to register.
        """
        self._apps: dict[str, "PymordialApp"] = {}

        if apps:
            for app in apps:
                self.add_app(app)

    @abstractmethod
    def _resolve_plugin(
        self,
        name: str,
        default_factory: Callable[[], "PymordialPlugin"],
        configure_found_plugin: Callable[["PymordialPlugin"], None] | None = None,
    ) -> "PymordialPlugin":
        """Resolves a plugin from the registry or falls back to a default."""
        pass

    def __getattr__(self, name: str) -> "PymordialApp":
        """Enables dot-notation access to registered apps."""
        if name in self._apps:
            return self._apps[name]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'. "
            f"Available apps: {list(self._apps.keys())}"
        )

    # --- Convenience Methods (delegate to sub-controllers) ---
    ## --- App Management ---
    def add_app(self, app: "PymordialApp") -> None:
        """Registers a PymordialApp instance with this controller."""
        # Set controller reference if not set
        if (
            app.pymordial_controller is not None
            and app.pymordial_controller is not self
        ):
            raise ValueError(
                f"App '{app.app_name}' is already registered with a different controller."
            )
        app.pymordial_controller = self

        # Sanitize app_name for attribute access
        sanitized_name = app.app_name.replace("-", "_").replace(" ", "_")

        # Store in registry
        self._apps[sanitized_name] = app

    def list_apps(self) -> list[str]:
        """Returns a list of registered app names."""
        return list(self._apps.keys())

    @property
    def apps(self) -> dict[str, "PymordialApp"]:
        """Returns the dictionary of registered apps."""
        return self._apps

    @abstractmethod
    def capture_screen(self) -> bytes | None:
        """Captures the current screen."""
        pass

    # --- Click Methods ---
    @abstractmethod
    def click_coord(self, coords: tuple[int, int], times: int = 1) -> bool:
        """Clicks specific coordinates on the screen."""
        pass

    @abstractmethod
    def click_element(
        self,
        pymordial_element: "PymordialElement",
        times: int = 1,
        screenshot_img_bytes: bytes | None = None,
        max_tries: int = 1,
    ) -> bool:
        """Clicks a UI element on the screen."""
        pass

    @abstractmethod
    def click_elements(
        self,
        pymordial_elements: list["PymordialElement"],
        screenshot_img_bytes: bytes | None = None,
        max_tries: int = 1,
    ) -> bool:
        """Clicks any of the elements in the list."""
        pass

    @abstractmethod
    def find_element(
        self,
        pymordial_element: "PymordialElement",
        pymordial_screenshot: bytes | None = None,
        max_tries: int = 1,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of a UI element on the screen."""
        pass

    @abstractmethod
    def is_element_visible(
        self,
        pymordial_element: "PymordialElement",
        pymordial_screenshot: bytes | None = None,
        max_tries: int | None = None,
    ) -> bool:
        """Checks if a UI element is visible on the screen."""
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
        """Opens an app on the device."""
        pass

    @abstractmethod
    def close_app(
        self,
        package_name: str,
        timeout: int,
        wait_time: int,
    ) -> bool:
        """Closes an app on the device."""
        pass

    @abstractmethod
    def read_text(
        self,
        image_path: "Path | bytes | str",
        case_sensitive: bool = False,
        strategy: "PymordialExtractStrategy | None" = None,
    ) -> list[str]:
        """Read text from an image using OCR."""
        pass

    @abstractmethod
    def check_text(
        self,
        text_to_find: str,
        image_path: "Path | bytes | str",
        case_sensitive: bool = False,
        strategy: "PymordialExtractStrategy | None" = None,
    ) -> bool:
        """Check if specific text exists in an image."""
        pass

    def __repr__(self) -> str:
        """Returns a string representation of the PymordialController."""
        return f"PymordialController(apps={len(self._apps)})"
