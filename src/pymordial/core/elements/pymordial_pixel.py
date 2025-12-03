"""Implementation of PymordialPixel element."""

from dataclasses import dataclass, field

from pymordial.core.pymordial_element import PymordialElement
from pymordial.utils.config import get_config

_CONFIG = get_config()


@dataclass(kw_only=True)
class PymordialPixel(PymordialElement):
    """UI element identified by a specific pixel color at a coordinate.

    Attributes:
        pixel_color: The expected RGB color tuple (r, g, b).
        tolerance: Color matching tolerance (0-255).

    Note:
        The size attribute is automatically set to the pixel_size from config
        and should not be specified by users.
    """

    pixel_color: tuple[int, int, int]
    tolerance: int = 0
    # Override parent's size to always be PIXEL_SIZE from config
    size: tuple[int | float, int | float] = field(
        default_factory=lambda: tuple(_CONFIG["element"]["pixel_size"])
    )

    def __post_init__(self):
        """Post-initialization processing and validation."""
        super().__post_init__()

        # Validate pixel_color
        if not isinstance(self.pixel_color, tuple):
            raise TypeError(
                f"Pixel color must be a tuple, not {type(self.pixel_color).__name__}"
            )

        if len(self.pixel_color) != 3:
            raise ValueError(
                f"Pixel color must have 3 values (r, g, b), got {len(self.pixel_color)}"
            )

        if not all(isinstance(c, int) for c in self.pixel_color):
            raise TypeError("All pixel color values must be integers")

        if not all(0 <= c <= 255 for c in self.pixel_color):
            raise ValueError(
                f"All pixel color values must be between 0 and 255, got {self.pixel_color}"
            )

        # Validate tolerance
        if not isinstance(self.tolerance, int):
            raise TypeError(
                f"Tolerance must be an integer, not {type(self.tolerance).__name__}"
            )

        if not (0 <= self.tolerance <= 255):
            raise ValueError(
                f"Tolerance must be between 0 and 255, got {self.tolerance}"
            )
