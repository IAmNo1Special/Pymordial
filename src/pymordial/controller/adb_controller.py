"""Controller for ADB interactions."""

import logging
import queue
import sys
import threading
import time

import av
import numpy as np
from adb_shell.adb_device import AdbDeviceTcp

from pymordial.core.pymordial_app import PymordialApp
from pymordial.utils.config import get_config

_CONFIG = get_config()

# --- ADB Configuration ---
DEFAULT_IP = _CONFIG["adb"]["default_ip"]
DEFAULT_PORT = _CONFIG["adb"]["default_port"]
DEFAULT_TIMEOUT = _CONFIG["adb"]["default_timeout"]
DEFAULT_WAIT_TIME = _CONFIG["adb"]["default_wait_time"]

# --- Stream Configuration ---
STREAM_RESOLUTION = _CONFIG["adb"]["stream"]["resolution"]
STREAM_BITRATE = _CONFIG["adb"]["stream"]["bitrate"]
STREAM_TIME_LIMIT = _CONFIG["adb"]["stream"]["time_limit"]
STREAM_QUEUE_SIZE = _CONFIG["adb"]["stream"]["queue_size"]
STREAM_READ_TIMEOUT = _CONFIG["adb"]["stream"]["read_timeout"]
STREAM_START_TIMEOUT_ITERATIONS = _CONFIG["adb"]["stream"]["start_timeout_iterations"]
STREAM_START_WAIT = _CONFIG["adb"]["stream"]["start_wait"]
STOP_STREAM_TIMEOUT = _CONFIG["adb"]["stream"]["stop_timeout"]

# --- Monkey Configuration ---
MONKEY_VERBOSITY = _CONFIG["adb"]["monkey_verbosity"]

# --- App Check Configuration ---
APP_CHECK_RETRIES = _CONFIG["adb"]["app_check_retries"]

# --- Key Events ---
KEYEVENT_HOME = _CONFIG["adb"]["keyevents"]["home"]
KEYEVENT_ENTER = _CONFIG["adb"]["keyevents"]["enter"]
KEYEVENT_ESC = _CONFIG["adb"]["keyevents"]["esc"]
KEYEVENT_APP_SWITCH = _CONFIG["adb"]["keyevents"]["app_switch"]

# --- ADB Commands ---
CMD_SCREENRECORD = _CONFIG["adb"]["commands"]["screenrecord"]
CMD_DUMPSYS_FOCUS = _CONFIG["adb"]["commands"]["dumpsys_focus"]
CMD_FORCE_STOP = _CONFIG["adb"]["commands"]["force_stop"]
CMD_SCREENCAP = _CONFIG["adb"]["commands"]["screencap"]
CMD_TAP = _CONFIG["adb"]["commands"]["tap"]
CMD_TEXT = _CONFIG["adb"]["commands"]["text"]
CMD_KEYEVENT = _CONFIG["adb"]["commands"]["keyevent"]
CMD_MONKEY = _CONFIG["adb"]["commands"]["monkey"]


