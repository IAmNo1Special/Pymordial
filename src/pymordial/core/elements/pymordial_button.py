"""Implementation of PymordialButton element."""

from pathlib import Path

from pymordial.core.elements.pymordial_image import PymordialImage


class PymordialButton(PymordialImage):
    """UI element representing a clickable button.

    Currently behaves identical to PymordialImage but semantically distinct.
    """

    def __init__(
        self,
        label: str,
        asset_path: str | Path,
        bluestacks_resolution: tuple[int, int],
        position: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
        confidence: float | None = None,
        element_text: str | None = None,
        is_static: bool = True,
    ):
        """Initializes a PymordialButton.

        Args:
            label: A unique identifier for the element.
            asset_path: Path to the image template file.
            bluestacks_resolution: The reference window size (width, height).
            position: Optional (x, y) coordinates.
            size: Optional (width, height).
            confidence: Optional matching confidence threshold.
            element_text: Optional text associated with the element.
            is_static: Whether the element is static on screen.
        """
        super().__init__(
            label,
            asset_path,
            bluestacks_resolution,
            position,
            size,
            confidence,
            element_text,
            is_static,
        )
