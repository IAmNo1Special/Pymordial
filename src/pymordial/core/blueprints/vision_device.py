import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class PymordialVisionDevice(ABC):
    """Abstract base class for vision-based device interaction.

    Defines the contract for visual operations such as screen scaling,
    pixel color checking, and text extraction/finding.
    """

    @abstractmethod
    @abstractmethod
    def scale_img_to_screen(self) -> Any:
        """Scales the reference image to match the current screen resolution.

        Returns:
            A PIL Image object resized to the device screen dimensions.
        """
        pass

    @abstractmethod
    def check_pixel_color(self) -> bool | None:
        """Verifies if a specific pixel matches a target color.

        Returns:
            True if color matches within tolerance, False if not, None if error.
        """
        pass

    @abstractmethod
    def where_element(self) -> tuple[int, int] | None:
        """Finds the coordinates of a visual element.

        Returns:
            A tuple of (x, y) coordinates if found, None otherwise.
        """
        pass

    @abstractmethod
    def where_elements(self) -> tuple[int, int] | None:
        """Finds the coordinates of one of multiple visual elements.

        Returns:
            A tuple of (x, y) coordinates if any element is found, None otherwise.
        """
        pass

    @abstractmethod
    def find_text(self) -> tuple[int, int] | None:
        """Finds the coordinates of specific text on the screen.

        Returns:
            A tuple of (x, y) coordinates if text is found, None otherwise.
        """
        pass

    @abstractmethod
    def check_text(self) -> bool:
        """Checks if specific text is visible on the screen.

        Returns:
            True if text is found, False otherwise.
        """
        pass

    @abstractmethod
    def read_text(self) -> list[str]:
        """Reads all text from the current screen.

        Returns:
            A list of strings representing the text lines found on screen.
        """
        pass
