"""Abstract base class for Pymordial UI elements."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pymordial.utils.config import get_config

if TYPE_CHECKING:
    from pymordial.controller.pymordial_controller import PymordialController
    from pymordial.controller.image_controller import ImageController

_CONFIG = get_config()


class PymordialElement(ABC):
    """Abstract base class for all UI elements.

    Attributes:
        label: A unique identifier for the element.
        bluestacks_resolution: The reference window size (width, height) used when
            defining the element.
        position: Optional (x, y) coordinates of the element.
        size: Optional (width, height) of the element.
    """

    def __init__(
        self,
        label: str,
        bluestacks_resolution: tuple[int, int],
        position: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
    ):
        """Initializes a PymordialElement.

        Args:
            label: A unique identifier for the element.
            bluestacks_resolution: The reference window size (width, height).
            position: Optional (x, y) coordinates.
            size: Optional (width, height).
        """
        self.label = label.lower()
        self.bluestacks_resolution = bluestacks_resolution
        self.position = position
        self.size = size

    @property
    def region(self) -> tuple[int, int, int, int] | None:
        """Returns (left, top, right, bottom) if position and size are set."""
        if self.position and self.size:
            return (
                self.position[0],
                self.position[1],
                self.position[0] + self.size[0],
                self.position[1] + self.size[1],
            )
        return None

    @property
    def center(self) -> tuple[int, int] | None:
        """Returns (x, y) center coordinates if position and size are set."""
        if self.position and self.size:
            return (
                self.position[0] + self.size[0] // 2,
                self.position[1] + self.size[1] // 2,
            )
        return self.position

    @abstractmethod
    def match(
        self,
        pymordial_controller: "PymordialController",
        image_controller: "ImageController",
        screenshot: bytes | None = None,
    ) -> tuple[int, int] | None:
        """Attempts to find the element on screen.

        Args:
            pymordial_controller: The Pymordial controller instance.
            image_controller: The Image controller instance.
            screenshot: Optional pre-captured screenshot bytes.

        Returns:
            Tuple of (x, y) coordinates if found, None otherwise.
        """
        pass
