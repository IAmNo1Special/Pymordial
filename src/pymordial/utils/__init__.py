"""
Pymordial utilities module.
"""

import queue


def validate_and_convert_int(value: int | str, param_name: str) -> int:
    """Validate and convert value to int if possible"""
    if not isinstance(value, int):
        try:
            value: int = int(value)
        except ValueError as e:
            raise ValueError(f"Error in {param_name}: {e}")
    return value


class PymordialStreamReader:
    """File-like object that reads from a queue."""

    def __init__(self, queue_size: int, read_timeout: float):
        self.queue = queue.Queue(maxsize=queue_size)
        self.read_timeout = read_timeout
        self.buffer = b""
        self.closed = False

    def read(self, size=-1):
        """Read bytes from queue."""
        while len(self.buffer) < size or size == -1:
            try:
                chunk = self.queue.get(timeout=self.read_timeout)
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

__all__ = [
    "validate_and_convert_int",
    "PymordialStreamReader",
]