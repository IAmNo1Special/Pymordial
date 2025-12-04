"""Implementation of PymordialImage element."""

from dataclasses import dataclass
from pathlib import Path

from pymordial.core.pymordial_element import PymordialElement
from pymordial.utils.config import get_config

_CONFIG = get_config()


@dataclass(kw_only=True)
class PymordialImage(PymordialElement):
    """PymordialElement that contains an image.

    Attributes:
        filepath: Absolute path of the element's image.
        confidence: Matching confidence threshold (0.0 to 1.0).
        image_text: Optional known text that the image contains.
    """

    filepath: str | Path
    confidence: float | int
    image_text: str | None = None

    def __post_init__(self):
        super().__post_init__()

        try:
            self.filepath = Path(self.filepath).resolve()
        except TypeError:
            raise TypeError(
                f"Filepath must be a string or Path object, not {type(self.filepath).__name__}"
            )
        except Exception as e:
            raise ValueError(f"Invalid filepath: {e}")

        try:
            self.confidence = float(self.confidence)
        except (ValueError, TypeError):
            raise ValueError(
                f"Confidence must be a float or int, not {type(self.confidence).__name__}"
            )

        if not (0 <= self.confidence <= 1):
            raise ValueError(
                f"Confidence must be between 0 and 1, got {self.confidence}"
            )

        if self.image_text is not None:
            if not isinstance(self.image_text, str):
                raise TypeError(
                    f"Image text must be a string, not {type(self.image_text).__name__}"
                )
            self.image_text = self.image_text.lower()

    def __repr__(self) -> str:
        """Returns a string representation of the image element."""
        return (
            f"PymordialImage("
            f"label='{self.label}', "
            f"filepath='{self.filepath}', "
            f"confidence={self.confidence}, "
            f"position={self.position}, "
            f"size={self.size})"
        )
