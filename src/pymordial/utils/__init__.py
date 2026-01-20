import functools
import logging
import queue
import sys

logger = logging.getLogger(__name__)


def validate_and_convert_int(value: int | str, param_name: str) -> int:
    """Validate and convert value to int if possible"""
    if not isinstance(value, int):
        try:
            value: int = int(value)
        except ValueError as e:
            raise ValueError(f"Error in {param_name}: {e}")
    return value


def log_property_setter(func):
    """Decorator to log property setter operations with dynamic logger selection.

    Priority:
    1. self.logger (if attached to a class method)
    2. Global module 'logger' (if attached to a standalone function)
    3. utils.__init__.logger (fallback)

    Args:
        func: The property setter function to decorate.

    Returns:
        The decorated function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 1. Try to get logger from 'self' (first arg of a method)
        target_logger = None
        if args and hasattr(args[0], "logger"):
            target_logger = getattr(args[0], "logger")

        # 2. Try to get module-level logger
        if target_logger is None:
            module = sys.modules.get(func.__module__)
            if module:
                target_logger = getattr(module, "logger", None)

        # 3. Fallback to utils.logger
        if target_logger is None:
            target_logger = logger

        # Heuristic for the 'value' being set:
        # If it's a method (self, value), use args[1]
        # If it's a function (value), use args[0]
        value = None
        if len(args) > 1:
            value = args[1]
        elif len(args) == 1:
            value = args[0]

        target_logger.debug(f"Setting {func.__name__}...")
        result = func(*args, **kwargs)
        target_logger.debug(f"{func.__name__} set to {value}")
        return result

    return wrapper


class PymordialStreamReader:
    """File-like object that reads from a queue."""

    def __init__(self, queue_size: int, read_timeout: float):
        self.queue = queue.Queue(maxsize=queue_size)
        self.read_timeout = read_timeout
        self.buffer = b""
        self.closed = False

    def read(self, size=-1):
        """Read bytes from queue."""
        # If we have enough data in buffer, return immediately
        if size != -1 and len(self.buffer) >= size:
            result = self.buffer[:size]
            self.buffer = self.buffer[size:]
            return result

        # Otherwise, try to get more data
        try:
            # We wait for ONE chunk. If it times out, we return what we have.
            # We do NOT loop infinitely on Empty.
            chunk = self.queue.get(timeout=self.read_timeout)

            if chunk is None:  # End signal
                self.closed = True

            else:
                self.buffer += chunk

        except queue.Empty:
            # Timeout reached. Do NOT continue. Return partial data or empty.
            pass

        # Return whatever we managed to gather
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


__all__ = [
    "validate_and_convert_int",
    "log_property_setter",
    "PymordialStreamReader",
]
