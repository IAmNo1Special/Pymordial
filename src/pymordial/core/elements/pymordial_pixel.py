"""Implementation of PymordialPixel element."""

from typing import TYPE_CHECKING

from pymordial.core.pymordial_element import PymordialElement
from pymordial.utils.config import get_config

if TYPE_CHECKING:
    from pymordial.controller.bluestacks_controller import BluestacksController
    from pymordial.controller.image_controller import ImageController

_CONFIG = get_config()
PIXEL_SIZE = tuple(_CONFIG["element"]["pixel_size"])


class PymordialPixel(PymordialElement):
    """UI element identified by a specific pixel color at a coordinate.

    Attributes:
        pixel_color: The expected RGB color tuple (r, g, b).
        tolerance: Color matching tolerance (0-255).
    """

    def __init__(
        self,
        label: str,
        position: tuple[int, int],
        pixel_color: tuple[int, int, int],
        bluestacks_resolution: tuple[int, int],
        tolerance: int = 0,
    ):
        """Initializes a PymordialPixel.

        Args:
            label: A unique identifier for the element.
            position: The (x, y) coordinates of the pixel.
            pixel_color: The expected RGB color (r, g, b).
            bluestacks_resolution: The reference window size (width, height).
            tolerance: Color matching tolerance.
        """
        # Pixels have a fixed small size defined in config
        super().__init__(label, bluestacks_resolution, position, size=PIXEL_SIZE)
        self.pixel_color = pixel_color
        self.tolerance = tolerance

    def match(
        self,
        bs_controller: "BluestacksController",
        image_controller: "ImageController",
        screenshot: bytes | None = None,
    ) -> tuple[int, int] | None:
        """Attempts to find the element by checking pixel color.

        Args:
            bs_controller: The BlueStacks controller instance.
            image_controller: The Image controller instance.
            screenshot: Optional pre-captured screenshot bytes.

        Returns:
            The position (x, y) if the color matches, None otherwise.
        """
        screen_image = screenshot if screenshot else bs_controller.capture_screen(self)
        if not screen_image:
            return None

        # Check if the pixel at self.position matches self.pixel_color
        is_match = image_controller.check_pixel_color(
            target_coords=self.position,
            target_color=self.pixel_color,
            image=screen_image,
            tolerance=self.tolerance,
        )

        return self.position if is_match else None
