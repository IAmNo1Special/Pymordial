"""Controller for image processing and element detection."""

import logging
from io import BytesIO
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from adb_shell.exceptions import TcpTimeoutException
from PIL import Image
from pyautogui import ImageNotFoundException, center, locate

from pymordial.core.extract_strategy import PymordialExtractStrategy
from pymordial.core import PymordialElement
from pymordial.core import PymordialImage
from pymordial.utils.config import get_config
from pymordial.utils.image_text_checker import ImageTextChecker

if TYPE_CHECKING:
    from pymordial.controller.pymordial_controller import PymordialController
logger = logging.getLogger(__name__)

_CONFIG = get_config()

# --- Image Controller Configuration ---
DEFAULT_FIND_UI_RETRIES = _CONFIG["image_controller"]["default_find_ui_retries"]
DEFAULT_WAIT_TIME = _CONFIG["bluestacks"]["default_wait_time"]


class ImageController:
    """Handles image processing, text extraction, and element detection.

    Attributes:
        img_txt_checker: Helper for checking text in images.
    """

    def __init__(self, PymordialController: "PymordialController"):
        """Initializes the ImageController."""
        self.pymordial_controller = PymordialController
        self.img_txt_checker: ImageTextChecker = ImageTextChecker()

    def check_text(
        self,
        text_to_find: str,
        image_path: Path | bytes | str,
        strategy: PymordialExtractStrategy | None = None,
    ) -> bool:
        """Checks if specific text is present in an image.

        Convenience method that delegates to the internal ImageTextChecker.

        Args:
            text_to_find: Text to search for in the image.
            image_path: Path to image file, image bytes, or string path.
            strategy: Optional preprocessing strategy (only for TesseractOCR).

        Returns:
            True if the text is found, False otherwise.

        Raises:
            ValueError: If the image cannot be read.
        """
        return self.img_txt_checker.check_text(text_to_find, image_path, strategy)

    def read_text(
        self,
        image_path: Path | bytes | str,
        strategy: PymordialExtractStrategy | None = None,
    ) -> list[str]:
        """Reads text from an image.

        Convenience method that delegates to the internal ImageTextChecker.

        Args:
            image_path: Path to image file, image bytes, or string path.
            strategy: Optional preprocessing strategy (only for TesseractOCR).

        Returns:
            List of detected text lines.

        Raises:
            ValueError: If the image cannot be read.
        """
        return self.img_txt_checker.read_text(image_path, strategy)

    def scale_img_to_screen(
        self,
        image_path: str,
        screen_image: str | Image.Image | bytes,
        bluestacks_resolution: tuple[int, int],
    ) -> Image.Image:
        """Scales an image to match the current screen resolution.

        Args:
            image_path: Path to the image to scale.
            screen_image: The current screen image (path, bytes, or PIL Image).
            bluestacks_resolution: The original window size the image was designed for.

        Returns:
            The scaled PIL Image.
        """
        # If screen_image is bytes, convert to PIL Image
        if isinstance(screen_image, bytes):
            screen_image = Image.open(BytesIO(screen_image))

        # If screen_image is a string (file path), open it
        elif isinstance(screen_image, str):
            screen_image = Image.open(screen_image)

        # At this point, screen_image should be a PIL Image
        game_screen_width, game_screen_height = screen_image.size

        needle_img: Image.Image = Image.open(image_path)

        needle_img_size: tuple[int, int] = needle_img.size

        original_window_size: tuple[int, int] = bluestacks_resolution

        ratio_width: float = game_screen_width / original_window_size[0]
        ratio_height: float = game_screen_height / original_window_size[1]

        scaled_image_size: tuple[int, int] = (
            int(needle_img_size[0] * ratio_width),
            int(needle_img_size[1] * ratio_height),
        )
        scaled_image: Image.Image = needle_img.resize(scaled_image_size)
        return scaled_image

    def check_pixel_color(
        self,
        target_coords: tuple[int, int],
        target_color: tuple[int, int, int],
        image: bytes | str,
        tolerance: int = 0,
    ) -> bool:
        """Checks if the pixel at (x, y) matches the target color within a tolerance.

        Args:
            target_coords: (x, y) coordinates of the pixel.
            target_color: (R, G, B) target color.
            image: Image bytes or file path.
            tolerance: Color matching tolerance (0-255).

        Returns:
            True if the pixel matches, False otherwise.

        Raises:
            ValueError: If arguments are invalid or image processing fails.
        """

        def check_color_with_tolerance(
            color1: tuple[int, int, int], color2: tuple[int, int, int], tolerance: int
        ) -> bool:
            """Check if two colors are within a certain tolerance."""
            return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

        try:
            if len(target_coords) != 2:
                raise ValueError("Coords must be a tuple of two values")
            if len(target_color) != 3:
                raise ValueError("Target color must be a tuple of three values")
            if tolerance < 0:
                raise ValueError("Tolerance must be a non-negative integer")

            if not image:
                raise ValueError("Failed to capture screenshot")

            if isinstance(image, bytes):
                with Image.open(BytesIO(image)) as image:
                    pixel_color = image.getpixel(target_coords)
                    return check_color_with_tolerance(
                        pixel_color, target_color, tolerance
                    )
            elif isinstance(image, str):
                with Image.open(image) as image:
                    pixel_color = image.getpixel(target_coords)
                    return check_color_with_tolerance(
                        pixel_color, target_color, tolerance
                    )
            else:
                raise ValueError("Image must be a bytes or str")

        except ValueError as e:
            logger.error(f"ValueError in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}")
        except Exception as e:
            logger.error(f"Error in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}")

    def where_image(
        self,
        pymordial_image: PymordialImage,
        screenshot_img_bytes: bytes | None = None,
        max_retries: int = DEFAULT_FIND_UI_RETRIES,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of a PymordialImage element on the screen.

        Args:
            pymordial_image: The PymordialImage element to find.
            screenshot_img_bytes: Optional pre-captured screenshot.
            max_retries: Maximum number of retries.

        Returns:
            (x, y) coordinates if found, None otherwise.
        """
        # Ensures PymordialController's ADB is connected before trying to find the PymordialImage element
        if not isinstance(pymordial_image, PymordialImage):
            raise TypeError(
                f"pymordial_image must be a PymordialImage instance, not {type(pymordial_image)}"
            )
            return None
        if screenshot_img_bytes is None:
            match self.pymordial_controller.adb.is_connected():
                case False:
                    raise ValueError("PymordialController's ADB is not connected")
            try:
                # TODO: Will use capture_screenshot method to capture screenshot
                pass
            except TcpTimeoutException:
                raise TcpTimeoutException(
                    f"TCP timeout while finding element {pymordial_image.label}"
                )

        logger.debug(f"Finding UI element. Max retries: {max_retries}")
        logger.debug(f"Looking for PymordialImage: {pymordial_image.label}...")
        find_ui_retries: int = 0
        while (
            (find_ui_retries < max_retries)
            if max_retries is not None and max_retries > 0
            else True
        ):
            try:
                haystack_img = Image.open(BytesIO(screenshot_img_bytes))

                # Scale the needle image to match current resolution
                scaled_img = self.scale_img_to_screen(
                    image_path=pymordial_image.asset_path,
                    screen_image=haystack_img,
                    bluestacks_resolution=pymordial_image.resolution,
                )

                try:
                    ui_location = locate(
                        needleImage=scaled_img,
                        haystackImage=haystack_img,
                        confidence=pymordial_image.confidence,
                        grayscale=True,
                        region=self.region,
                    )
                except ImageNotFoundException:
                    logger.debug(
                        f"Failed to find PymordialImage element: {pymordial_image.label}"
                    )
                    return None

                coords = center(ui_location)
                if coords:
                    logger.debug(
                        f"PymordialImage {pymordial_image.label} found at: {coords}"
                    )
                    return coords

            except Exception as e:
                logger.error(f"Error finding element {pymordial_image.label}: {e}")

            find_ui_retries += 1
            logger.debug(
                f"PymordialImage {pymordial_image.label} not found. Retrying... ({find_ui_retries}/{max_retries})"
            )

            sleep(DEFAULT_WAIT_TIME)
            continue

        logger.info(f"Wasn't able to find PymordialImage within {max_retries} retries: {pymordial_image.label}")
        return None

    def where_elements(
        self,
        ui_elements: list[PymordialElement],
        pymordial_controller: "PymordialController | None" = None,
        screenshot_img_bytes: bytes | None = None,
        max_tries: int = DEFAULT_FIND_UI_RETRIES,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of the first found element from a list.

        Args:
            ui_elements: List of elements to search for.
            pymordial_controller: The PymordialController instance (optional).
            screenshot_img_bytes: Optional pre-captured screenshot.
            max_tries: Maximum number of retries per element.

        Returns:
            (x, y) coordinates of the first found element, or None if none found.
        """
        coord: tuple[int, int] | None = None
        for ui_element in ui_elements:
            coord = self.where_element(
                pymordial_element=ui_element,
                pymordial_controller=pymordial_controller,
                screenshot_img_bytes=screenshot_img_bytes,
                max_retries=max_tries,
            )
            if coord:
                return coord
        return None
