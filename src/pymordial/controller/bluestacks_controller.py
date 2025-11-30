"""Controller for managing the BlueStacks emulator."""

import io
import logging
import os
import time
from importlib.resources import files

import psutil
import win32con
import win32gui
from PIL import Image, ImageGrab

from pymordial.controller.adb_controller import AdbController
from pymordial.controller.image_controller import ImageController
from pymordial.core.elements.pymordial_button import PymordialButton
from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.pymordial_app import PymordialApp
from pymordial.core.pymordial_element import PymordialElement
from pymordial.state_machine import BluestacksState, StateMachine
from pymordial.utils import validate_and_convert_int
from pymordial.utils.config import get_config

_CONFIG = get_config()

# --- Bluestacks Configuration ---
DEFAULT_TRANSPORT_TIMEOUT_S = _CONFIG["bluestacks"]["default_transport_timeout_s"]
WAIT_FOR_LOAD_TIMEOUT = _CONFIG["bluestacks"]["wait_for_load_timeout"]
HD_PLAYER_EXE = _CONFIG["bluestacks"]["hd_player_exe"]
DEFAULT_REF_WINDOW_SIZE = tuple(_CONFIG["bluestacks"]["resolution"])
DEFAULT_MAX_RETRIES = _CONFIG["bluestacks"]["default_max_retries"]
DEFAULT_WAIT_TIME = _CONFIG["bluestacks"]["default_wait_time"]
DEFAULT_TIMEOUT = _CONFIG["bluestacks"]["default_timeout"]
PROCESS_WAIT_TIMEOUT = _CONFIG["adb"]["process_wait_timeout"]
WINDOW_TITLE = _CONFIG["bluestacks"]["window_title"]
UI_LOADING_IMG_LABEL = _CONFIG["bluestacks"]["ui"]["loading_img_label"]
UI_LOADING_TEXT = _CONFIG["bluestacks"]["ui"]["loading_text"]
UI_MY_GAMES_BUTTON_LABEL = _CONFIG["bluestacks"]["ui"]["my_games_button_label"]
UI_MY_GAMES_TEXT = _CONFIG["bluestacks"]["ui"]["my_games_text"]
UI_STORE_SEARCH_INPUT_LABEL = _CONFIG["bluestacks"]["ui"]["store_search_input_label"]
UI_STORE_SEARCH_TEXT = _CONFIG["bluestacks"]["ui"]["store_search_text"]
UI_STORE_BUTTON_LABEL = _CONFIG["bluestacks"]["ui"]["store_button_label"]
UI_PLAYSTORE_SEARCH_INPUT_LABEL = _CONFIG["bluestacks"]["ui"][
    "playstore_search_input_label"
]
UI_LOADING_SCREEN_IMG_LABEL = _CONFIG["bluestacks"]["ui"]["loading_screen_img_label"]
UI_ADB_SCREENSHOT_IMG_LABEL = _CONFIG["bluestacks"]["ui"]["adb_screenshot_img_label"]

# --- Assets ---
ASSET_LOADING_IMG = _CONFIG["assets"]["bluestacks_loading_img"]
ASSET_MY_GAMES_BUTTON = _CONFIG["assets"]["bluestacks_my_games_button"]
ASSET_STORE_SEARCH_INPUT = _CONFIG["assets"]["bluestacks_store_search_input"]
ASSET_STORE_BUTTON = _CONFIG["assets"]["bluestacks_store_button"]
ASSET_PLAYSTORE_SEARCH_INPUT = _CONFIG["assets"]["bluestacks_playstore_search_input"]
ASSET_LOADING_SCREEN_IMG = _CONFIG["assets"]["bluestacks_loading_screen_img"]
ASSET_ADB_SCREENSHOT_IMG = _CONFIG["assets"]["adb_screenshot_img"]


# Initialize logger
logger = logging.getLogger(__name__)


def log_property_setter(func):
    """Decorator to log property setter operations.

    Args:
        func: The property setter function to decorate.

    Returns:
        The decorated function.
    """

    def wrapper(self, value: object | None):
        logger.debug(f"Setting {func.__name__}...")
        result = func(self, value)
        logger.debug(f"{func.__name__} set to {value}")
        return result

    return wrapper


