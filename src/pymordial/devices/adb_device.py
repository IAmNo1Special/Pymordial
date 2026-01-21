"""Controller for ADB interactions."""

from __future__ import annotations

import copy
import os
import threading
from logging import DEBUG, WARNING, basicConfig, getLogger
from time import sleep, time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymordial.core.app import PymordialApp
    from pymordial.utils.config import PymordialConfig

from io import BytesIO

import av
import numpy as np
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from PIL import Image

from pymordial.core.blueprints.bridge_device import PymordialBridgeDevice
from pymordial.utils import PymordialStreamReader
from pymordial.utils.config import AdbConfig, get_config


class PymordialAdbDevice(PymordialBridgeDevice):
    """Handles Android device communication using adb-shell.

    Configuration is loaded from default settings but can be overridden
    per instance by modifying the instance attributes after initialization.

    Attributes:
        name (str): The plugin name ("adb").
        version (str): The plugin version.
        host (str): The address of the device; may be an IP address or a host name.
        port (int): The device port to which we are connecting
        device (AdbDeviceTcp): The adb_shell.AdbDeviceTcp instance.
        config (AdbConfig): The configuration dictionary.
    """

    name: str = "adb"
    version: str = "0.1.0"

    # DEFAULT_CONFIG will be fetched in __init__ if not provided
    # to allow easier testing and dynamic configuration updates.

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        config: AdbConfig | None = None,
        adbshell_log_level: int = WARNING,
    ):
        """Initalizes PymordialAdbDevice.

        Args:
            host: The address of the device; may be an IP address or a host name.
            port: The device port to which we are connecting.
            config: A TypedDict containing ADB configuration. Defaults to package defaults.
            adbshell_log_level: The log level for adb-shell (e.g. logging.WARNING).
        """
        self.logger = getLogger("PymordialAdbDevice")
        basicConfig(
            level=DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        self.logger.debug("Initalizing PymordialAdbDevice...")
        self.config = copy.deepcopy(config or get_config()["adb"])
        self.host: str = host or self.config["default_host"]
        self.port: int = port or self.config["default_port"]

        getLogger("adb_shell").setLevel(
            adbshell_log_level
        )  # Silence adb_shell debug logs

        self._device: AdbDeviceTcp | None = None

        # Streaming attributes
        self._stream_thread: threading.Thread | None = None
        self._latest_frame: np.ndarray | None = None
        self._is_streaming = threading.Event()
        self.logger.debug("PymordialAdbDevice initalized.")

    def initialize(self, config: "PymordialConfig") -> None:
        """Initializes the ADB device plugin.

        Args:
            config: Global Pymordial configuration dictionary.
        """
        # In a full comprehensive implementation, we might reload config here.
        # For now, we rely on __init__ logic or manual property updates.
        pass

    def shutdown(self) -> None:
        """Disconnects and cleans up resources."""
        self.disconnect()

    @property
    def is_streaming(self) -> bool:
        """Check if streaming is currently active.

        Returns:
            True if streaming is active, False otherwise.
        """
        return self._is_streaming.is_set()

    def find_package_by_keyword(self, keyword) -> str | None:
        self.logger.debug("Finding package by keyword...")
        # 'pm list packages' returns 'package:com.name.app'
        # We strip 'package:' and filter for your keyword
        output = self.run_command("pm list packages", decode=True)
        if output:
            packages = [
                line.replace("package:", "").strip() for line in output.splitlines()
            ]
            # 1. Try exact match
            if keyword in packages:
                self.logger.debug(f"Exact package match found: {keyword}")
                return keyword
            # 2. Try case-insensitive partial match
            matches = [pkg for pkg in packages if keyword.lower() in pkg.lower()]
            if matches:
                # Return the shortest match (best fit for keyword)
                best_match = min(matches, key=len)
                self.logger.debug(
                    f"Partial package match found: {best_match} (best of {len(matches)} matches)"
                )
                return best_match
        self.logger.debug(f"No package found matching '{keyword}'")
        return None

    def get_launch_activity(self, package_name) -> str | None:
        self.logger.debug("Getting launch activity...")
        # This command queries the system for the EXACT entry point
        cmd = f"cmd package resolve-activity --brief {package_name}"
        # MUST decode to string to avoid b'...' in f-string later
        output = self.run_command(cmd, decode=True)

        if not output:
            return None

        # Standard output is usually the package/activity on the last line
        lines = output.strip().splitlines()
        if lines:
            activity = lines[-1].strip()
            if "/" not in activity or "No activity found" in activity:
                self.logger.debug(f"No valid activity found for {package_name}")
                return None

            self.logger.debug(f"Launch activity found: {activity}")
            return activity

        self.logger.debug("Launch activity not found.")
        return None

    def connect(self) -> bool:
        self.logger.debug(f"Connecting to ADB at {self.host}:{self.port}...")

        if self._device is None:
            self.logger.debug(
                "PymordialAdbDevice device not initialized. Attempting to initialize..."
            )
            self._device = self._create_adb_device()

        if self._device.available:
            self.logger.debug("PymordialAdbDevice device already connected.")
            return True

        self.logger.debug(
            "PymordialAdbDevice device not connected. Attempting to connect..."
        )
        try:
            self._device.connect(rsa_keys=self._get_adb_signer())
            self.logger.debug("PymordialAdbDevice device connection successful.")
            return True
        except Exception as e:
            self.logger.warning(f"Error connecting to PymordialAdbDevice device: {e}")
            self._device = None
            return False

    def is_connected(self) -> bool:
        """Checks if PymordialAdbDevice device is connected.

        Returns:
            True if the device is connected, False otherwise.
        """
        self.logger.debug("Checking if PymordialAdbDevice device is connected...")
        if self._device is None:
            self.logger.debug(
                "PymordialAdbDevice device not initialized. Use connect() method to initialize."
            )
            return False
        if not self._device.available:
            self.logger.debug("PymordialAdbDevice device not connected.")
            return False
        self.logger.debug("PymordialAdbDevice device connected.")
        return True

    def disconnect(self) -> bool:
        """Disconnects the PymordialAdbDevice device.

        Returns:
            True if disconnected (or already disconnected), False on error.
        """
        self.logger.debug("Disconnecting from PymordialAdbDevice device...")
        self.stop_stream()  # Stop streaming if active

        if self._device is None or not self._device.available:
            return True

        try:
            self._device.close()
            if not self._device.available:
                self.logger.debug("Disconnected from PymordialAdbDevice device.")
                return True
            self.logger.debug("Failed to disconnect from PymordialAdbDevice device.")
            return False
        except Exception as e:
            self.logger.error(
                f"Error disconnecting from PymordialAdbDevice device: {e}"
            )
            return False

    def run_command(self, command: str, decode: bool = False) -> bytes | None:
        """Executes a shell command and returns the output.

        Args:
            command: The command to execute.

        Returns:
            The command output as bytes, or None if not connected.
        """
        self.logger.debug(f"Executing shell command: {command}...")
        try:
            output = self._device.shell(
                command,
                timeout_s=self.config["commands"]["timeout"],
                read_timeout_s=self.config["commands"]["read_timeout"],
                transport_timeout_s=self.config["commands"]["transport_timeout"],
                decode=decode,
            )
        except Exception as e:
            self.logger.error(f"Failed to execute shell command {command}: {e}")
            return None
        self.logger.debug(f"Shell command {command} executed successfully.")
        return output

    def get_focused_app(self) -> dict[str, str] | None:
        """Gets information about the currently focused app.

        Returns:
            A dictionary with 'package' and 'activity', or None if failed.
        """
        self.logger.debug("Getting focused app info...")
        # 'dumpsys window windows' is more reliable than just 'dumpsys window' on some Android versions
        # Look for mCurrentFocus or mFocusedApp lines
        output = self.run_command(
            "dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'", decode=True
        )
        if not output:
            return None

        # Format: mCurrentFocus=Window{... u0 com.android.settings/com.android.settings.Settings}
        # Format: mFocusedApp=AppWindowToken{... token=Token{... u0 com.example/com.example.MainActivity}}
        import re

        match = re.search(r"([a-zA-Z0-9._]+)/([a-zA-Z0-9._$]+)", output)
        if match:
            pkg, activity = match.groups()
            self.logger.debug(f"Focused app: package={pkg}, activity={activity}")
            return {"package": pkg, "activity": activity}

        self.logger.debug("Could not parse focused app info from dumpsys")
        return None

    def open_app(
        self,
        app_name: str,
        package_name: str | None = None,
        timeout: float = 10.0,
        wait_time: float = 1.0,
    ) -> bool:
        """Opens an app by name or package, with optional verification.
        Args:
            app_name: Name/keyword to search for the package if package_name not provided.
            package_name: Optional exact package name.
            timeout: Max seconds to wait for app to start (if verify=True).
            wait_time: Seconds between verification retries.
        Returns:
            True if launched, False otherwise.
        """
        pkg = package_name or self.find_package_by_keyword(app_name)
        if not pkg:
            self.logger.error(f"Could not find package for '{app_name}'")
            return False
        # Try activity-based launch first (faster, more reliable)
        activity = self.get_launch_activity(pkg)
        if activity:
            self.run_command(f"am start -n {activity}")
            self.logger.debug(f"Launched {app_name} via Activity: {activity}")
        else:
            # Fallback to monkey
            self.logger.debug(
                f"Activity not found, using Monkey fallback for {app_name}"
            )
            self.run_command(f"monkey -p {pkg} -c android.intent.category.LAUNCHER 1")
            self.logger.debug(f"Launched {app_name} via Monkey")

        start_time = time()
        while time() - start_time < timeout:
            if self.is_app_running(pkg, max_retries=1, wait_time=0):
                self.logger.debug(f"Verified {app_name} is running")
                return True
            sleep(wait_time)
        self.logger.warning(f"{app_name} did not start within {timeout}s")
        return False

    # max_retries and wait_time default need
    # to be made into class variables
    def is_app_running(
        self,
        package_name: str | None = None,
        pymordial_app: "PymordialApp" | None = None,
        app_name: str | None = None,
        max_retries: int = 2,
        wait_time: int = 1,
    ) -> bool:
        """Checks if an app is running using pidof command.

        Args:
            package_name: Direct package name (e.g., 'com.android.settings').
            pymordial_app: PymordialApp instance to extract package from.
            app_name: App name keyword to search for.
            max_retries: Number of retries.
            wait_time: Time to wait between retries.

        Returns:
            True if running, False otherwise.

        Priority: package_name > pymordial_app > app_name.
        """
        # Handle case where PymordialApp might be passed positionally as package_name
        if package_name and not isinstance(package_name, str):
            if hasattr(package_name, "package_name"):
                pymordial_app = package_name
                package_name = None

        pkg = (
            package_name
            or (pymordial_app.package_name if pymordial_app else None)
            or (self.find_package_by_keyword(app_name) if app_name else None)
        )

        if not pkg:
            self.logger.warning(
                f"Could not resolve package for is_app_running (package_name={package_name}, "
                f"pymordial_app={pymordial_app}, app_name={app_name})"
            )
            return False

        if not self._device.available:
            self.logger.debug(
                "PymordialAdbDevice device not connected. Attempting to reconnect..."
            )
            if not self.connect():
                raise ConnectionError(
                    "PymordialAdbDevice device not connected and reconnection failed."
                )
            self.logger.debug("PymordialAdbDevice device reconnected.")

        for attempt in range(max_retries):
            try:
                output = self.run_command(f"pidof {pkg}", decode=True)
                if output and output.strip():
                    self.logger.debug(f"Found {pkg} running with PID: {output.strip()}")
                    return True
            except Exception as e:
                self.logger.debug(f"pidof check failed: {e}")

            if attempt < max_retries - 1:
                self.logger.debug(
                    f"{pkg} not found. Retrying ({attempt + 1}/{max_retries})..."
                )
                sleep(wait_time)

        self.logger.debug(f"{pkg} not found after {max_retries} attempts")
        return False

    def show_recent_apps(self) -> bool:
        """Shows the recent apps drawer.

        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug("Showing recent apps...")
        if not self._device.available:
            self.logger.debug(
                "PymordialAdbDevice device not connected. Skipping 'show_recent_apps' method call."
            )
            return False
        self.run_command(f"input keyevent {self.config['keyevents']['app_switch']}")
        self.logger.debug("Recent apps drawer successfully opened")
        return True

    def close_app(
        self,
        package_name: str | None = None,
        app_name: str | None = None,
        timeout: float = 5.0,
        wait_time: float = 0.5,
    ) -> bool:
        """Closes an app and verifies it stopped.

        Provide either package_name (exact) or app_name (keyword search).
        If both provided, package_name takes priority.

        Args:
            package_name: Exact package name (e.g., 'com.revomon.vr').
            app_name: Keyword to search for package (e.g., 'revomon').
            timeout: Max seconds to wait for app to close.
            wait_time: Seconds between verification retries.

        Returns:
            True if app is confirmed closed, False otherwise.

        Raises:
            ValueError: If neither package_name nor app_name is provided.
        """
        if package_name:
            pkg = package_name
        elif app_name:
            pkg = self.find_package_by_keyword(app_name)
            if not pkg:
                self.logger.error(f"Could not find package for '{app_name}'")
                return False
        else:
            raise ValueError("Must provide either package_name or app_name")

        self.logger.debug(f"Closing app: {pkg}")

        if not self._device.available:
            self.logger.warning("ADB not connected. Cannot close app.")
            return False

        self.run_command(f"am force-stop {pkg}")

        # Poll to confirm app closed
        start_time = time()
        while time() - start_time < timeout:
            if not self.is_app_running(pkg, max_retries=1, wait_time=0):
                self.logger.debug(f"Verified {pkg} is closed")
                return True
            sleep(wait_time)

        self.logger.warning(f"{pkg} may still be running after {timeout}s")
        return False

    def close_all_apps(self, exclude: list[str] | None = None) -> None:
        """Force stops all packages to clear the device state.

        Args:
            exclude: Optional list of package names to exclude from closing.
        """
        self.logger.debug("Closing all apps...")

        # Get list of all packages
        output = self.run_command("pm list packages", decode=True)
        if not output:
            self.logger.warning("No packages found.")
            return

        # Output format: package:com.example.app
        # run_command with decode=True returns str
        packages = [
            line.replace("package:", "").strip()
            for line in output.splitlines()
            if line.strip()
        ]
        exclude = exclude or []

        count = 0
        for pkg in packages:
            if pkg in exclude:
                continue
            self.run_command(f"am force-stop {pkg}")
            count += 1

        self.logger.debug(f"Closed {count} apps.")

    def tap(self, x: int, y: int) -> bool:
        """Performs a simple tap at (x, y).

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        self.logger.debug(f"Tapping at ({x}, {y})")
        output = self.run_command(f"input tap {x} {y}")
        if output:
            self.logger.debug(f"Tap at ({x}, {y}) successful")
            return True
        else:
            self.logger.debug(f"Tap at ({x}, {y}) failed")
            return False

    def type_text(self, text: str) -> bool:
        """Types text on the device.
        Args:
            text: The text to type.
        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug(f"Typing text: {text} ...")
        if not self._device.available:
            self.logger.debug(
                "PymordialAdbDevice device not connected. Skipping 'type_text' method call."
            )
            return False

        # Escape special characters for ADB input text
        # Spaces become %s, other special chars need escaping
        escaped_text = text.replace("\\", "\\\\")  # Escape backslashes first
        escaped_text = escaped_text.replace(" ", "%s")
        escaped_text = escaped_text.replace("'", "\\'")
        escaped_text = escaped_text.replace('"', '\\"')
        escaped_text = escaped_text.replace("&", "\\&")
        escaped_text = escaped_text.replace("<", "\\<")
        escaped_text = escaped_text.replace(">", "\\>")
        escaped_text = escaped_text.replace(";", "\\;")
        escaped_text = escaped_text.replace("|", "\\|")

        self.run_command(f"input text '{escaped_text}'")
        self.logger.debug(f"Text '{text}' sent via ADB")
        return True

    def go_home(self) -> bool:
        """Navigates to the home screen.

        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug("PymordialAdbDevice navigating to home screen...")
        if not self._device.available:
            self.logger.debug(
                "PymordialAdbDevice device not connected. Skipping 'go_home' method call."
            )
            return False
        # Go to home screen
        self.run_command(f"input keyevent {self.config['keyevents']['home']}")
        sleep(self.config["default_wait_time"])
        self.logger.debug("PymordialAdbDevice successfully navigated to home screen.")
        return True

    def capture_screenshot(self) -> bytes | None:
        """Captures a screenshot of the device.

        Returns:
            The screenshot as bytes, or None if failed.
        """
        self.logger.debug("Capturing screenshot...")
        if not self._device.available:
            self.logger.warning("ADB not connected. Skipping screenshot.")
            return None

        try:
            screenshot_bytes: bytes | None = self.run_command(
                self.config["commands"]["screencap"]
            )
            if screenshot_bytes:
                self.logger.debug("Screenshot captured successfully")
                return screenshot_bytes
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
        return None

    # width and height defaults need
    # to be made into class variables
    def start_stream(self) -> bool:
        """Starts screen streaming using adb-shell's streaming_shell with PyAV decoding.

        Automatically detects resolution from a screenshot.

        Returns:
            True if stream started successfully, False otherwise.
        """
        self.logger.debug("Starting PymordialAdbDevice stream...")
        if self._is_streaming.is_set():
            self.logger.debug("PymordialAdbDevice stream already running")
            return True

        if not self._device.available:
            self.logger.error("Cannot start stream: not connected")
            return False

        # Auto-detect resolution
        screenshot_bytes = self.capture_screenshot()
        if not screenshot_bytes:
            self.logger.error(
                "Cannot start stream: failed to capture screenshot for resolution detection"
            )
            return False

        try:
            img = Image.open(BytesIO(screenshot_bytes))
            width, height = img.size
            size_arg = f"{width}x{height}"
            self.logger.debug(f"Detected resolution: {width}x{height}")
        except Exception as e:
            self.logger.error(f"Error detecting resolution: {e}")
            return False

        self._is_streaming.set()
        command = (
            f"screenrecord --output-format=h264 "
            # f"--verbose "  <--- DELETE THIS LINE
            f"--size {size_arg} "
            f"--bit-rate {self.config['stream']['bitrate']} "
            f"--time-limit {self.config['stream']['time_limit']} "
            f"-"
        )

        stream_reader = PymordialStreamReader(
            queue_size=self.config["stream"]["queue_size"],
            read_timeout=self.config["stream"]["read_timeout"],
        )

        self._stream_thread = threading.Thread(
            target=self._stream_worker,
            args=(command, stream_reader),
            daemon=True,
        )
        self._stream_thread.start()

        # Wait for first frame
        for _ in range(self.config["stream"]["start_timeout_iterations"]):
            if self._latest_frame is not None:
                self.logger.info("PymordialAdbDevice stream started successfully")
                return True
            sleep(self.config["stream"]["start_wait"])

        self.logger.error("PymordialAdbDevice stream timeout: no frames")
        self.stop_stream()
        return False

    def stop_stream(self) -> None:
        """Stops the screen stream."""
        self.logger.debug("Stopping PymordialAdbDevice stream...")
        self._is_streaming.clear()
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=self.config["stream"]["stop_timeout"])

        # Cleanup: kill background screenrecord and remove temp file
        try:
            self.run_command("pkill -9 screenrecord")
        except Exception:
            pass  # Best effort cleanup

        self._latest_frame = None
        self.logger.debug("PymordialAdbDevice stream stopped")

    def get_latest_frame(self) -> np.ndarray | None:
        """Gets the latest decoded frame from the stream.

        Returns:
            The latest frame as a numpy array (RGB), or None if no frame available.
        """
        # No lock needed - reference read is atomic in Python (GIL)
        # Copy to prevent caller from modifying the frame
        frame = self._latest_frame
        return frame.copy() if frame is not None else None

    def capture_screen(self) -> "bytes | np.ndarray | None":
        """Captures the current BlueStacks screen using the appropriate capture strategy.

        Returns:
            The screenshot as bytes or numpy array, or None if failed.
        """

        if not self.is_connected():
            self.connect()
            if not self.is_connected():
                self.logger.warning(
                    "Cannot capture screen - ADB controller is not initialized"
                )
                return None

        # Always use streaming - start if not active
        if not self.is_streaming:
            self.logger.info("Starting stream for capture_screen...")
            if not self.start_stream():
                self.logger.error(
                    "Failed to start stream, falling back to capture_screenshot."
                )
                return self.capture_screenshot()

        frame = self.get_latest_frame()
        if frame is not None:
            # Validate frame isn't corrupted (all same color)
            if frame.std() < 1.0:  # Nearly uniform = likely corrupted
                self.logger.warning(
                    "Frame appears corrupted (uniform color), restarting stream..."
                )
                self.stop_stream()
                if self.start_stream():
                    frame = self.get_latest_frame()
                    if frame is not None and frame.std() >= 1.0:
                        self.logger.debug("Returning fresh frame after restart.")
                        return frame
                self.logger.error("Failed to get valid frame after restart")
                return self.capture_screenshot()
            self.logger.debug("Returning latest frame from stream.")
            return frame

        self.logger.warning(
            "Stream active but no frame available. Falling back to screenshot."
        )
        return self.capture_screenshot()

    def press_enter(self) -> bool:
        """Presses the Enter key.

        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug("Pressing enter key...")
        if not self._device.available:
            self.logger.debug(
                "PymordialAdbDevice device not connected. Skipping 'press_enter' method call."
            )
            return False
        self.run_command(f"input keyevent {self.config['keyevents']['enter']}")
        self.logger.debug("Enter key sent via ADB")
        return True

    def press_esc(self) -> bool:
        """Presses the Esc key.

        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug("Pressing esc key...")
        if not self._device.available:
            self.logger.debug(
                "PymordialAdbDevice device not connected. Skipping 'press_esc' method call."
            )
            return False
        # Send the esc key using ADB
        self.run_command(f"input keyevent {self.config['keyevents']['esc']}")
        self.logger.debug("Esc key sent via ADB")
        return True

    def _get_adb_signer(
        self, adbkey_path: str | None = None
    ) -> list[PythonRSASigner] | None:
        """
        Gets the ADB signer.

        Args:
            adbkey_path: Path to the ADB key. If None, uses the default location of ~/.android/adbkey.

        Returns:
            List of PythonRSASigner objects if the adb key is found, None otherwise.
        """
        try:
            self.logger.debug("Getting signer...")
            # Standard location for ADB keys on Windows
            if adbkey_path is None:
                adbkey_path: str = os.path.expanduser("~/.android/adbkey")
            if os.path.exists(adbkey_path):
                with open(adbkey_path) as f:
                    priv = f.read()
                self.logger.debug("Signer found.")
                return [PythonRSASigner("", priv)]
            self.logger.debug("Signer not found.")
            return None
        except Exception as e:
            self.logger.error(f"Error getting signer: {e}")
            return None

    def _create_adb_device(self) -> AdbDeviceTcp | None:
        self.logger.debug("Creating PymordialAdbDevice device...")
        device: AdbDeviceTcp | None = None
        try:
            device = AdbDeviceTcp(host=self.host, port=self.port)
        except Exception as e:
            self.logger.error(f"Error creating PymordialAdbDevice device: {e}")

        if device:
            self.logger.debug("PymordialAdbDevice device created.")
        else:
            self.logger.error("PymordialAdbDevice device not created.")
        return device

    def _stream_worker(
        self, command: str, stream_reader: PymordialStreamReader
    ) -> None:
        """Worker thread that reads H264 stream and decodes with PyAV."""
        self.logger.debug(f"Starting stream worker with command: {command}")
        try:
            # Start streaming shell
            stream_gen = self._device.streaming_shell(command, decode=False)

            # Feed chunks to reader in a separate thread
            def feeder():
                try:
                    for chunk in stream_gen:
                        if not self._is_streaming.is_set():
                            break
                        stream_reader.queue.put(chunk)
                except Exception as e:
                    self.logger.error(f"Feeder error: {e}")
                finally:
                    stream_reader.queue.put(None)  # End signal

            feeder_thread = threading.Thread(target=feeder, daemon=True)
            feeder_thread.start()

            # Decode with PyAV
            with av.open(stream_reader, mode="r", format="h264") as container:
                for frame in container.decode(video=0):
                    if not self._is_streaming.is_set():
                        break
                    rgb_frame = frame.to_ndarray(format="rgb24")
                    # No lock needed - assignment is atomic in Python (GIL)
                    self._latest_frame = rgb_frame

        except Exception as e:
            if self._is_streaming.is_set():
                self.logger.error(f"Stream error: {e}")
        finally:
            stream_reader.close()
            self._is_streaming.clear()
            self.logger.debug("Stream ended")


if __name__ == "__main__":
    controller = PymordialAdbDevice()
    if controller.connect():
        controller.open_app("revomon")
    else:
        print("Failed to connect to device")
