from abc import ABC, abstractmethod
from enum import Enum, auto
from logging import DEBUG, basicConfig, getLogger

from pymordial.core.state_machine import StateMachine


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
    """Abstract interface for controlling emulator software (e.g., BlueStacks).

    Attributes:
        logger: Logger instance for emulator operations.
        state: StateMachine tracking the emulator's lifecycle.
    """

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
        """Opens the emulator software.

        Returns:
            True if the launch command was successful, False otherwise.
        """
        pass

    @abstractmethod
    def wait_for_load(self):
        """Waits for the emulator to reach a ready state.

        Returns:
            True if proper loading was detected within timeout, False otherwise.
        """
        pass

    @abstractmethod
    def is_ready(self):
        """Checks if the emulator is currently ready to accept commands.

        Returns:
            True if the emulator is ready, False otherwise.
        """
        pass

    @abstractmethod
    def close(self):
        """Closes or terminates the emulator software.

        Returns:
            True if the close command was successful, False otherwise.
        """
        pass
