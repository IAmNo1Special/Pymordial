"""Controller for image processing and element detection."""

import logging
from io import BytesIO
from time import sleep
from typing import TYPE_CHECKING

import numpy as np
from adb_shell.exceptions import TcpTimeoutException
from PIL import Image
from pyautogui import ImageNotFoundException, center, locate

from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.elements.pymordial_pixel import PymordialPixel
from pymordial.core.pymordial_element import PymordialElement
from pymordial.utils.config import get_config

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
        text_controller: Helper for checking text in images.
    """

    def __init__(self, PymordialController: "PymordialController"):
        """Initializes the ImageController."""
        self.pymordial_controller = PymordialController

    def scale_img_to_screen(
        self,
        image_path: str,
        screen_image: "str | Image.Image | bytes | np.ndarray",
        bluestacks_resolution: tuple[int, int],
    ) -> Image.Image:
        """Scales an image to match the current screen resolution.

        Args:
            image_path: Path to the image to scale.
            screen_image: The current screen image (path, bytes, numpy array, or PIL Image).
            bluestacks_resolution: The original window size the image was designed for.

        Returns:
            The scaled PIL Image.
        """
        # If screen_image is bytes, convert to PIL Image
        if isinstance(screen_image, bytes):
            screen_image = Image.open(BytesIO(screen_image))
        # If screen_image is numpy array, convert to PIL Image
        elif isinstance(screen_image, np.ndarray):
            screen_image = Image.fromarray(screen_image)
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
        pymordial_pixel: PymordialPixel,
        screenshot_img_bytes: "bytes | np.ndarray | None" = None,
    ) -> bool | None:
        """Checks if the pixel at (x, y) matches the target color within a tolerance.

        Args:
            pymordial_pixel: The PymordialPixel to check.
            screenshot_img_bytes: The screenshot image bytes or numpy array.

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
            if pymordial_pixel.position is None:
                logger.warning(
                    f"PymordialPixel {pymordial_pixel.label} has no position defined. Cannot find."
                )
                return None

            # Ensure coordinates are integers
            target_coords = (
                int(pymordial_pixel.position[0]),
                int(pymordial_pixel.position[1]),
            )
            if len(target_coords) != 2:
                raise ValueError(
                    f"Coords for {pymordial_pixel.label} must be a tuple of two values, not {target_coords}"
                )
            if len(pymordial_pixel.pixel_color) != 3:
                raise ValueError(
                    f"Pixel color for {pymordial_pixel.label} must be a tuple of three values, not {pymordial_pixel.pixel_color}"
                )
            if pymordial_pixel.tolerance < 0:
                raise ValueError(
                    f"Tolerance for {pymordial_pixel.label} must be a non-negative integer, not {pymordial_pixel.tolerance}"
                )

            if screenshot_img_bytes is None:
                raise ValueError(
                    f"Failed to capture screenshot for {pymordial_pixel.label}"
                )

            if isinstance(screenshot_img_bytes, bytes):
                with Image.open(BytesIO(screenshot_img_bytes)) as image:
                    pixel_color = image.getpixel(target_coords)
                    return check_color_with_tolerance(
                        pixel_color,
                        pymordial_pixel.pixel_color,
                        pymordial_pixel.tolerance,
                    )
            elif isinstance(screenshot_img_bytes, np.ndarray):
                image = Image.fromarray(screenshot_img_bytes)
                pixel_color = image.getpixel(target_coords)
                return check_color_with_tolerance(
                    pixel_color,
                    pymordial_pixel.pixel_color,
                    pymordial_pixel.tolerance,
                )
            else:
                raise ValueError(
                    f"Image must be a bytes or numpy array, not {type(screenshot_img_bytes)}"
                )

        except ValueError as e:
            logger.error(f"ValueError in check_pixel_color: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}") from e

    def where_element(
        self,
        pymordial_element: PymordialElement,
        screenshot_img_bytes: "bytes | np.ndarray | None" = None,
        max_tries: int = DEFAULT_FIND_UI_RETRIES,
        set_position: bool = False,
        set_size: bool = False,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of a PymordialElement on the screen.

        Args:
            pymordial_element: The PymordialElement to find.
            screenshot_img_bytes: Optional pre-captured screenshot (bytes or numpy array).
            max_tries: Maximum number of retries. If None, will retry indefinitely.
                This is useful for waiting out loading screens with unknown/dynamic duration.
            set_position: If True, updates the element's position with found coordinates.
            set_size: If True, updates the element's size with found dimensions.

        Returns:
            (x, y) coordinates if found, None otherwise.

        Note:
            When max_tries=None, this method will loop indefinitely until the element
            is found. This is intentional for scenarios where load times are unknown
            or dynamic (e.g., waiting for loading screens to complete).
        """
        logger.debug(
            f"Looking for PymordialElement(Max retries: {max_tries}): {pymordial_element.label}..."
        )

        find_ui_retries: int = 0
        current_img = screenshot_img_bytes

        while (find_ui_retries < max_tries) if max_tries is not None else True:
            # Capture screen if we don't have an image to check
            if current_img is None:
                # Ensures PymordialController's ADB is connected
                if not self.pymordial_controller.adb.is_connected():
                    self.pymordial_controller.adb.connect()
                    if not self.pymordial_controller.adb.is_connected():
                        raise ValueError("PymordialController's ADB is not connected")

                try:
                    current_img = self.pymordial_controller.capture_screen()
                    if current_img is None:
                        logger.warning("Failed to capture screen.")
                except TcpTimeoutException:
                    raise TcpTimeoutException(
                        f"TCP timeout while finding element {pymordial_element.label}"
                    )
                except Exception as e:
                    logger.error(f"Error capturing screen: {e}")

            if current_img is not None:
                if isinstance(pymordial_element, PymordialImage):
                    ui_location = None
                    try:
                        if isinstance(current_img, bytes):
                            haystack_img = Image.open(BytesIO(current_img))
                        elif isinstance(current_img, np.ndarray):
                            haystack_img = Image.fromarray(current_img)
                        else:
                            # Should not happen if capture_screen returns correct types
                            # But if user passes something else...
                            logger.warning(
                                f"Unsupported image type: {type(current_img)}. Attempting to open as file path if string."
                            )
                            if isinstance(current_img, str):
                                haystack_img = Image.open(current_img)
                            else:
                                raise ValueError(
                                    f"Unsupported image type: {type(current_img)}"
                                )

                        # Scale the needle image to match current resolution
                        scaled_img = self.scale_img_to_screen(
                            image_path=pymordial_element.filepath,
                            screen_image=haystack_img,
                            bluestacks_resolution=pymordial_element.og_resolution,
                        )

                        ui_location = locate(
                            needleImage=scaled_img,
                            haystackImage=haystack_img,
                            confidence=pymordial_element.confidence,
                            grayscale=True,
                            region=pymordial_element.region,
                        )
                    except ImageNotFoundException:
                        logger.debug(
                            f"Failed to find PymordialImage element: {pymordial_element.label}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error finding element {pymordial_element.label}: {e}"
                        )

                    if ui_location:
                        coords = center(ui_location)
                        logger.debug(
                            f"PymordialImage {pymordial_element.label} found at: {coords}"
                        )

                        if set_position:
                            # ui_location is (left, top, width, height)
                            pymordial_element.position = (
                                ui_location[0],
                                ui_location[1],
                            )
                            logger.debug(
                                f"Updated position for {pymordial_element.label} to {pymordial_element.position}"
                            )

                        if set_size:
                            # ui_location is (left, top, width, height)
                            pymordial_element.size = (ui_location[2], ui_location[3])
                            logger.debug(
                                f"Updated size for {pymordial_element.label} to {pymordial_element.size}"
                            )

                        return coords
                else:
                    raise NotImplementedError(
                        f"Element type: {type(pymordial_element)} is not supported."
                    )

            # Prepare for next retry
            find_ui_retries += 1
            current_img = None  # Force capture on next iteration

            if max_tries is not None and find_ui_retries >= max_tries:
                break

            logger.debug(
                f"PymordialImage {pymordial_element.label} not found. Retrying... ({find_ui_retries}/{max_tries})"
            )
            sleep(DEFAULT_WAIT_TIME)

        logger.info(
            f"Wasn't able to find PymordialImage within {max_tries} retries: {pymordial_element.label}"
        )
        return None

    def where_elements(
        self,
        pymordial_elements: list[PymordialElement],
        screenshot_img_bytes: "bytes | np.ndarray | None" = None,
        max_tries: int = DEFAULT_FIND_UI_RETRIES,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of the first found element from a list.

        Args:
            pymordial_elements: List of elements to search for.
            screenshot_img_bytes: Optional pre-captured screenshot (bytes or numpy array).
            max_tries: Maximum number of retries per element.

        Returns:
            (x, y) coordinates of the first found element, or None if none found.
        """
        for pymordial_element in pymordial_elements:
            coord: tuple[int, int] | None = self.where_element(
                pymordial_element=pymordial_element,
                screenshot_img_bytes=screenshot_img_bytes,
                max_tries=max_tries,
            )
            if coord is not None:
                return coord
        return None

    def __repr__(self) -> str:
        """Returns a string representation of the ImageController."""
        return f"ImageController(pymordial_controller={id(self.pymordial_controller)})"
