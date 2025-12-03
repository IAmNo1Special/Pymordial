"""Implementation of PymordialButton element."""

from dataclasses import dataclass

from pymordial.core.elements.pymordial_image import PymordialImage


@dataclass(kw_only=True)
class PymordialButton(PymordialImage):
    """UI element representing a clickable button.

    Currently behaves identical to PymordialImage but semantically distinct.
    Inherits all attributes from PymordialImage:
        - label: A unique identifier for the element.
        - position: (x, y) coordinates of the element's bounding box.
        - size: (width, height) of the element's bounding box.
        - og_resolution: The original window resolution (width, height).
        - filepath: Absolute path of the element's image.
        - confidence: Matching confidence threshold (0.0 to 1.0).
        - image_text: Optional known text that the element contains.
    """