class BluestacksElements:
    """Stores BlueStacks UI elements.

    Attributes:
        controller: The BluestacksController instance.
        bluestacks_loading_img: Image element for loading screen.
        bluestacks_my_games_button: Button element for 'My games'.
        bluestacks_store_search_input: Input element for store search.
        bluestacks_store_button: Button element for store.
        bluestacks_playstore_search_inpput: Input element for Play Store search.
        bluestacks_loading_screen_img: Image element for full loading screen.
        adb_screenshot_img: Image element for ADB screenshot.
    """

    def __init__(self, controller):
        """Initializes BluestacksElements.

        Args:
            controller: The BluestacksController instance.
        """
        self.controller = controller

        self.bluestacks_loading_img: PymordialElement = PymordialImage(
            label=UI_LOADING_IMG_LABEL,
            bluestacks_resolution=self.controller.ref_window_size,
            asset_path=files("pymordial.assets").joinpath(ASSET_LOADING_IMG),
            confidence=0.7,
            element_text=UI_LOADING_TEXT,
        )

        self.bluestacks_my_games_button: PymordialElement = PymordialButton(
            label=UI_MY_GAMES_BUTTON_LABEL,
            bluestacks_resolution=self.controller.ref_window_size,
            asset_path=files("pymordial.assets").joinpath(ASSET_MY_GAMES_BUTTON),
            confidence=0.6,
            element_text=UI_MY_GAMES_TEXT,
        )

        self.bluestacks_store_search_input: PymordialElement = PymordialImage(
            label=UI_STORE_SEARCH_INPUT_LABEL,
            bluestacks_resolution=self.controller.ref_window_size,
            asset_path=files("pymordial.assets").joinpath(ASSET_STORE_SEARCH_INPUT),
            is_static=False,
            confidence=0.6,
            element_text=UI_STORE_SEARCH_TEXT,
        )

        self.bluestacks_store_button: PymordialElement = PymordialButton(
            label=UI_STORE_BUTTON_LABEL,
            bluestacks_resolution=self.controller.ref_window_size,
            asset_path=files("pymordial.assets").joinpath(ASSET_STORE_BUTTON),
            confidence=0.6,
        )

        self.bluestacks_playstore_search_inpput: PymordialElement = PymordialImage(
            label=UI_PLAYSTORE_SEARCH_INPUT_LABEL,
            bluestacks_resolution=self.controller.ref_window_size,
            asset_path=files("pymordial.assets").joinpath(ASSET_PLAYSTORE_SEARCH_INPUT),
            is_static=False,
            confidence=0.5,
            element_text=UI_STORE_SEARCH_TEXT,
        )

        # Loading elements
        self.bluestacks_loading_screen_img: PymordialElement = PymordialImage(
            label=UI_LOADING_SCREEN_IMG_LABEL,
            bluestacks_resolution=self.controller.ref_window_size,
            asset_path=files("pymordial.assets").joinpath(ASSET_LOADING_SCREEN_IMG),
            is_static=False,
            confidence=0.99,
        )

        self.adb_screenshot_img: PymordialElement = PymordialImage(
            label=UI_ADB_SCREENSHOT_IMG_LABEL,
            bluestacks_resolution=self.controller.ref_window_size,
            asset_path=files("pymordial.assets").joinpath(ASSET_ADB_SCREENSHOT_IMG),
            is_static=False,
            confidence=0.99,
        )


