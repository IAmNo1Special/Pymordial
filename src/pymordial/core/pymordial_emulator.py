from abc import ABC, abstractmethod
from logging import DEBUG, basicConfig, getLogger


class PymordialEmulatorDevice(ABC):
    """Interface for emulators."""

    logger = getLogger("PymordialEmulatorDevice")
    basicConfig(
        level=DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    @abstractmethod
    def open(self):
        """Opens the emulator."""
        pass

    @abstractmethod
    def wait_for_load(self):
        """Waits for the emulator to load."""
        pass

    @abstractmethod
    def is_ready(self):
        """Checks if the emulator is ready."""
        pass

    @abstractmethod
    def close(self):
        """Closes the emulator."""
        pass

    