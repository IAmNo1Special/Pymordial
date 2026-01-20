from abc import ABC, abstractmethod
from enum import Enum, auto
from logging import DEBUG, basicConfig, getLogger

from pymordial.state_machine import StateMachine


class EmulatorState(Enum):
    """Enumeration of emulator states."""

    CLOSED = auto()
    LOADING = auto()
    READY = auto()

    @classmethod
    def get_transitions(cls) -> dict[Enum, list[Enum]]:
        """Define valid state transitions for the emulator state machine.

        Returns:
            A dictionary mapping current states to their allowed next states.
        """
        return {
            cls.CLOSED: [cls.LOADING],
            cls.LOADING: [cls.CLOSED, cls.READY],
            cls.READY: [cls.CLOSED, cls.LOADING],
        }


class PymordialEmulatorDevice(ABC):
    """Interface for emulators."""

    logger = getLogger("PymordialEmulatorDevice")
    state = StateMachine(
        current_state=EmulatorState.CLOSED,
        transitions=EmulatorState.get_transitions(),
    )
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
