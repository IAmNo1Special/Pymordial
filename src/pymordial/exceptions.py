"""Custom exceptions for Pymordial."""


class PymordialError(Exception):
    """Base exception for Pymordial-related errors.

    All Pymordial-specific exceptions should inherit from this class.
    """


class PymordialEmulatorError(PymordialError):
    """Error related to BlueStacks emulator operations.

    This exception is raised when there are issues with:
    - Emulator startup/shutdown
    - Emulator state management
    - ADB connection to the emulator
    """


class PymordialAppError(PymordialError):
    """Error related to Android app operations.

    This exception is raised when there are issues with:
    - App installation/uninstallation
    - App state management
    - App interaction
    """


class PymordialStateError(PymordialError):
    """Error related to invalid state transitions.

    This exception is raised when:
    - An invalid state transition is attempted
    - The current state is unexpected
    - State validation fails
    """


class PymordialConnectionError(PymordialError):
    """Error related to ADB connection issues.

    This exception is raised when:
    - ADB connection cannot be established
    - ADB commands fail
    - ADB server is unreachable
    """


class PymordialTimeoutError(PymordialError):
    """Error related to operation timeouts.

    This exception is raised when:
    - An operation takes longer than expected
    - A timeout occurs during waiting for a state
    - A command execution times out
    """


class ElementNotFoundError(PymordialError):
    """Error raised when an element is not found.

    This exception is raised when:
    - Attempting to retrieve a non-existent element from a screen
    - Attempting to remove a non-existent element from a screen
    """
