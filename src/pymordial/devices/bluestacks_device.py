"""Controller for managing the BlueStacks emulator."""

import copy
import os
import time
from logging import DEBUG, basicConfig, getLogger

import psutil

from pymordial.core.app import PymordialApp
from pymordial.core.blueprints.emulator_device import (EmulatorState,
                                                       PymordialEmulatorDevice)
from pymordial.core.blueprints.vision_device import PymordialVisionDevice
from pymordial.devices.adb_device import PymordialAdbDevice
from pymordial.utils import log_property_setter, validate_and_convert_int
from pymordial.utils.config import BluestacksConfig, get_config


class PymordialBluestacksDevice(PymordialEmulatorDevice):
    """Controls the BlueStacks emulator.

    Attributes:
        running_apps: A list of currently running PymordialApp instances.
        state: The state machine managing the BlueStacks lifecycle state.
        elements: A container for BlueStacks UI elements.
        config: The configuration dictionary for BlueStacks.
    """

    def __init__(
        self,
        adb_bridge_device: PymordialAdbDevice,
        vision_device: PymordialVisionDevice,
        config: BluestacksConfig | None = None,
    ) -> None:
        """Initializes the PymordialBluestacksDevice.

        Args:
            adb_bridge_device: The bridge device (e.g. PymordialAdbDevice) used for
                low-level ADB interactions.
            vision_device: The vision device used for screen analysis.
            config: A TypedDict containing BlueStacks configuration options.
                Defaults to package defaults if None.
        """
        self.logger = getLogger("PymordialBluestacksDevice")
        basicConfig(
            level=DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger.info("Initializing PymordialBluestacksDevice...")
        self.config = copy.deepcopy(config or get_config()["bluestacks"])
        self.running_apps: list[PymordialApp] | list = list()

        self._adb_bridge_device: PymordialAdbDevice = adb_bridge_device
        self._vision_device: PymordialVisionDevice = vision_device
        self._ref_window_size: tuple[int, int] = tuple(
            self.config["default_resolution"]
        )
        self._filepath: str | None = None
        self._hd_player_exe: str = self.config["hd_player_exe"]

        self.state.register_handler(EmulatorState.LOADING, self.wait_for_load, None)
        self.state.register_handler(
            EmulatorState.READY, self._adb_bridge_device.connect, None
        )

        self._autoset_filepath()

        self.logger.debug(
            f"PymordialBluestacksDevice initialized with the following state:\n{self.state}\n"
        )

    @property
    def ref_window_size(self) -> tuple[int, int] | None:
        """Gets the reference window size.

        Returns:
            A tuple containing (width, height) in pixels, or None if not set.
        """
        return self._ref_window_size

    @ref_window_size.setter
    @log_property_setter
    def ref_window_size(self, width_height: tuple[int | str, int | str]) -> None:
        """Sets the reference window size.

        Args:
            width_height: A tuple containing (width, height) in pixels. Values
                can be integers or string representations of integers.

        Raises:
            ValueError: If the provided width or height are not integers (or
                strings representing integers), or if they are not positive.
        """
        width = width_height[0]
        height = width_height[1]
        if not isinstance(width, int):
            if isinstance(width, str) and width.isdigit():
                width: int = int(width)
                if width <= 0:
                    self.logger.warning(
                        "ValueError while trying to set PymordialBluestacksDevice 'ref_window_size': Provided width must be positive integers!"
                    )
                    raise ValueError("Provided width must be positive integers")
            else:
                self.logger.warning(
                    "ValueError while trying to set PymordialBluestacksDevice 'ref_window_size': Provided width must be an integer or the string representation of an integer!"
                )
                raise ValueError(
                    "Provided width must be integer or the string representation of an integer!"
                )

        if not isinstance(height, int):
            if isinstance(height, str) and height.isdigit():
                height: int = int(height)
                if height <= 0:
                    self.logger.warning(
                        "ValueError while trying to set PymordialBluestacksDevice 'ref_window_size': Provided height must be positive integers!"
                    )
                    raise ValueError("Provided height must be positive integers")
            else:
                self.logger.warning(
                    "ValueError while trying to set PymordialBluestacksDevice 'ref_window_size': Provided height must be an integer or the string representation of an integer!"
                )
                raise ValueError(
                    "Provided height must be integer or the string representation of an integer!"
                )

        self._ref_window_size = (width, height)

    @property
    def filepath(self) -> str | None:
        """Gets the BlueStacks executable filepath.

        Returns:
            The absolute path to the HD-Player.exe file as a string, or None
            if it has not been determined.
        """
        return self._filepath

    @filepath.setter
    @log_property_setter
    def filepath(self, filepath: str) -> None:
        """Sets the BlueStacks executable filepath.

        Args:
            filepath: The absolute path to HD-Player.exe.

        Raises:
            ValueError: If the provided filepath is not a string or if the path
                does not exist on the filesystem.
        """
        if not isinstance(filepath, str):
            self.logger.warning(
                "ValueError while trying to set PymordialBluestacksDevice 'filepath': Provided filepath must be a string!"
            )
            raise ValueError("Provided filepath must be a string")

        if not os.path.exists(filepath):
            self.logger.warning(
                "ValueError while trying to set PymordialBluestacksDevice 'filepath': Provided filepath does not exist!"
            )
            raise ValueError("Provided filepath does not exist")

        self._filepath: str = filepath

    def open(
        self,
        max_retries: int | None = None,
        wait_time: int | None = None,
        timeout_s: int | None = None,
    ) -> None:
        """Opens the BlueStacks emulator application.

        Args:
            max_retries: The maximum number of attempts to detect the process
                after launching. Defaults to the configuration value.
            wait_time: The time in seconds to wait between detection attempts.
                Defaults to the configuration value.
            timeout_s: The maximum total time in seconds to wait for the process
                to appear before timing out. Defaults to the configuration value.

        Raises:
            ValueError: If BlueStacks fails to start due to an OS error.
            Exception: If the BlueStacks process window is not found after the
                specified retries or timeout period.
        """
        max_retries: int = validate_and_convert_int(
            max_retries or self.config["default_open_app_max_retries"], "max_retries"
        )
        wait_time: int = validate_and_convert_int(
            wait_time or self.config["default_open_app_wait_time"], "wait_time"
        )
        timeout_s: int = validate_and_convert_int(
            timeout_s or self.config["default_open_app_timeout"], "timeout_s"
        )
        match self.state.current_state:
            case EmulatorState.CLOSED:
                self.logger.info("Opening Bluestacks controller...")
                if not self._filepath:
                    self._autoset_filepath()
                try:
                    os.startfile(self._filepath)
                except Exception as e:
                    self.logger.error(f"Failed to start Bluestacks: {e}")
                    raise ValueError(f"Failed to start Bluestacks: {e}")

                start_time: float = time.time()

                for attempt in range(max_retries):
                    is_open: bool = any(
                        p.name().lower() == self._hd_player_exe.lower()
                        for p in psutil.process_iter(["name"])
                    )
                    if is_open:
                        self.logger.info("Bluestacks controller opened successfully.")
                        # Transition to LOADING - state handler will automatically call wait_for_load()
                        self.state.transition_to(EmulatorState.LOADING)
                        return

                    if time.time() - start_time > timeout_s:
                        self.logger.error(
                            "Timeout waiting for Bluestacks window to appear"
                        )
                        raise Exception(
                            "Timeout waiting for Bluestacks window to appear"
                        )

                    self.logger.warning(
                        f"Attempt {attempt + 1}/{max_retries}: Could not find Bluestacks window."
                    )
                    time.sleep(wait_time)

                self.logger.error(
                    f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}"
                )
                raise Exception(
                    f"Failed to find Bluestacks window after all attempts {attempt + 1}/{max_retries}"
                )
            case EmulatorState.LOADING:
                self.logger.info(
                    "Bluestacks controller is already open and currently loading."
                )
                return
            case EmulatorState.READY:
                self.logger.info("Bluestacks controller is already open and ready.")
                return

    def open_settings(self) -> bool:
        """Opens the Settings app using a verified activity name.

        Returns:
            True if opened successfully, False otherwise.
        """
        # Based on manual verification:
        # package: com.bluestacks.settings
        # activity: .SettingsActivity
        self.logger.info("Opening Settings...")
        return self._adb_bridge_device.open_app(
            "settings", package_name="com.bluestacks.settings"
        )

    def wait_for_load(self, timeout_s: int | None = None) -> None:
        """Waits for Bluestacks to finish loading by polling the ADB connection.

        This method blocks until the emulator is responsive via ADB or the
        timeout is reached.

        Args:
            timeout_s: The maximum number of seconds to wait for the emulator
                to load. Defaults to the configuration value.
        """
        self.logger.debug("Waiting for Bluestacks to load (ADB check)...")
        start_time = time.time()
        timeout_s = timeout_s or self.config["default_load_timeout"]

        while self.state.current_state == EmulatorState.LOADING:
            # Try to connect to ADB
            if self._adb_bridge_device.connect():
                default_ui_load_wait_time: int = self.config[
                    "default_ui_load_wait_time"
                ]
                self.logger.debug(
                    f"Waiting {default_ui_load_wait_time} seconds for UI to stabilize..."
                )
                time.sleep(default_ui_load_wait_time)
                self.logger.info("Bluestacks is loaded & ready.")
                self.state.transition_to(EmulatorState.READY)
                return

            # Check timeout
            if time.time() - start_time > timeout_s:
                self.logger.error(
                    f"Timeout waiting for Bluestacks to load after {timeout_s} seconds."
                )
                # We transition to READY anyway to allow retry logic elsewhere if needed,
                # or maybe we should raise? For now, mimicking previous behavior.
                self.state.transition_to(EmulatorState.READY)
                return

            time.sleep(self.config["default_load_wait_time"])

    def is_ready(self) -> bool:
        """Checks if BlueStacks is in the READY state.

        Returns:
            True if the current state is EmulatorState.READY, False otherwise.
        """
        return self.state.current_state == EmulatorState.READY

    def close(self) -> bool:
        """Kills the Bluestacks controller process.

        This will also disconnect the ADB bridge device.

        Returns:
            True if the Bluestacks process was found and killed, or if no
            process was found running. False if the process was found but
            could not be killed.

        Raises:
            ValueError: If an unexpected error occurs during the process
                killing routine.
        """
        self.logger.info("Killing Bluestacks controller...")

        try:
            process_found = False
            for proc in psutil.process_iter(["pid", "name"]):
                if proc.info["name"] == self._hd_player_exe:
                    process_found = True
                    try:
                        self._adb_bridge_device.disconnect()
                    except Exception as e:
                        self.logger.warning(
                            f"Error in close method while trying to disconnect adb bridge: {e}\nContinuing to close the Bluestacks process..."
                        )
                    try:
                        proc.kill()
                        proc.wait(timeout=self.config["default_process_kill_timeout"])
                    except (
                        psutil.NoSuchProcess,
                        psutil.AccessDenied,
                        psutil.ZombieProcess,
                    ):
                        return False

            if not process_found:
                self.logger.debug("Bluestacks process was not found.")
                return False

            if self.state.current_state != EmulatorState.CLOSED:
                self.state.transition_to(EmulatorState.CLOSED)

            self.logger.info("Bluestacks process killed.")
            return True

        except Exception as e:
            self.logger.error(f"Error in close: {e}")
            raise ValueError(f"Failed to kill Bluestacks: {e}")

    def _autoset_filepath(self) -> None:
        """Automatically detects and sets the BlueStacks executable path.

        This method attempts to locate `HD-Player.exe` by searching:
        1. Standard "Program Files" locations.
        2. Common custom installation paths.
        3. The current working directory.
        4. A broad walk of the C: drive (if initial checks fail).

        Raises:
            FileNotFoundError: If `HD-Player.exe` cannot be located automatically
                in any of the searched locations.
        """
        self.logger.debug("Setting filepath...")

        # Common installation paths for BlueStacks
        search_paths = [
            # Standard Program Files locations
            os.path.join(
                os.environ.get("ProgramFiles", ""),
                "BlueStacks_nxt",
                self._hd_player_exe,
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""),
                "BlueStacks_nxt",
                self._hd_player_exe,
            ),
            # Alternative BlueStacks versions
            os.path.join(
                os.environ.get("ProgramFiles", ""), "BlueStacks", self._hd_player_exe
            ),
            os.path.join(
                os.environ.get("ProgramFiles(x86)", ""),
                "BlueStacks",
                self._hd_player_exe,
            ),
            # Common custom installation paths
            f"C:\\Program Files\\BlueStacks_nxt\\{self._hd_player_exe}",
            f"C:\\Program Files (x86)\\BlueStacks_nxt\\{self._hd_player_exe}",
            f"C:\\BlueStacks\\{self._hd_player_exe}",
            f"C:\\BlueStacks_nxt\\{self._hd_player_exe}",
            # Check if file exists in current directory or subdirectories
            self._hd_player_exe,
        ]

        # Remove empty paths from environment variables
        search_paths = [
            path for path in search_paths if path and path != self._hd_player_exe
        ]

        # Add current working directory relative paths
        cwd = os.getcwd()
        search_paths.extend(
            [
                os.path.join(cwd, "BlueStacks_nxt", self._hd_player_exe),
                os.path.join(cwd, "BlueStacks", self._hd_player_exe),
            ]
        )

        self.logger.debug(
            f"Searching for HD-Player.exe in {len(search_paths)} locations"
        )

        for potential_path in search_paths:
            if os.path.exists(potential_path) and os.path.isfile(potential_path):
                self._filepath = potential_path
                self.logger.debug(f"HD-Player.exe filepath set to {self._filepath}.")
                return
            else:
                self.logger.debug(f"Checked path (does not exist): {potential_path}")

        # If we still haven't found it, try a broader search
        self.logger.debug("Performing broader search for HD-Player.exe...")
        try:
            for root, dirs, files in os.walk("C:\\"):
                if self._hd_player_exe in files:
                    potential_path = os.path.join(root, self._hd_player_exe)
                    if "bluestacks" in root.lower():
                        self._filepath = potential_path
                        self.logger.debug(
                            f"HD-Player.exe found via broad search: {self._filepath}"
                        )
                        return
        except Exception as e:
            self.logger.debug(f"Broad search failed: {e}")

        self.logger.error(
            "Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath."
        )
        self.logger.error(f"Searched paths: {search_paths}")
        self.logger.error(f"Current working directory: {os.getcwd()}")
        self.logger.error(f"ProgramFiles: {os.environ.get('ProgramFiles')}")
        self.logger.error(f"ProgramFiles(x86): {os.environ.get('ProgramFiles(x86)')}")
        raise FileNotFoundError(
            "Could not find HD-Player.exe. Please ensure BlueStacks is installed or manually specify the filepath."
        )


if __name__ == "__main__":
    from pymordial.devices.adb_device import PymordialAdbDevice
    from pymordial.devices.ui_device import PymordialUiDevice

    adb_bridge_device = PymordialAdbDevice(host="127.0.0.1", port=5555)
    vision_device = PymordialUiDevice(bridge_device=adb_bridge_device)
    device = PymordialBluestacksDevice(
        adb_bridge_device=adb_bridge_device, vision_device=vision_device
    )
    device.open()
    if device.is_ready():
        device.close()
    else:
        print("Main Function: BlueStacks is not ready.")
