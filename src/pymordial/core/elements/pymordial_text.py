"""Implementation of PymordialText element."""

from typing import TYPE_CHECKING

from pymordial.core.pymordial_element import PymordialElement
from pymordial.core.extract_strategy import PymordialExtractStrategy

if TYPE_CHECKING:
    from pymordial.controller.bluestacks_controller import BluestacksController
    from pymordial.controller.image_controller import ImageController


class PymordialText(PymordialElement):
    """UI element identified by text content (via OCR).

    Attributes:
        text: The text string to search for.
        extract_strategy: Optional OCR preprocessing strategy.
    """

    def __init__(
        self,
        label: str,
        text: str,
        bluestacks_resolution: tuple[int, int],
        position: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
        extract_strategy: PymordialExtractStrategy | None = None,
    ):
        """Initializes a PymordialText.

        Args:
            label: A unique identifier for the element.
            text: The text string to search for.
            bluestacks_resolution: The reference window size (width, height).
            position: Optional (x, y) coordinates.
            size: Optional (width, height).
            extract_strategy: Optional OCR preprocessing strategy.
        """
        super().__init__(label, bluestacks_resolution, position, size)
        self.text = text
        self.extract_strategy = extract_strategy

    def match(
        self,
        bs_controller: "BluestacksController",
        image_controller: "ImageController",
        screenshot: bytes | None = None,
    ) -> tuple[int, int] | None:
        """Attempts to find the element by checking for text presence.

        Args:
            bs_controller: The BlueStacks controller instance.
            image_controller: The Image controller instance.
            screenshot: Optional pre-captured screenshot bytes.

        Returns:
            The center coordinates if found, None otherwise.
        """
        screen_image = screenshot if screenshot else bs_controller.capture_screen(self)
        if not screen_image:
            return None

        # Use ImageController's text checking capabilities
        # Note: This is a basic check. For finding coordinates of text,
        # we might need more advanced OCR features in the future.
        # For now, if text is found, we return the center of the defined region
        # or the center of the screen if no region is defined.

        is_found = image_controller.check_text(
            text_to_find=self.text,
            image_path=screen_image,
            strategy=self.extract_strategy,
        )

        if is_found:
            return self.center if self.center else (0, 0)  # Fallback if no position

        return None