class BluestacksController:
    """Controls the BlueStacks emulator.

    Attributes:
        running_apps: List of currently running PymordialApp instances.
        bluestacks_state: The state machine managing BlueStacks state.
        elements: Container for BlueStacks UI elements.
    """

    def __init__(
        self, adb_controller: AdbController, image_controller: ImageController
    ) -> None:
        """Initializes the BluestacksController.

        Args:
            adb_controller: The AdbController instance.
            image_controller: The ImageController instance.
        """
        logger.info("Initializing BluestacksController")

        self._ref_window_size: tuple[int, int] = DEFAULT_REF_WINDOW_SIZE
        self._filepath: str | None = None
        self._default_transport_timeout_s: int = DEFAULT_TRANSPORT_TIMEOUT_S
        self.running_apps: list[PymordialApp] | list = list()
        self.bluestacks_state = StateMachine(
            current_state=BluestacksState.CLOSED,
            transitions=BluestacksState.get_transitions(),
        )

        self.elements: BluestacksElements = BluestacksElements(self)
        self._autoset_filepath()

        self._adb_controller: AdbController = adb_controller
        self._image_controller: ImageController = image_controller

        self.bluestacks_state.register_handler(
            BluestacksState.LOADING, self.wait_for_load, None
        )
        self.bluestacks_state.register_handler(
            BluestacksState.READY, self._adb_controller.connect, None
        )

        logger.debug(
            f"BluestacksController initialized with the following state:\n{self.bluestacks_state}\n"
        )

    @property
    def ref_window_size(self) -> tuple[int, int] | None:
        """Gets the reference window size."""
        return self._ref_window_size

    @ref_window_size.setter
    @log_property_setter
    def ref_window_size(self, width: int | str, height: int | str) -> None:
        """Sets the reference window size.

        Args:
            width: Width in pixels.
            height: Height in pixels.

        Raises:
            ValueError: If dimensions are invalid.
        """
        if not isinstance(width, int):
            if isinstance(width, str) and width.isdigit():
                width: int = int(width)
                if width <= 0:
                    logger.warning(
                        "ValueError while trying to set BluestacksController 'ref_window_size': Provided width must be positive integers!"
                    )
                    raise ValueError("Provided width must be positive integers")
            else:
                logger.warning(
                    "ValueError while trying to set BluestacksController 'ref_window_size': Provided width must be an integer or the string representation of an integer!"
                )
                raise ValueError(
                    "Provided width must be integer or the string representation of an integer!"
                )

        if not isinstance(height, int):
            if isinstance(height, str) and height.isdigit():
                height: int = int(height)
                if height <= 0:
                    logger.warning(
                        "ValueError while trying to set BluestacksController 'ref_window_size': Provided height must be positive integers!"
                    )
                    raise ValueError("Provided height must be positive integers")
            else:
                logger.warning(
                    "ValueError while trying to set BluestacksController 'ref_window_size': Provided height must be an integer or the string representation of an integer!"
                )
                raise ValueError(
                    "Provided height must be integer or the string representation of an integer!"
                )

        self._ref_window_size = (width, height)

    @property
    def filepath(self) -> str | None:
        """Gets the BlueStacks executable filepath."""
        return self._filepath

    @filepath.setter
    @log_property_setter
    def filepath(self, filepath: str) -> None:
        """Sets the BlueStacks executable filepath.

        Args:
            filepath: Path to HD-Player.exe.

        Raises:
            ValueError: If filepath is invalid or does not exist.
        """
        if not isinstance(filepath, str):
            logger.warning(
                "ValueError while trying to set BluestacksController 'filepath': Provided filepath must be a string!"
            )
            raise ValueError("Provided filepath must be a string")

        if not os.path.exists(filepath):
            logger.warning(
                "ValueError while trying to set BluestacksController 'filepath': Provided filepath does not exist!"
            )
            raise ValueError("Provided filepath does not exist")

        self._filepath: str = filepath

    def _autoset_filepath(self):
        """Automatically detects and sets the BlueStacks executable path."""
        logger.debug("Setting filepath...")

        # Common installation paths for BlueStacks
        search_paths = [
            # Standard Program Files locations
            os.path.join(
                os.environ.get("ProgramFiles", ""), "BlueStacks_nxt", HD_PLAYER_EXE
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""),
                "BlueStacks_nxt",
                HD_PLAYER_EXE,
            ),
            # Alternative BlueStacks versions
            os.path.join(
                os.environ.get("ProgramFiles", ""), "BlueStacks", HD_PLAYER_EXE
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""), "BlueStacks", HD_PLAYER_EXE
            ),
            # Common custom installation paths
            f"C:\\Program Files\\BlueStacks_nxt\\{HD_PLAYER_EXE}",
            f"C:\\Program Files (x86)\\BlueStacks_nxt\\{HD_PLAYER_EXE}",
            f"C:\\BlueStacks\\{HD_PLAYER_EXE}",
            f"C:\\BlueStacks_nxt\\{HD_PLAYER_EXE}",
            # Check if file exists in current directory or subdirectories
            HD_PLAYER_EXE,
        ]

        # Remove empty paths from environment variables
        search_paths = [path for path in search_paths if path and path != HD_PLAYER_EXE]

        # Add current working directory relative paths
        cwd = os.getcwd()
        search_paths.extend(
            [
                os.path.join(cwd, "BlueStacks_nxt", HD_PLAYER_EXE),
                os.path.join(cwd, "BlueStacks", HD_PLAYER_EXE),
            ]
        )

        logger.debug(f"Searching for HD-Player.exe in {len(search_paths)} locations")

        for potential_path in search_paths:
            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                self._filepath = potential_path
                logger.debug(f"HD-Player.exe filepath set to {self._filepath}.")
                return
            else:
                logger.debug(f"Checked path (does not exist): {potential_path}")

        # If we still haven't found it, try a broader search
        logger.debug("Performing broader search for HD-Player.exe...")
        try:
            for root, dirs, files in os.walk("C:\\"):
                if HD_PLAYER_EXE in files:
                    potential_path = os.path.join(root, HD_PLAYER_EXE)
                    if "bluestacks" in root.lower():
                        self._filepath = potential_path
                        logger.debug(
                            f"HD-Player.exe found via broad search: {self._filepath}"
                        )
                        return
        except Exception as e:
            logger.debug(f"Broad search failed: {e}")

        logger.error(
            "Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath."
        )
        logger.error(f"Searched paths: {search_paths}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"ProgramFiles: {os.environ.get('ProgramFiles')}")
        logger.error(f"ProgramFiles(x86): {os.environ.get('ProgramFiles(x86)')}")
        raise FileNotFoundError(
            "Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath."
        )

    def capture_loading_screen(self) -> bytes | None:
        """Captures the loading screen of BlueStacks.

        Returns:
            The loading screen image as bytes, or None if not found.
        """
        time.sleep(1.0)
        hwnd: int = win32gui.FindWindow(None, WINDOW_TITLE)
        if hwnd:
            try:
                # Restore the window if minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                # Pin the window to the foreground
                win32gui.SetWindowPos(
                    hwnd,
                    win32con.HWND_TOPMOST,
                    0,
                    0,
                    0,
                    0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
                )
                time.sleep(0.5)
                rect: tuple[int, int, int, int] = win32gui.GetWindowRect(hwnd)
                bluestacks_window_image: Image.Image = ImageGrab.grab(bbox=rect)
                time.sleep(0.5)

                # Convert image to bytes
                img_byte_arr = io.BytesIO()
                bluestacks_window_image.save(img_byte_arr, format="PNG")
                img_byte_arr = img_byte_arr.getvalue()

                # Unpin the window from the foreground
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE
                )
                logger.debug("Loading screen captured as bytes")
                return img_byte_arr
            except Exception as e:
                logger.warning(f"Error capturing loading screen: {e}")
                raise Exception(f"Error capturing loading screen: {e}")
        else:
            logger.warning("Could not find 'Bluestacks App Player' window")
            return None

    def open(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
        wait_time: int = DEFAULT_WAIT_TIME,
        timeout_s: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Opens the BlueStacks emulator.

        Args:
            max_retries: Maximum number of retries.
            wait_time: Wait time between retries.
            timeout_s: Timeout in seconds.

        Raises:
            ValueError: If BlueStacks fails to start.
            Exception: If BlueStacks window is not found.
        """
        max_retries: int = validate_and_convert_int(max_retries, "max_retries")
        wait_time: int = validate_and_convert_int(wait_time, "wait_time")
        timeout_s: int = validate_and_convert_int(timeout_s, "timeout_s")
        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED:
                logger.info("Opening Bluestacks controller...")
                if not self._filepath:
                    self._autoset_filepath()
                try:
                    os.startfile(self._filepath)
                except Exception as e:
                    logger.error(f"Failed to start Bluestacks: {e}")
                    raise ValueError(f"Failed to start Bluestacks: {e}")

                start_time: float = time.time()

                for attempt in range(max_retries):
                    is_open: bool = any(
                        p.name().lower() == HD_PLAYER_EXE.lower()
                        for p in psutil.process_iter(["name"])
                    )
                    if is_open:
                        logger.info("Bluestacks controller opened successfully.")
                        # Transition to LOADING - state handler will automatically call wait_for_load()
                        self.bluestacks_state.transition_to(BluestacksState.LOADING)
                        return

                    if time.time() - start_time > timeout_s:
                        logger.error("Timeout waiting for Bluestacks window to appear")
                        raise Exception(
                            "Timeout waiting for Bluestacks window to appear"
                        )

                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries}: Could not find Bluestacks window."
                    )
                    time.sleep(wait_time)

                logger.error(
                    f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}"
                )
                raise Exception(
                    f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}"
                )
            case BluestacksState.LOADING:
                logger.info(
                    "Bluestacks controller is already open and currently loading."
                )
                return
            case BluestacksState.READY:
                logger.info("Bluestacks controller is already open and ready.")
                return

    def wait_for_load(self, timeout_s: int = WAIT_FOR_LOAD_TIMEOUT):
        """Waits for Bluestacks to finish loading.

        Args:
            timeout_s: Maximum number of seconds to wait.

        Raises:
            TimeoutError: If loading takes longer than timeout.
        """
        logger.debug("Waiting for Bluestacks to load...")
        start_time = time.time()
        while self.bluestacks_state.current_state == BluestacksState.LOADING:
            loading_screen: tuple[int, int] | None = (
                self._image_controller.where_element(
                    pymordial_element=self.elements.bluestacks_loading_img,
                    pymordial_controller=None,
                    screenshot_img_bytes=self.capture_loading_screen(),
                )
            )

            # If loading screen is NOT found, Bluestacks is ready
            if loading_screen is None:
                logger.debug(
                    "Loading screen no longer visible - Bluestacks is ready!"
                )
                self.bluestacks_state.transition_to(BluestacksState.READY)
                return
            else:
                logger.debug("Bluestacks is still loading...")

            # Check timeout
            if time.time() - start_time > timeout_s:
                logger.error(
                    f"Timeout waiting for Bluestacks to load after {timeout_s}s"
                )
                self.bluestacks_state.transition_to(BluestacksState.READY)
                return

            time.sleep(DEFAULT_WAIT_TIME)

        logger.info("Bluestacks is loaded & ready.")


    def kill_bluestacks(self) -> bool:
        """Kills the Bluestacks controller process.

        This will also close the ADB connection.

        Returns:
            True if Bluestacks was successfully killed, False otherwise.

        Raises:
            ValueError: If killing the process fails.
        """
        logger.info("Killing Bluestacks controller...")

        match self.bluestacks_state.current_state:
            case BluestacksState.CLOSED:
                logger.debug("Bluestacks is already closed.")
                return True
            case BluestacksState.LOADING | BluestacksState.READY:
                try:
                    self._adb_controller.disconnect()
                    for proc in psutil.process_iter(["pid", "name"]):
                        info = proc.info
                        if info["name"] == HD_PLAYER_EXE:
                            proc.kill()
                            proc.wait(
                                timeout=PROCESS_WAIT_TIMEOUT
                            )  # Wait for process to terminate
                            self.bluestacks_state.transition_to(BluestacksState.CLOSED)
                            logger.info("Bluestacks controller killed.")
                            return True
                    return False
                except Exception as e:
                    logger.error(f"Error in kill_bluestacks: {e}")
                    raise ValueError(f"Failed to kill Bluestacks: {e}")

    def is_ready(self) -> bool:
        """Check if BlueStacks is in READY state."""
        return self.bluestacks_state.current_state == BluestacksState.READY
