"""Controller for image processing and element detection."""

import copy
from io import BytesIO
from logging import DEBUG, basicConfig, getLogger
from pathlib import Path
from time import sleep

import cv2
import numpy as np
from adb_shell.exceptions import TcpTimeoutException
from PIL import Image

from pymordial.core.blueprints.bridge_device import PymordialBridgeDevice
from pymordial.core.blueprints.element import PymordialElement
from pymordial.core.blueprints.ocr_device import PymordialOCRDevice
from pymordial.core.blueprints.vision_device import PymordialVisionDevice
from pymordial.devices.adb_device import PymordialAdbDevice
from pymordial.devices.extract_strategies import PymordialExtractStrategy
from pymordial.devices.tesseract_device import PymordialTesseractDevice
from pymordial.ui.image import PymordialImage
from pymordial.ui.pixel import PymordialPixel
from pymordial.utils.config import VisionConfig, get_config


class PymordialUiDevice(PymordialVisionDevice):
    """Handles all visual recognition tasks.

    This class consolidates image recognition (template matching), pixel color detection,
    and Optical Character Recognition (OCR) into a single interface. It routes
    element finding requests to the appropriate backend based on the element type
    (PymordialImage, PymordialPixel, or PymordialText).

    Attributes:
        bridge_device: Helper for underlying device operations (e.g., ADB).
        config: Configuration dictionary for vision settings (timeouts, retries).
        ocr_engine: The backend engine used for text extraction (e.g., Tesseract).
    """

    name: str = "ui"
    version: str = "0.1.0"

    def __init__(
        self,
        bridge_device: PymordialBridgeDevice | None = None,
        config: VisionConfig | None = None,
    ):
        """Initializes the PymordialUiDevice.

        Args:
            bridge_device: Optional PymordialBridgeDevice for device interactions.
                If None, a new PymordialAdbDevice will be created.
            config: Optional configuration dictionary. If None, loads defaults
                from the global configuration.
        """
        self.logger = getLogger("PymordialUiDevice")
        basicConfig(
            level=DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self._bridge_device: PymordialBridgeDevice = (
            bridge_device or PymordialAdbDevice()
        )
        self._ocr_device: PymordialOCRDevice = PymordialTesseractDevice()
        self.config: VisionConfig = copy.deepcopy(
            config or get_config()["image_controller"]
        )

    def initialize(self, config: dict) -> None:
        """Initializes the UI device plugin with configuration.

        Args:
            config: Configuration dictionary containing OCR settings,
                timeouts, and other UI device parameters.
        """
        # TODO: Use config to set OCR strategy/timeouts if provided
        pass

    def set_bridge_device(self, bridge_device: PymordialBridgeDevice) -> None:
        """Sets the bridge device (dependency injection).

        Args:
             bridge_device: The bridge device instance to use.
        """
        self._bridge_device = bridge_device

    def shutdown(self) -> None:
        """Cleans up resources."""
        pass

    def scale_img_to_screen(
        self,
        image_path: str,
        screen_image: "str | Image.Image | bytes | np.ndarray",
        bluestacks_resolution: tuple[int, int],
    ) -> Image.Image:
        """Scales an image to match the current screen resolution.

        Args:
            image_path: The file path to the reference image (needle) to scale.
            screen_image: The current screen content. Can be a file path,
                bytes, numpy array, or a PIL Image object.
            bluestacks_resolution: The reference resolution (width, height)
                that the image_path was originally captured at.

        Returns:
            A PIL Image object of the needle image, scaled to match the
            dimensions of the provided screen_image.
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
        pymordial_screenshot: "bytes | np.ndarray | None" = None,
    ) -> bool | None:
        """Checks if a specific pixel matches a target color within a given tolerance.

        If a screenshot is not provided, one will be captured automatically from
        the connected device.

        Args:
            pymordial_pixel: The pixel element definition containing coordinates,
                target color, and tolerance.
            pymordial_screenshot: Optional current screen content. Can be bytes
                or a numpy array. If None, a fresh screenshot is captured.

        Returns:
            True if the pixel at the specified coordinates matches the target
            color within the tolerance. Returns None if the pixel element has
            no position defined.

        Raises:
            ValueError: If the screenshot cannot be captured, processed, or if
                the pixel definition is invalid (e.g., missing coordinates).
        """

        def check_color_with_tolerance(
            color1: tuple[int, int, int], color2: tuple[int, int, int], tolerance: int
        ) -> bool:
            """Check if two colors are within a certain tolerance."""
            return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

        # Capture screen if we don't have an image to check
        if pymordial_screenshot is None:
            # Ensures ADB is connected
            if not self._bridge_device.is_connected():
                self._bridge_device.connect()
                if not self._bridge_device.is_connected():
                    raise ValueError("ADB is not connected")

            try:
                pymordial_screenshot = self._bridge_device.capture_screen()
                if pymordial_screenshot is None:
                    self.logger.warning("Failed to capture screen.")
            # except TcpTimeoutException:
            #    raise TcpTimeoutException(
            #        f"TCP timeout while finding element {pymordial_element.label}"
            #    )
            except Exception as e:
                self.logger.error(f"Error capturing screen: {e}")

        try:
            if pymordial_pixel.position is None:
                self.logger.warning(
                    f"PymordialPixel {pymordial_pixel.label} has no position defined. Cannot find."
                )
                return None

            # Ensure coordinates are integers
            target_coords = (
                int(pymordial_pixel.position[0]),
                int(pymordial_pixel.position[1]),
            )

            # Scale coordinates if og_resolution is defined
            if pymordial_pixel.og_resolution is not None:
                # Get the actual screenshot dimensions
                if isinstance(pymordial_screenshot, bytes):
                    with Image.open(BytesIO(pymordial_screenshot)) as img:
                        actual_width, actual_height = img.size
                elif isinstance(pymordial_screenshot, np.ndarray):
                    actual_height, actual_width = pymordial_screenshot.shape[:2]
                else:
                    actual_width, actual_height = pymordial_pixel.og_resolution

                og_width, og_height = pymordial_pixel.og_resolution
                scale_x = actual_width / og_width
                scale_y = actual_height / og_height
                original_coords = target_coords
                target_coords = (
                    int(target_coords[0] * scale_x),
                    int(target_coords[1] * scale_y),
                )
                self.logger.debug(
                    f"Resolution scaling for '{pymordial_pixel.label}': "
                    f"og={og_width}x{og_height}, actual={actual_width}x{actual_height}, "
                    f"scale=({scale_x:.2f}, {scale_y:.2f}), "
                    f"coords {original_coords} -> {target_coords}"
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

            if pymordial_screenshot is None:
                raise ValueError(
                    f"Failed to capture screenshot for {pymordial_pixel.label}"
                )

            if isinstance(pymordial_screenshot, bytes):
                with Image.open(BytesIO(pymordial_screenshot)) as image:
                    pixel_color = image.getpixel(target_coords)
                    is_match = check_color_with_tolerance(
                        pixel_color,
                        pymordial_pixel.pixel_color,
                        pymordial_pixel.tolerance,
                    )
                    self.logger.debug(
                        f"Pixel check '{pymordial_pixel.label}' at {target_coords}: "
                        f"actual={pixel_color}, expected={pymordial_pixel.pixel_color}, "
                        f"tolerance={pymordial_pixel.tolerance}, match={is_match}"
                    )
                    return is_match
            elif isinstance(pymordial_screenshot, np.ndarray):
                image = Image.fromarray(pymordial_screenshot)
                pixel_color = image.getpixel(target_coords)
                is_match = check_color_with_tolerance(
                    pixel_color,
                    pymordial_pixel.pixel_color,
                    pymordial_pixel.tolerance,
                )
                self.logger.debug(
                    f"Pixel check '{pymordial_pixel.label}' at {target_coords}: "
                    f"actual={pixel_color}, expected={pymordial_pixel.pixel_color}, "
                    f"tolerance={pymordial_pixel.tolerance}, match={is_match}"
                )
                return is_match
            else:
                raise ValueError(
                    f"Image must be a bytes or numpy array, not {type(pymordial_screenshot)}"
                )

        except ValueError as e:
            self.logger.error(f"ValueError in check_pixel_color: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error in check_pixel_color: {e}")
            raise ValueError(f"Error checking pixel color: {e}") from e

    def where_element(
        self,
        pymordial_element: PymordialElement,
        pymordial_screenshot: "bytes | np.ndarray | None" = None,
        max_tries: int | None = None,
        set_position: bool = False,
        set_size: bool = False,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of a PymordialElement on the screen.

        Args:
            pymordial_element: The PymordialElement instance to locate.
            pymordial_screenshot: Optional pre-captured screenshot (bytes or
                numpy array) to search within. If None, a new screenshot will
                be captured.
            max_tries: Maximum number of attempts to find the element. If None,
                it will retry indefinitely (useful for waiting on loading screens).
            set_position: If True, updates the element's `position` attribute
                with the found coordinates.
            set_size: If True, updates the element's `size` attribute with the
                found dimensions.

        Returns:
            A tuple containing (x, y) coordinates of the element's center if found,
            or None if the element was not found after the specified attempts.

        Note:
            If max_tries is None, this method loops indefinitely until the element
            is found.
        """
        self.logger.debug(f"Looking for PymordialElement: {pymordial_element.label}...")
        if max_tries is None:
            max_tries = self.config["default_find_ui_retries"]

        find_ui_retries: int = 0
        pymordial_screenshot = pymordial_screenshot

        while (find_ui_retries < max_tries) if max_tries is not None else True:
            # Capture screen if we don't have an image to check
            if pymordial_screenshot is None:
                # Ensures ADB is connected
                if not self._bridge_device.is_connected():
                    self._bridge_device.connect()
                    if not self._bridge_device.is_connected():
                        raise ValueError("ADB is not connected")

                try:
                    pymordial_screenshot = self._bridge_device.capture_screen()
                    if pymordial_screenshot is None:
                        self.logger.warning("Failed to capture screen.")
                except TcpTimeoutException:
                    raise TcpTimeoutException(
                        f"TCP timeout while finding element {pymordial_element.label}"
                    )
                except Exception as e:
                    self.logger.error(f"Error capturing screen: {e}")

            if pymordial_screenshot is not None:
                if isinstance(pymordial_element, PymordialImage):
                    ui_location = None
                    try:
                        if isinstance(pymordial_screenshot, bytes):
                            haystack_img = Image.open(BytesIO(pymordial_screenshot))
                        elif isinstance(pymordial_screenshot, np.ndarray):
                            haystack_img = Image.fromarray(pymordial_screenshot)
                        elif isinstance(pymordial_screenshot, Image.Image):
                            haystack_img = pymordial_screenshot
                        else:
                            # Should not happen if capture_screen returns correct types
                            self.logger.warning(
                                f"Unsupported image type: {type(pymordial_screenshot)}. Attempting to open as file path if string."
                            )
                            if isinstance(pymordial_screenshot, str):
                                haystack_img = Image.open(pymordial_screenshot)
                            else:
                                raise ValueError(
                                    f"Unsupported image type: {type(pymordial_screenshot)}"
                                )

                        # Scale the needle image to match current resolution
                        scaled_img = self.scale_img_to_screen(
                            image_path=pymordial_element.filepath,
                            screen_image=haystack_img,
                            bluestacks_resolution=pymordial_element.og_resolution,
                        )

                        # Prepare OpenCV images
                        haystack_cv = cv2.cvtColor(
                            np.array(haystack_img), cv2.COLOR_RGB2BGR
                        )
                        needle_cv = cv2.cvtColor(
                            np.array(scaled_img), cv2.COLOR_RGB2BGR
                        )

                        if pymordial_element.region:
                            left, top, width, height = pymordial_element.region
                            haystack_cv = haystack_cv[
                                top : top + height, left : left + width
                            ]
                        else:
                            left, top = 0, 0

                        result = cv2.matchTemplate(
                            haystack_cv, needle_cv, cv2.TM_CCOEFF_NORMED
                        )
                        _, max_val, _, max_loc = cv2.minMaxLoc(result)

                        if max_val >= pymordial_element.confidence:
                            # max_loc is (x, y) relative to the region
                            match_x = max_loc[0] + left
                            match_y = max_loc[1] + top
                            match_w, match_h = scaled_img.size

                            ui_location = (match_x, match_y, match_w, match_h)
                        else:
                            ui_location = None

                    except Exception as e:
                        self.logger.error(
                            f"Error finding element {pymordial_element.label}: {e}"
                        )

                    if ui_location:
                        # coords = center(ui_location) -> (x + w//2, y + h//2)
                        coords = (
                            ui_location[0] + ui_location[2] // 2,
                            ui_location[1] + ui_location[3] // 2,
                        )
                        self.logger.debug(
                            f"PymordialImage {pymordial_element.label} found at: {coords}"
                        )

                        if set_position:
                            # ui_location is (left, top, width, height)
                            pymordial_element.position = (
                                ui_location[0],
                                ui_location[1],
                            )
                            self.logger.debug(
                                f"Updated position for {pymordial_element.label} to {pymordial_element.position}"
                            )

                        if set_size:
                            # ui_location is (left, top, width, height)
                            pymordial_element.size = (ui_location[2], ui_location[3])
                            self.logger.debug(
                                f"Updated size for {pymordial_element.label} to {pymordial_element.size}"
                            )

                        return coords
                else:
                    raise NotImplementedError(
                        f"Element type: {type(pymordial_element)} is not supported."
                    )

            # Prepare for next retry
            find_ui_retries += 1
            pymordial_screenshot = None  # Force capture on next iteration

            if max_tries is not None and find_ui_retries >= max_tries:
                break

            self.logger.debug(
                f"PymordialImage {pymordial_element.label} not found. Retrying... ({find_ui_retries}/{max_tries})"
            )
            sleep(self.config["default_wait_time"])

        self.logger.info(
            f"Wasn't able to find PymordialImage within {max_tries} retries: {pymordial_element.label}"
        )
        return None

    def where_elements(
        self,
        pymordial_elements: list[PymordialElement],
        pymordial_screenshot: "bytes | np.ndarray | None" = None,
        max_tries: int | None = None,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of the first found element from a list.

        Args:
            pymordial_elements: A list of PymordialElement objects to search for.
            pymordial_screenshot: Optional pre-captured screenshot (bytes or
                numpy array) to avoid capturing a new one.
            max_tries: Maximum number of retries for each element in the list.

        Returns:
            A tuple containing (x, y) coordinates of the first element successfully
            located, or None if no elements from the list were found.
        """
        if max_tries is None:
            max_tries = self.config["default_find_ui_retries"]
        for pymordial_element in pymordial_elements:
            coord: tuple[int, int] | None = self.where_element(
                pymordial_element=pymordial_element,
                pymordial_screenshot=pymordial_screenshot,
                max_tries=max_tries,
            )
            if coord is not None:
                return coord
        return None

    def find_text(
        self,
        text_to_find: str,
        pymordial_screenshot: "Path | bytes | str | np.ndarray",
        strategy: PymordialExtractStrategy | None = None,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of specific text in the image.

        Args:
            text_to_find: The text string to search for.
            pymordial_screenshot: The source image to search within. Can be a
                file path (str or Path) or raw image bytes.
            strategy: Optional preprocessing strategy to apply before OCR.

        Returns:
            A tuple containing (x, y) coordinates of the found text center, or
            None if the text was not found.
        """
        try:
            # Check if the OCR engine supports find_text (it should as per PymordialOCRDevice)
            if hasattr(self._ocr_device, "find_text"):
                # Pass strategy if it's PymordialTesseractDevice, otherwise just the required args
                if isinstance(self._ocr_device, PymordialTesseractDevice):
                    return self._ocr_device.find_text(
                        text_to_find, pymordial_screenshot, strategy=strategy
                    )
                return self._ocr_device.find_text(text_to_find, pymordial_screenshot)
            else:
                self.logger.warning(
                    f"OCR engine {type(self._ocr_device).__name__} does not support find_text"
                )
                return None
        except Exception as e:
            self.logger.error(f"Error finding text in image: {e}")
            return None

    def check_text(
        self,
        text_to_find: str,
        pymordial_screenshot: "Path | bytes | str | np.ndarray",
        case_sensitive: bool = False,
        strategy: PymordialExtractStrategy | None = None,
    ) -> bool:
        """Checks if specific text is present in the image.

        Args:
            text_to_find: The exact text string to search for.
            pymordial_screenshot: The source image to search within. Can be a
                file path (str or Path), raw image bytes, or a numpy array.
            case_sensitive: If True, performs a case-sensitive search.
                Defaults to False.
            strategy: Optional preprocessing strategy to apply before OCR.
                This is currently only supported by PymordialTesseractDevice.

        Returns:
            True if the text is found in the image, False otherwise.

        Raises:
            ValueError: If the image cannot be loaded or processed.
        """

        # Capture screen if we don't have an image to check
        if pymordial_screenshot is None:
            # Ensures ADB is connected
            if not self._bridge_device.is_connected():
                self._bridge_device.connect()
                if not self._bridge_device.is_connected():
                    raise ValueError("ADB is not connected")

            try:
                pymordial_screenshot = self._bridge_device.capture_screen()
                if pymordial_screenshot is None:
                    self.logger.warning("Failed to capture screen.")
            # except TcpTimeoutException:
            #    raise TcpTimeoutException(
            #        f"TCP timeout while finding element {pymordial_element.label}"
            #    )
            except Exception as e:
                self.logger.error(f"Error capturing screen: {e}")

        try:
            # Extract text with optional strategy (if supported)
            if strategy is not None and isinstance(
                self._ocr_device, PymordialTesseractDevice
            ):
                extracted = self._ocr_device.extract_text(
                    pymordial_screenshot, strategy=strategy
                )
            else:
                extracted = self._ocr_device.extract_text(pymordial_screenshot)

            if case_sensitive:
                return text_to_find in extracted
            return text_to_find.lower() in extracted.lower()
        except Exception as e:
            self.logger.error(f"Error checking text in image: {e}")
            raise ValueError(f"Error checking text in image: {e}") from e

    def read_text(
        self,
        pymordial_screenshot: "Path | bytes | str | np.ndarray",
        case_sensitive: bool = False,
        strategy: PymordialExtractStrategy | None = None,
    ) -> list[str]:
        """Reads and extracts text lines from an image.

        Args:
            pymordial_screenshot: The source image to read text from. Can be a
                file path (str or Path), raw image bytes, or a numpy array.
            case_sensitive: If True, preserves the original case of the text.
                If False, converts all text to lowercase. Defaults to False.
            strategy: Optional preprocessing strategy to apply before OCR.
                This is currently only supported by PymordialTesseractDevice.

        Returns:
            A list of strings, where each string corresponds to a line of text
            detected in the image. Empty lines and whitespace-only lines are
            excluded.

        Raises:
            ValueError: If the image cannot be loaded or processed by the OCR engine.
        """

        try:
            # Extract text with optional strategy (if supported)
            if strategy is not None and isinstance(
                self._ocr_device, PymordialTesseractDevice
            ):
                text = self._ocr_device.extract_text(
                    pymordial_screenshot, strategy=strategy
                )
            else:
                text = self._ocr_device.extract_text(pymordial_screenshot)
            if case_sensitive:
                return [line.strip() for line in text.split("\n") if line.strip()]
            return [
                line.strip().lower()
                for line in text.split("\n")
                if line.strip().lower()
            ]
        except Exception as e:
            self.logger.error(f"Error reading text from image: {e}")
            raise ValueError(f"Error reading text from image: {e}") from e
