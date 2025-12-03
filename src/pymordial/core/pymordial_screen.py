"""Container for Pymordial UI elements representing a screen."""

from dataclasses import dataclass, field

from pymordial.core.pymordial_element import PymordialElement
from pymordial.exceptions import ElementNotFoundError


@dataclass
class PymordialScreen:
    """Represents a screen within an application.

    Attributes:
        name: The name of the screen.
        elements: A dictionary of elements belonging to this screen.
    """

    name: str
    elements: dict[str, PymordialElement] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validates the screen attributes after initialization.

        Raises:
            ValueError: If the name is empty or not a string.
            TypeError: If elements is not a dictionary or contains invalid keys/values.
        """
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Screen name must be a non-empty string")

        if not isinstance(self.elements, dict):
            raise TypeError("Elements must be a dictionary")

        for key, element in self.elements.items():
            if not isinstance(key, str):
                raise TypeError(
                    f"Element keys must be strings, got {type(key).__name__}"
                )
            if not isinstance(element, PymordialElement):
                raise TypeError(
                    f"Values must be PymordialElement instances, got {type(element).__name__}"
                )

    def add_element(self, element: PymordialElement) -> None:
        """Adds an element to the screen.

        Args:
            element: The element to add.

        Raises:
            TypeError: If the element is not a PymordialElement instance.
            ValueError: If an element with the same label already exists.
        """
        if not isinstance(element, PymordialElement):
            raise TypeError(
                f"Element must be a PymordialElement instance, got {type(element).__name__}"
            )
        if element.label in self.elements:
            raise ValueError(f"Element with label '{element.label}' already exists")
        self.elements[element.label] = element

    def get_element(self, label: str) -> PymordialElement:
        """Retrieves an element by its label.

        Args:
            label: The label of the element to retrieve.

        Returns:
            The PymordialElement instance.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        try:
            return self.elements[label]
        except KeyError:
            raise ElementNotFoundError(
                f"Element '{label}' not found on screen '{self.name}'"
            )

    def remove_element(self, label: str) -> PymordialElement:
        """Removes an element by its label.

        Args:
            label: The label of the element to remove.

        Returns:
            The removed PymordialElement.

        Raises:
            ElementNotFoundError: If the element is not found.
        """
        try:
            return self.elements.pop(label)
        except KeyError:
            raise ElementNotFoundError(
                f"Element '{label}' not found on screen '{self.name}'"
            )
