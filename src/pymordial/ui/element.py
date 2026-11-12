"""Abstract base class for Pymordial UI elements."""

from dataclasses import dataclass, field
from typing import final
from uuid import uuid4


@dataclass(kw_only=True, eq=False)
class PymordialElement:
    """Abstract base class for all UI elements.

    Attributes:
        label: A unique identifier for the element.
        position: Optional (x, y) coordinates of the element's bounding box.
        size: Optional (width, height) of the element's bounding box.
        og_resolution: The original window resolution (width, height) used when
            defining the element.
        element_id: Unique identifier for this element instance (auto-generated).
    """

    label: str
    position: tuple[int | float, int | float] | None = None
    size: tuple[int | float, int | float] | None = None
    og_resolution: tuple[int, int] | None = None
    element_id: str = field(default_factory=lambda: str(uuid4()), init=False)

    def __post_init__(self):
        """Post-initialization processing and validation.

        Raises:
            TypeError: If label, position, size, or og_resolution types are invalid.
            ValueError: If label is empty, or if numeric values (position, size, resolution)
                are invalid (negative, zero, wrong length).
        """
        # Validate label
        if not isinstance(self.label, str):
            raise TypeError(f"Label must be a string, not {type(self.label).__name__}")
        if not self.label.strip():
            raise ValueError("Label cannot be empty or whitespace only")
        self.label = self.label.lower()

        # Validate position
        if self.position is not None:
            if not isinstance(self.position, tuple):
                raise TypeError(
                    f"Position must be a tuple, not {type(self.position).__name__}"
                )
            if len(self.position) != 2:
                raise ValueError(
                    f"Position must have 2 values (x, y), got {len(self.position)}"
                )
            if not all(isinstance(p, (int, float)) for p in self.position):
                raise TypeError("All position values must be integers or floats")
            if not all(p >= 0 for p in self.position):
                raise ValueError(
                    f"Position values must be non-negative, got {self.position}"
                )

        # Validate size
        if self.size is not None:
            if not isinstance(self.size, tuple):
                raise TypeError(f"Size must be a tuple, not {type(self.size).__name__}")
            if len(self.size) != 2:
                raise ValueError(
                    f"Size must have 2 values (width, height), got {len(self.size)}"
                )
            if not all(isinstance(s, (int, float)) for s in self.size):
                raise TypeError("All size values must be integers or floats")
            if not all(s > 0 for s in self.size):
                raise ValueError(f"Size values must be positive, got {self.size}")

        # Validate and set og_resolution
        if self.og_resolution is None:
            self.og_resolution = (1920, 1080)
        else:
            if not isinstance(self.og_resolution, tuple):
                raise TypeError(
                    f"Original resolution must be a tuple, not {type(self.og_resolution).__name__}"
                )
            if len(self.og_resolution) != 2:
                raise ValueError(
                    f"Original resolution must have 2 values (width, height), got {len(self.og_resolution)}"
                )
            if not all(isinstance(r, int) for r in self.og_resolution):
                raise TypeError("All original resolution values must be integers")
            if not all(r > 0 for r in self.og_resolution):
                raise ValueError(
                    f"Original resolution values must be positive, got {self.og_resolution}"
                )

    @property
    @final
    def region(self) -> tuple[int, int, int, int] | None:
        """Calculates the bounding box region.

        Returns:
            A tuple of (left, top, right, bottom) if position and size are set,
            otherwise None.
        """
        if self.position and self.size:
            return (
                int(self.position[0]),
                int(self.position[1]),
                int(self.position[0] + self.size[0]),
                int(self.position[1] + self.size[1]),
            )
        return None

    @property
    @final
    def center(self) -> tuple[int | float, int | float] | None:
        """Calculates the center coordinates.

        Returns:
            A tuple of (x, y) coordinates representing the center point if
            position and size are set, otherwise returns the position itself.
        """
        if self.position and self.size:
            return (
                int(self.position[0] + self.size[0] // 2),
                int(self.position[1] + self.size[1] // 2),
            )
        return self.position

    @staticmethod
    def _validate_resolution(
        resolution: tuple[int, int],
    ) -> tuple[int, int]:
        """Validates a (width, height) resolution tuple.

        Raises:
            TypeError: If the resolution is not a tuple of integers.
            ValueError: If it does not have 2 values or any value is not positive.
        """
        if not isinstance(resolution, tuple):
            raise TypeError(
                f"Resolution must be a tuple, not {type(resolution).__name__}"
            )
        if len(resolution) != 2:
            raise ValueError(
                f"Resolution must have 2 values (width, height), got {len(resolution)}"
            )
        if not all(isinstance(r, int) for r in resolution):
            raise TypeError("All resolution values must be integers")
        if not all(r > 0 for r in resolution):
            raise ValueError(
                f"Resolution values must be positive, got {resolution}"
            )
        return resolution

    def _scale_point(
        self,
        point: tuple[int | float, int | float],
        current_resolution: tuple[int, int],
    ) -> tuple[int, int]:
        """Scales one (x, y) point from og_resolution to current_resolution."""
        width, height = self._validate_resolution(current_resolution)
        og_width, og_height = self.og_resolution
        return (
            round(point[0] * width / og_width),
            round(point[1] * height / og_height),
        )

    def scaled_position(
        self, current_resolution: tuple[int, int]
    ) -> tuple[int, int] | None:
        """Returns the element's position scaled to current_resolution.

        Each axis scales independently by its own ratio, so a layout
        recorded at one aspect ratio still lands proportionally on another.
        Returns None when the element has no position. The stored
        position and og_resolution are never modified, so old saved
        elements keep working exactly as before.
        """
        if self.position is None:
            return None
        return self._scale_point(self.position, current_resolution)

    def scaled_size(
        self, current_resolution: tuple[int, int]
    ) -> tuple[int, int] | None:
        """Returns the element's size scaled to current_resolution.

        Returns None when the element has no size.
        """
        if self.size is None:
            return None
        width, height = self._validate_resolution(current_resolution)
        og_width, og_height = self.og_resolution
        return (
            round(self.size[0] * width / og_width),
            round(self.size[1] * height / og_height),
        )

    def scaled_region(
        self, current_resolution: tuple[int, int]
    ) -> tuple[int, int, int, int] | None:
        """Returns the bounding box scaled to current_resolution.

        Returns (left, top, right, bottom), or None when the element
        has no position or size. Mirrors region, computed from the
        scaled position and scaled size.
        """
        scaled_position = self.scaled_position(current_resolution)
        scaled_size = self.scaled_size(current_resolution)
        if scaled_position is None or scaled_size is None:
            return None
        return (
            scaled_position[0],
            scaled_position[1],
            scaled_position[0] + scaled_size[0],
            scaled_position[1] + scaled_size[1],
        )

    def scaled_center(
        self, current_resolution: tuple[int, int]
    ) -> tuple[int, int] | None:
        """Returns the click target scaled to current_resolution.

        Mirrors center, computed from the scaled position and scaled
        size, and falls back to the scaled position when there is no
        size. Returns None when the element has no position.
        """
        scaled_position = self.scaled_position(current_resolution)
        if scaled_position is None:
            return None
        scaled_size = self.scaled_size(current_resolution)
        if scaled_size is None:
            return scaled_position
        return (
            scaled_position[0] + scaled_size[0] // 2,
            scaled_position[1] + scaled_size[1] // 2,
        )

    def __hash__(self) -> int:
        """Returns hash based on unique element_id."""
        return hash(self.element_id)

    def __eq__(self, other) -> bool:
        """Compares elements by their unique element_id."""
        if not isinstance(other, PymordialElement):
            return NotImplemented
        return self.element_id == other.element_id
