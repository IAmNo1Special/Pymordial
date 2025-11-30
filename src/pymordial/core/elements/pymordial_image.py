"""Implementation of PymordialImage element."""

from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image
from pyautogui import center, locate

from pymordial.core.pymordial_element import PymordialElement
from pymordial.utils.config import get_config

if TYPE_CHECKING:
    from pymordial.controller.pymordial_controller import PymordialController
    from pymordial.controller.image_controller import ImageController

_CONFIG = get_config()
DEFAULT_CONFIDENCE = _CONFIG["element"]["default_confidence"]
BLUESTACKS_RESOLUTION = _CONFIG["bluestacks"]["resolution"]


class PymordialImage(PymordialElement):
    """UI element identified by an image template.

    Attributes:
        path: Path to the image template file.
        confidence: Matching confidence threshold (0.0 to 1.0).
    """

    def __init__(
        self,
        label: str,
        asset_path: str | Path,
        bluestacks_resolution: tuple[int, int] = BLUESTACKS_RESOLUTION,
        position: tuple[int, int] | None = None,
        size: tuple[int, int] | None = None,
        confidence: float | None = None,
        element_text: str | None = None,
        is_static: bool = True,
    ):
        """Initializes a PymordialImage.

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
        super().__init__(label, bluestacks_resolution, position, size)
        self.asset_path = str(asset_path)
        self.confidence = float(confidence) if confidence else DEFAULT_CONFIDENCE
        self.element_text = element_text
        self.is_static = is_static

    def match(
        self,
        pymordial_controller: "PymordialController",
        image_controller: "ImageController",
        screenshot: bytes | None = None,
    ) -> tuple[int, int] | None:
        """Attempts to find the element on screen using template matching.

        Args:
            pymordial_controller: The Pymordial controller instance.
            image_controller: The Image controller instance.
            screenshot: Optional pre-captured screenshot bytes.

        Returns:
            Tuple of (x, y) coordinates if found, None otherwise.
        """
        screen_image = screenshot if screenshot else pymordial_controller.capture_screen()
        if not screen_image:
            return None

        haystack_img = Image.open(BytesIO(screen_image))

        # Scale the needle image to match current resolution
        scaled_img = image_controller.scale_img_to_screen(
            image_path=self.asset_path,
            screen_image=haystack_img,
            bluestacks_resolution=BLUESTACKS_RESOLUTION,
        )

        try:
            ui_location = locate(
                needleImage=scaled_img,
                haystackImage=haystack_img,
                confidence=self.confidence,
                grayscale=True,
                region=self.region,
            )

            if ui_location:
                return center(ui_location)
        except Exception:
            return None

        return None
