"""Main controller for the Pymordial automation framework."""

import logging
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from PIL import Image

from pymordial.controller.adb_controller import AdbController
from pymordial.controller.bluestacks_controller import BluestacksController
from pymordial.controller.image_controller import ImageController
from pymordial.controller.text_controller import TextController
from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.elements.pymordial_pixel import PymordialPixel
from pymordial.core.elements.pymordial_text import PymordialText
from pymordial.core.pymordial_element import PymordialElement
from pymordial.ocr.extract_strategy import PymordialExtractStrategy
from pymordial.state_machine import EmulatorState
from pymordial.utils.config import get_config

if TYPE_CHECKING:
    from pymordial.core.pymordial_app import PymordialApp

logger = logging.getLogger(__name__)

_CONFIG = get_config()


class PymordialController:
    """Main controller that orchestrates ADB, BlueStacks, and Image controllers.

    Attributes:
        adb: The AdbController instance.
        image: The ImageController instance.
        bluestacks: The BluestacksController instance.
    """

    DEFAULT_CLICK_TIMES = _CONFIG["controller"]["default_click_times"]
    DEFAULT_MAX_TRIES = _CONFIG["controller"]["default_max_tries"]
    CLICK_COORD_TIMES = _CONFIG["controller"]["click_coord_times"]
    CMD_TAP = _CONFIG["adb"]["commands"]["tap"]

    def __init__(
        self,
        adb_host: str | None = None,
        adb_port: int | None = None,
        apps: list["PymordialApp"] | None = None,
    ):
        """Initializes the PymordialController.

        Args:
            adb_host: Optional ADB host address.
            adb_port: Optional ADB port.
            apps: Optional list of PymordialApp instances to register.
        """
        self.adb = AdbController(host=adb_host, port=adb_port)
        self.image = ImageController(self)
        self.text = TextController(pymordial_controller=self)
        self.bluestacks = BluestacksController(self)
        self._apps: dict[str, "PymordialApp"] = {}
        self._streaming_enabled = False  # Track if streaming should be active

        if apps:
            for app in apps:
                self.add_app(app)

    @property
    def is_streaming(self) -> bool:
        """Check if streaming is currently active.

        Returns:
            True if streaming is active, False otherwise.
        """
        return self.adb._is_streaming.is_set()

    def __getattr__(self, name: str) -> "PymordialApp":
        """Enables dot-notation access to registered apps.

        Args:
            name: The name of the app to access.

        Returns:
            The registered PymordialApp instance.

        Raises:
            AttributeError: If the app is not found.
        """
        if name in self._apps:
            return self._apps[name]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'. "
            f"Available apps: {list(self._apps.keys())}"
        )

    # --- Convenience Methods (delegate to sub-controllers) ---
    ## --- App Management ---
    def add_app(self, app: "PymordialApp") -> None:
        """Registers a PymordialApp instance with this controller.

        Args:
            app: The PymordialApp instance to register.

        Raises:
            ValueError: If the app is already registered with a different controller.
        """
        # Set controller reference if not set
        if (
            app.pymordial_controller is not None
            and app.pymordial_controller is not self
        ):
            raise ValueError(
                f"App '{app.app_name}' is already registered with a different controller."
            )
        app.pymordial_controller = self

        # Sanitize app_name for attribute access
        sanitized_name = app.app_name.replace("-", "_").replace(" ", "_")

        # Store in registry
        self._apps[sanitized_name] = app

    def list_apps(self) -> list[str]:
        """Returns a list of registered app names.

        Returns:
            List of registered app names.
        """
        return list(self._apps.keys())

    def disconnect(self) -> None:
        """Closes the ADB connection and performs cleanup."""
        if self.adb.is_connected():
            self.adb.disconnect()

    ## --- Click Methods ---
    def click_coord(
        self, coords: tuple[int, int], times: int = CLICK_COORD_TIMES
    ) -> bool:
        """Clicks specific coordinates on the screen.

        Args:
            coords: (x, y) coordinates to click.
            times: Number of times to click.

        Returns:
            True if the click was sent successfully, False otherwise.
        """
        # Ensure Bluestacks is ready before trying to click coords
        match self.bluestacks.bluestacks_state.current_state:
            case EmulatorState.CLOSED | EmulatorState.LOADING:
                logger.warning("Cannot click coords - Bluestacks is not ready")
                return False
            case EmulatorState.READY:
                is_connected = self.adb.is_connected()
                if not is_connected:
                    logger.warning(
                        "ADB device not connected. Skipping 'click_coords' method call."
                    )
                    return False
                single_tap = PymordialController.CMD_TAP.format(
                    x=coords[0], y=coords[1]
                )
                tap_command = " && ".join([single_tap] * times)

                self.adb.shell_command(tap_command)
                logger.debug(
                    f"Click event sent via ADB at coords x={coords[0]}, y={coords[1]}"
                )
                return True

    def click_element(
        self,
        pymordial_element: PymordialElement,
        times: int = DEFAULT_CLICK_TIMES,
        screenshot_img_bytes: bytes | None = None,
        max_tries: int = DEFAULT_MAX_TRIES,
    ) -> bool:
        """Clicks a UI element on the screen.

        Args:
            pymordial_element: The element to click.
            times: Optional number of times to click. Defaults to DEFAULT_CLICK_TIMES config.
            screenshot_img_bytes: Optional pre-captured screenshot to look for the element in. Defaults to None.
            max_tries: Optional maximum number of retries to find the element. Defaults to DEFAULT_MAX_TRIES config.

        Returns:
            True if the element was found and clicked, False otherwise.
        """
        # Ensure Bluestacks is ready before trying to click ui
        match self.bluestacks.bluestacks_state.current_state:
            case EmulatorState.CLOSED | EmulatorState.LOADING:
                logger.warning("Cannot click coords - Bluestacks is not ready")
                return False
            case EmulatorState.READY:
                if not self.adb.is_connected():
                    self.adb.connect()
                    if not self.adb.is_connected():
                        logger.warning(
                            "ADB device not connected. Skipping 'click_element' method call."
                        )
                        return False
                coord: tuple[int, int] | None = self.find_element(
                    pymordial_element=pymordial_element,
                    pymordial_screenshot=screenshot_img_bytes,
                    max_tries=max_tries,
                )
                if not coord:
                    logger.debug(f"UI element {pymordial_element.label} not found")
                    return False
                if self.click_coord(coord, times=times):
                    logger.debug(
                        f"Click event sent via ADB at coords x={coord[0]}, y={coord[1]}"
                    )
                    return True
                return False
            case _:
                logger.warning(
                    "Cannot click coords - PymordialController.bluestacks_state.current_state is not in a valid state."
                    " Make sure it is in the 'EmulatorState.READY' state."
                )
                return False

    def click_elements(
        self,
        pymordial_elements: list[PymordialElement],
        screenshot_img_bytes: bytes | None = None,
        max_tries: int = DEFAULT_MAX_TRIES,
    ) -> bool:
        """Clicks any of the elements in the list.

        Args:
            pymordial_elements: List of elements to try clicking.
            screenshot_img_bytes: Optional pre-captured screenshot.
            max_tries: Maximum number of retries per element.

        Returns:
            True if any element was clicked, False otherwise.
        """
        return any(
            self.click_element(
                pymordial_element=pymordial_element,
                screenshot_img_bytes=screenshot_img_bytes,
                max_tries=max_tries,
            )
            for pymordial_element in pymordial_elements
        )

    def go_home(self) -> None:
        """Navigate to Android home screen.

        Convenience method that delegates to adb.go_home().
        """
        self.adb.go_home()

    def go_back(self) -> None:
        """Press Android back button.

        Convenience method that delegates to adb.go_back().
        """
        self.adb.go_back()

    def tap(self, x: int, y: int) -> None:
        """Tap at specific coordinates.

        Args:
            x: X coordinate.
            y: Y coordinate.

        Convenience method that delegates to adb.tap().
        """
        return self.adb.tap(x, y)

    def swipe(
        self, start_x: int, start_y: int, end_x: int, end_y: int, duration: int = 300
    ) -> None:
        """Perform swipe gesture.

        Args:
            start_x: Starting X coordinate.
            start_y: Starting Y coordinate.
            end_x: Ending X coordinate.
            end_y: Ending Y coordinate.
            duration: Swipe duration in milliseconds.

        Convenience method that delegates to adb.swipe().
        """
        return self.adb.swipe(start_x, start_y, end_x, end_y, duration)

    def capture_screen(self) -> "bytes | np.ndarray | None":
        """Captures the current BlueStacks screen using the appropriate capture strategy.

        Returns:
            The screenshot as bytes or numpy array, or None if failed.
        """

        if not self.adb.is_connected():
            self.adb.connect()
            if not self.adb.is_connected():
                logger.warning(
                    "Cannot capture screen - ADB controller is not initialized"
                )
                return None

        # Always use streaming - start if not active
        if not self.is_streaming:
            logger.info("Starting stream for capture_screen...")
            if not self.start_streaming():
                logger.error("Failed to start stream")
                return None

        frame = self.adb.get_latest_frame()
        if frame is not None:
            # Validate frame isn't corrupted (all same color)
            if frame.std() < 1.0:  # Nearly uniform = likely corrupted
                logger.warning(
                    "Frame appears corrupted (uniform color), restarting stream..."
                )
                self.adb.stop_stream()
                if self.start_streaming():
                    frame = self.adb.get_latest_frame()
                    if frame is not None and frame.std() >= 1.0:
                        logger.debug("Returning fresh frame after restart.")
                        return frame
                logger.error("Failed to get valid frame after restart")
                return None
            logger.debug("Returning latest frame from stream.")
            return frame

        logger.warning("Stream active but no frame available.")
        return None

    def find_element(
        self,
        pymordial_element: PymordialElement,
        pymordial_screenshot: bytes | None = None,
        max_tries: int = DEFAULT_MAX_TRIES,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of a UI element on the screen.

        Args:
            pymordial_element: The element to find.
            screenshot_img_bytes: Optional pre-captured screenshot.
            max_tries: Maximum number of retries.

        Returns:
            (x, y) coordinates if found, None otherwise.
        """
        if isinstance(pymordial_element, PymordialImage):
            return self.image.where_element(
                pymordial_element=pymordial_element,
                pymordial_screenshot=pymordial_screenshot,
                max_tries=max_tries,
            )
        elif isinstance(pymordial_element, PymordialText):
            return self.text.find_text(
                text_to_find=pymordial_element.element_text,
                pymordial_screenshot=pymordial_screenshot,
                strategy=pymordial_element.extract_strategy,
            )
        elif isinstance(pymordial_element, PymordialPixel):
            # Capture screenshot if not provided (avoid 'or' with numpy arrays)
            pixel_screenshot = (
                pymordial_screenshot
                if pymordial_screenshot is not None
                else self.capture_screen()
            )
            is_match = self.image.check_pixel_color(
                pymordial_pixel=pymordial_element,
                pymordial_screenshot=pixel_screenshot,
            )
            return pymordial_element.position if is_match else None

        raise NotImplementedError(
            f"find_element() not implemented for this element type: {type(pymordial_element)}"
        )

    def is_element_visible(
        self,
        pymordial_element: PymordialElement,
        pymordial_screenshot: bytes | None = None,
        max_tries: int | None = None,
    ) -> bool:
        """Checks if a UI element is visible on the screen.

        Args:
            pymordial_element: The element to check for.
            pymordial_screenshot: Optional pre-captured screenshot.
            max_tries: Optional maximum number of retries.

        Returns:
            True if the element is found, False otherwise.
        """
        if not isinstance(pymordial_element, PymordialElement):
            raise TypeError(
                f"pymordial_element must be an instance of PymordialElement, not {type(pymordial_element)}"
            )

        if isinstance(pymordial_element, PymordialImage):
            return (
                self.find_element(
                    pymordial_element=pymordial_element,
                    pymordial_screenshot=pymordial_screenshot,
                    max_tries=max_tries or PymordialController.DEFAULT_MAX_TRIES,
                )
                is not None
            )
        elif isinstance(pymordial_element, PymordialText):
            # For text, we use the text controller to check existence
            # Note: This doesn't return coordinates yet, so click_element won't work for Text
            # unless find_element is implemented for Text.

            # If the element has a defined region, crop the image to that region
            if pymordial_element.region and pymordial_screenshot is not None:
                try:
                    if isinstance(pymordial_screenshot, bytes):
                        pymordial_screenshot = Image.open(BytesIO(pymordial_screenshot))
                    elif isinstance(pymordial_screenshot, np.ndarray):
                        pymordial_screenshot = Image.fromarray(pymordial_screenshot)
                    else:
                        pymordial_screenshot = None

                    if pymordial_screenshot is not None:
                        # region is (left, top, right, bottom)
                        pymordial_screenshot = pymordial_screenshot.crop(
                            pymordial_element.region
                        )
                        pymordial_screenshot = np.array(pymordial_screenshot)
                except Exception as e:
                    logger.warning(f"Failed to crop image for text detection: {e}")

            return self.text.check_text(
                text_to_find=pymordial_element.element_text,
                pymordial_screenshot=pymordial_screenshot,
                strategy=pymordial_element.extract_strategy,
                case_sensitive=False,
            )
        elif isinstance(pymordial_element, PymordialPixel):
            return (
                self.find_element(
                    pymordial_element=pymordial_element,
                    pymordial_screenshot=pymordial_screenshot,
                    max_tries=max_tries or PymordialController.DEFAULT_MAX_TRIES,
                )
                is not None
            )
        else:
            raise NotImplementedError(
                f"is_element_visible not implemented for {type(pymordial_element)}"
            )

    # --- Input Methods ---

    def press_enter(self) -> None:
        """Press the Enter key.

        Convenience method that delegates to adb.press_enter().
        """
        return self.adb.press_enter()

    def press_esc(self) -> None:
        """Press the Esc key.

        Convenience method that delegates to adb.press_esc().
        """
        return self.adb.press_esc()

    def send_text(self, text: str) -> None:
        """Send text input to the device.

        Args:
            text: Text to send.

        Convenience method that delegates to adb.send_text().
        """
        return self.adb.send_text(text)

    # --- Shell & Utility Methods ---

    def shell_command(self, command: str) -> bytes | None:
        """Execute ADB shell command.

        Args:
            command: Shell command to execute.

        Returns:
            Command output as bytes, or None if failed.

        Convenience method that delegates to adb.shell_command().
        """
        return self.adb.shell_command(command)

    def get_current_app(self) -> str | None:
        """Get the currently running app's package name.

        Returns:
            Package name of current app, or None if failed.

        Convenience method that delegates to adb.get_current_app().
        """
        return self.adb.get_current_app()

    # --- OCR Methods ---

    def read_text(
        self,
        image_path: "Path | bytes | str",
        case_sensitive: bool = False,
        strategy: "PymordialExtractStrategy | None" = None,
    ) -> list[str]:
        """Read text from an image using OCR.

        Args:
            image_path: Path to image file, image bytes, or string path.
            strategy: Optional preprocessing strategy.

        Returns:
            List of detected text lines.

        Convenience method that delegates to text.read_text().
        """
        return self.text.read_text(image_path, case_sensitive, strategy)

    def check_text(
        self,
        text_to_find: str,
        image_path: "Path | bytes | str",
        case_sensitive: bool = False,
        strategy: "PymordialExtractStrategy | None" = None,
    ) -> bool:
        """Check if specific text exists in an image.

        Args:
            text_to_find: Text to search for.
            image_path: Image to search in.
            case_sensitive: Whether search is case-sensitive.
            strategy: Optional preprocessing strategy.

        Returns:
            True if text found, False otherwise.

        Convenience method that delegates to text.check_text().
        """
        return self.text.check_text(text_to_find, image_path, case_sensitive, strategy)

    # --- State Checking Methods ---

    def is_bluestacks_ready(self) -> bool:
        """Check if BlueStacks is in READY state.

        Returns:
            True if BlueStacks is ready, False otherwise.

        Convenience method that delegates to self.bluestacks.is_ready().
        """
        return self.bluestacks.is_ready()

    def is_bluestacks_loading(self) -> bool:
        """Check if BlueStacks is currently loading.

        Returns:
            True if BlueStacks is loading, False otherwise.

        Convenience method that delegates to bluestacks.is_loading().
        """
        return self.bluestacks.is_loading()

    # --- Streaming Methods ---

    def start_streaming(
        self, width: int = 1920, height: int = 1080, bitrate: str = "5M"
    ) -> bool:
        """Start video streaming for real-time frame access.

        Blocks until first frame is available or timeout.
        For real-time botting, streaming provides much lower latency
        than repeated screenshot capture (16-33ms vs 100-300ms).

        Args:
            width: Stream width. Default is 1920.
            height: Stream height. Default is 1080.
            bitrate: Stream bitrate (e.g., "5M" for 5 Mbps). Default is "5M".

        Returns:
            True if streaming started successfully, False otherwise.

        Convenience method that delegates to adb.start_stream().

        Example:
            >>> if controller.start_streaming():
            ...     frame = controller.get_frame()
            ...     # Process frame for real-time bot logic
            ...     text = controller.read_text(frame)
        """
        result = self.adb.start_stream(width, height, bitrate)
        if result:
            self._streaming_enabled = True
        return result

    def get_frame(self) -> "np.ndarray | None":
        """Get the latest frame from the active stream.

        Returns:
            Latest frame as numpy array (RGB), or None if unavailable.

        Convenience method that delegates to adb.get_latest_frame().

        Example:
            >>> frame = controller.get_frame()
            >>> if frame is not None:
            ...     # Process frame (OCR, template matching, etc.)
            ...     text = controller.read_text(frame)
        """
        return self.adb.get_latest_frame()

    def stop_streaming(self) -> None:
        """Stop the active video stream and disable auto-restart.

        Convenience method that delegates to adb.stop_stream().
        """
        self._streaming_enabled = False
        return self.adb.stop_stream()

    def __repr__(self) -> str:
        """Returns a string representation of the PymordialController."""
        return (
            f"PymordialController("
            f"apps={len(self.apps)}, "
            f"adb_connected={self.adb.is_connected()}, "
            f"bluestacks={self.bluestacks.bluestacks_state.current_state.name})"
        )
