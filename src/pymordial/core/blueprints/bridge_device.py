import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PymordialBridgeDevice(ABC):
    """Abstract base class for device bridges (e.g., ADB, Win32).

    Defines the low-level commands to control the device hardware or emulator.
    """

    @abstractmethod
    def connect(self):
        """Connects to the device bridge."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnects from the device bridge."""
        pass

    @abstractmethod
    def run_command(self):
        """Executes a raw shell command on the device."""
        pass

    @abstractmethod
    def open_app(self):
        """Opens an application on the device."""
        pass

    @abstractmethod
    def is_app_running(self):
        """Checks if an application is currently running."""
        pass

    @abstractmethod
    def show_recent_apps(self):
        """Shows the recent apps overview."""
        pass

    @abstractmethod
    def close_app(self):
        """Closes an application on the device."""
        pass

    @abstractmethod
    def tap(self):
        """Simulates a tap/click event."""
        pass

    @abstractmethod
    def type_text(self):
        """Simulates text input."""
        pass

    @abstractmethod
    def go_home(self):
        """Simulates pressing the Home button."""
        pass

    @abstractmethod
    def press_enter(self):
        """Simulates pressing the Enter key."""
        pass

    @abstractmethod
    def press_esc(self):
        """Simulates pressing the Escape/Back key."""
        pass

    @abstractmethod
    def capture_screenshot(self):
        """Captures a single frame from the device."""
        pass

    @abstractmethod
    def start_stream(self):
        """Starts a persistent video/screen stream."""
        pass

    @abstractmethod
    def stop_stream(self):
        """Stops the persistent video/screen stream."""
        pass

    @abstractmethod
    def get_latest_frame(self):
        """Retrieves the most recent frame from the stream."""
        pass
