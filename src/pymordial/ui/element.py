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

    def __hash__(self) -> int:
        """Returns hash based on unique element_id."""
        return hash(self.element_id)

    def __eq__(self, other) -> bool:
        """Compares elements by their unique element_id."""
        if not isinstance(other, PymordialElement):
            return NotImplemented
        return self.element_id == other.element_id
