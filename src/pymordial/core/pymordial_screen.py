"""Container for Pymordial UI elements representing a screen."""

from pymordial.core.pymordial_element import PymordialElement


class PymordialScreen:
    """Represents a screen within an application.

    Attributes:
        name: The name of the screen.
        elements: A dictionary of elements belonging to this screen.
    """

    def __init__(self, name: str, elements: dict[str, PymordialElement] | None = None):
        """Initializes a PymordialScreen.

        Args:
            name: The name of the screen.
            elements: Optional dictionary of elements.
        """
        self.name = name
        self.elements: dict[str, PymordialElement] = elements or {}

    def add_element(self, element: PymordialElement) -> None:
        """Adds an element to the screen.

        Args:
            element: The element to add.
        """
        self.elements[element.label] = element