class AdbController:
    """Handles device connection and all low-level ADB commands using adb-shell.

    Attributes:
        host: ADB server host.
        port: ADB server port.
        timeout: ADB command timeout.
        device: The connected AdbDeviceTcp instance.
    """

    logger = logging.getLogger(__name__)

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        timeout: int | None = None,
    ):
        """Initializes the AdbController.

        Args:
            host: ADB server host. Defaults to config value.
            port: ADB server port. Defaults to config value.
            timeout: ADB command timeout. Defaults to config value.
        """
        self.host = host or DEFAULT_IP
        self.port = port or DEFAULT_PORT
        self.timeout = timeout or DEFAULT_TIMEOUT
        self.device: AdbDeviceTcp | None = None

        # Streaming attributes
        self._stream_thread: threading.Thread | None = None
        self._latest_frame: np.ndarray | None = None
        self._is_streaming = threading.Event()

    def connect(self) -> bool:
        """Establishes the TCP connection to the ADB service.

        Returns:
            True if connected successfully, False otherwise.
        """
        self.logger.debug(f"Connecting to ADB at {self.host}:{self.port}...")

        match self.device:
            case None:
                self.logger.debug(
                    "ADB device not initialized. Attempting to initialize ADB device..."
                )
                self.device = AdbDeviceTcp(self.host, self.port)
        match self.device.available:
            case True:
                self.logger.debug("ADB device connected.")
                return True
            case False:
                self.logger.debug(
                    "ADB device not connected. Attempting to connect ADB device..."
                )

                try:
                    self.device.connect()
                    self.logger.debug("ADB connection successful.")
                    return True
                except Exception as e:
                    self.logger.warning(f"Error connecting to ADB: {e}")
                    self.device = None
                    return False

    def disconnect(self) -> bool:
        """Disconnects the ADB device.

        Returns:
            True if disconnected successfully, False otherwise.
        """
        self.stop_stream()  # Stop streaming if active
        self.logger.debug("Disconnecting ADB device...")
        match self.device:
            case None:
                self.logger.debug("ADB device not initialized.")
                return True
            case _:
                match self.device.available:
                    case True:
                        self.logger.debug(
                            "ADB device is connected. Attempting to disconnect ADB device..."
                        )
                        self.device.close()
                        match self.device.available:
                            case True:
                                self.logger.debug("ADB device not disconnected.")
                                return False
                            case False:
                                self.logger.debug("ADB device disconnected.")
                                return True
                    case False:
                        return True

    def is_connected(self) -> bool:
        """Checks if the ADB device is connected.

        Returns:
            True if connected, False otherwise.
        """
        match self.device:
            case None:
                self.logger.debug("ADB device not initialized.")
                return False
            case _:
                match self.device.available:
                    case True:
                        self.logger.debug("ADB device connected.")
                        return True
                    case False:
                        self.logger.debug("ADB device not connected.")
                        return False

    def start_stream(
        self, width: int = 1920, height: int = 1080, bitrate: str = STREAM_BITRATE
    ) -> bool:
        """Starts screen streaming using adb-shell's streaming_shell with PyAV decoding.

        Args:
            width: Stream width.
            height: Stream height.
            bitrate: Stream bitrate.

        Returns:
            True if stream started successfully, False otherwise.
        """
        if self._is_streaming.is_set():
            self.logger.debug("Stream already running")
            return True

        if not self.is_connected():
            self.logger.error("Cannot start stream: not connected")
            return False

        self._is_streaming.set()
        command = f"screenrecord --output-format=h264 --size {width}x{height} --bit-rate {bitrate} --time-limit {STREAM_TIME_LIMIT} -"

        # Queue-based file-like object for PyAV
        class StreamReader:
            """File-like object that reads from a queue."""

            def __init__(self):
                self.queue = queue.Queue(maxsize=STREAM_QUEUE_SIZE)
                self.buffer = b""
                self.closed = False

            def read(self, size=-1):
                """Read bytes from queue."""
                while len(self.buffer) < size or size == -1:
                    try:
                        chunk = self.queue.get(timeout=STREAM_READ_TIMEOUT)
                        if chunk is None:  # End signal
                            break
                        self.buffer += chunk
                        if size == -1 and len(self.buffer) > 0:
                            break
                    except queue.Empty:
                        if self.closed:
                            break
                        continue

                if size == -1 or size > len(self.buffer):
                    result = self.buffer
                    self.buffer = b""
                else:
                    result = self.buffer[:size]
                    self.buffer = self.buffer[size:]
                return result

            def readable(self):
                return True

            def close(self):
                self.closed = True

        stream_reader = StreamReader()

        def stream_worker():
            """Worker thread that reads H264 stream and decodes with PyAV."""
            try:
                # Start streaming shell
                stream_gen = self.device.streaming_shell(command, decode=False)

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

        self._stream_thread = threading.Thread(target=stream_worker, daemon=True)
        self._stream_thread.start()

        # Wait for first frame
        for _ in range(STREAM_START_TIMEOUT_ITERATIONS):  # 5 second timeout
            if self._latest_frame is not None:
                self.logger.info("Stream started successfully")
                return True
            time.sleep(STREAM_START_WAIT)

        self.logger.error("Stream timeout: no frames")
        self.stop_stream()
        return False

    def stop_stream(self) -> None:
        """Stops the screen stream."""
        if not self._is_streaming.is_set():
            return
        self.logger.info("Stopping stream...")
        self._is_streaming.clear()
        if self._stream_thread and self._stream_thread.is_alive():
            self._stream_thread.join(timeout=STOP_STREAM_TIMEOUT)
        # No lock needed - assignment is atomic
        self._latest_frame = None
        self.logger.info("Stream stopped")

    def get_latest_frame(self) -> np.ndarray | None:
        """Gets the latest decoded frame from the stream.

        Returns:
            The latest frame as a numpy array (RGB), or None if no frame available.
        """
        # No lock needed - reference read is atomic in Python (GIL)
        # Copy to prevent caller from modifying the frame
        frame = self._latest_frame
        return frame.copy() if frame is not None else None

    def shell_command(self, command: str) -> bytes | None:
        """Executes a shell command and returns the output.

        Args:
            command: The command to execute.

        Returns:
            The command output as bytes, or None if not connected.
        """
        self.logger.debug(f"Executing shell command: {command}")
        if not self.device:
            self.logger.warning("Error: ADB not connected.")
            return None

        try:
            return self.device.shell(
                command,
                timeout_s=self.timeout,
                read_timeout_s=self.timeout,
                transport_timeout_s=self.timeout,
                decode=False,
            )
        except ConnectionAbortedError:
            self.logger.error("ADB connection aborted. Attempting to reconnect...")
            if self.connect():
                self.logger.info("Reconnected to ADB successfully. Retrying command...")
                try:
                    return self.device.shell(
                        command,
                        timeout_s=self.timeout,
                        read_timeout_s=self.timeout,
                        transport_timeout_s=self.timeout,
                        decode=False,
                    )
                except Exception as e:
                    self.logger.critical(
                        f"Failed to execute command after reconnection: {e}"
                    )
                    sys.exit(1)
            else:
                self.logger.critical("Failed to reconnect to ADB. Exiting program.")
                sys.exit(1)

    def tap(self, x: int, y: int) -> None:
        """Performs a simple tap at (x, y).

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        self.logger.debug(f"Tapping at ({x}, {y})")
        self.shell_command(f"input tap {x} {y}")

    def open_app(
        self,
        app: PymordialApp,
        timeout: int,
        wait_time: int,
    ) -> bool:
        """Opens an app using the PymordialApp object.

        Args:
            app: The PymordialApp object to open.
            timeout: The timeout for the ADB command.
            wait_time: The wait time between retries.

        Returns:
            True if the app is opened, False otherwise.
        """
        self.logger.debug(f"Opening app with package name: {app.package_name} ...")
        if not self.is_connected():
            self.logger.warning(
                "ADB device not initialized. Skipping 'open_app' method call."
            )
            return False
        # Wait for app to open by checking if it's running
        start_time: float = time.time()
        while time.time() - start_time < timeout:
            self.shell_command(
                f"monkey -p {app.package_name} -v {MONKEY_VERBOSITY}"
            )
            match self.is_app_running(app, max_retries=5, wait_time=wait_time):
                case True:
                    self.logger.debug(
                        f"App with package name: {app.package_name} opened via ADB"
                    )
                    return True
                case False:
                    time.sleep(wait_time)
                    continue
        # If app isn't running after timeout, raise error
        self.logger.warning(
            f"App with package name: {app.package_name} did not start within {timeout} seconds"
        )
        return False

    def is_app_running(
        self,
        app: PymordialApp,
        max_retries: int = 1,
        wait_time: int = 1,
    ) -> bool:
        """Checks if an app is running using ps command.

        This method uses 'ps -A | grep' which is fast and doesn't hang.

        Args:
            app: The PymordialApp object to check.
            max_retries: Number of times to retry (default: 1 for quick check).
                        Set higher when waiting for app to start.
            wait_time: Seconds to wait between retries.

        Returns:
            True if the app process is found, False otherwise.

        Examples:
            # Quick check if app is closed (no retries needed)
            is_running = adb.is_app_running(app)

            # Wait for app to start (with retries)
            is_running = adb.is_app_running(app, max_retries=20, wait_time=1)
        """
        if not self.is_connected():
            self.logger.warning(
                "ADB device not connected. Skipping 'is_app_running' method call."
            )
            return False

        for attempt in range(max_retries):
            try:
                # Use ps -A to list ALL processes and grep for the package name
                output: bytes | None = self.shell_command(
                    f"ps -A | grep {app.package_name}"
                )

                found = False
                if output:
                    # Parse output to ensure exact match (avoid partial matches)
                    lines = output.decode("utf-8").strip().splitlines()
                    for line in lines:
                        parts = line.split()
                        if not parts:
                            continue
                        # The process name is usually the last column
                        process_name = parts[-1]
                        if process_name == app.package_name:
                            found = True
                            break

                if found:
                    self.logger.debug(
                        f"Found {app.app_name} process (attempt {attempt + 1}/{max_retries})"
                    )
                    return True
                else:
                    if attempt < max_retries - 1:  # More retries remaining
                        self.logger.debug(
                            f"{app.app_name} process not found. Retrying... ({attempt + 1}/{max_retries})"
                        )
                        time.sleep(wait_time)
                    else:  # Last attempt
                        self.logger.debug(
                            f"{app.app_name} process not found after {max_retries} attempts"
                        )
            except Exception as e:
                # grep returns exit code 1 when no match found - this is expected
                if attempt < max_retries - 1:
                    self.logger.debug(
                        f"App process check attempt {attempt + 1} failed: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.debug(f"App process not found or error: {e}")

        return False

    def close_app(
        self,
        app: PymordialApp,
        timeout: int,
        wait_time: int,
    ) -> bool:
        """Closes an app using the PymordialApp object.

        Args:
            app: The PymordialApp object to close.
            timeout: The timeout for the ADB command.
            wait_time: The wait time between retries.

        Returns:
            True if the app is closed, False otherwise.
        """
        self.logger.debug(f"Closing app with package name: {app.package_name}...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'close_app' method call."
            )
            return False

        # Force stop the app
        self.shell_command(
            f"am force-stop {app.package_name}",
        )

        # Wait a moment for the app to close
        time.sleep(wait_time)

        self.shell_command(f"am force-stop {app.package_name}")

        # Poll for app closure
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_app_running(app, max_retries=1, wait_time=0.1):
                self.logger.debug(
                    f"App with package name: {app.package_name} closed via ADB"
                )
                return True
            time.sleep(wait_time)

        self.logger.warning(
            f"App with package name: {app.package_name} may still be running after force stop"
        )
        return False

    def go_home(self) -> bool:
        """Navigates to the home screen.

        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug("Going to home screen...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'go_home' method call."
            )
            return False
        # Go to home screen
        self.shell_command(f"input keyevent {KEYEVENT_HOME}")
        time.sleep(DEFAULT_WAIT_TIME)
        self.logger.debug("Home screen opened via ADB")
        return True

    def capture_screenshot(self) -> bytes | None:
        """Captures a screenshot of the device.

        Returns:
            The screenshot as bytes, or None if failed.
        """
        self.logger.debug("Capturing screenshot...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'capture_screenshot' method call."
            )
            return None
        try:
            # Capture the screenshot
            screenshot_bytes: bytes | None = self.shell_command(CMD_SCREENCAP)
            if screenshot_bytes:
                self.logger.debug("Screenshot captured successfully")
                return screenshot_bytes
            return None
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
            return None

    def type_text(self, text: str) -> bool:
        """Types text on the device.

        Args:
            text: The text to type.

        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug(f"Typing text: {text} ...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'type_text' method call."
            )
            return False
        # Send the text using ADB
        self.shell_command(f"input text {text}")
        self.logger.debug(f"Text '{text}' sent via ADB")
        return True

    def press_enter(self) -> bool:
        """Presses the Enter key.

        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug("Pressing enter key...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'press_enter' method call."
            )
            return False
        # Send the enter key using ADB
        self.shell_command(f"input keyevent {KEYEVENT_ENTER}")
        self.logger.debug("Enter key sent via ADB")
        return True

    def press_esc(self) -> bool:
        """Presses the Esc key.

        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug("Pressing esc key...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'press_esc' method call."
            )
            return False
        # Send the esc key using ADB
        self.shell_command(f"input keyevent {KEYEVENT_ESC}")
        self.logger.debug("Esc key sent via ADB")
        return True

    def show_recent_apps(self) -> bool:
        """Shows the recent apps drawer.

        Returns:
            True if successful, False otherwise.
        """
        self.logger.debug("Showing recent apps...")
        if not self.device or not self.device.available:
            self.logger.warning(
                "ADB device not initialized. Skipping 'show_recent_apps' method call."
            )
            return False
        self.shell_command(f"input keyevent {KEYEVENT_APP_SWITCH}")
        self.logger.debug("Recent apps drawer successfully opened")
        return True

    def __repr__(self) -> str:
        """Returns a string representation of the AdbController."""
        return (
            f"AdbController("
            f"ip='{self.ip}', "
            f"port={self.port}, "
            f"connected={self.is_connected()}, "
            f"streaming={self._streaming})"
        )
