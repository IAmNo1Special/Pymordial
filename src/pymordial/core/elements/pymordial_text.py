"""Implementation of PymordialText element."""

from dataclasses import dataclass
from pathlib import Path

from pymordial.core.pymordial_element import PymordialElement
from pymordial.ocr.extract_strategy import PymordialExtractStrategy


@dataclass(kw_only=True)
class PymordialText(PymordialElement):
    """PymordialElement that contains text (can be known/unknown).

    Attributes:
        element_text: Known text that the element contains.
        filepath: Optional absolute path for where the element's image will be saved. When not provided, no image is saved.
        extract_strategy: Optional OCR preprocessing strategy.
    """

    element_text: str
    filepath: str | Path | None = None
    extract_strategy: PymordialExtractStrategy | None = None

    def __post_init__(self):
        super().__post_init__()

        if self.filepath is not None:
            try:
                self.filepath = Path(self.filepath).resolve()
            except TypeError:
                raise TypeError(
                    f"Filepath must be a string or Path object, not {type(self.filepath).__name__}"
                )
            except Exception as e:
                raise ValueError(f"Invalid filepath: {e}")

        if not isinstance(self.element_text, str):
            raise TypeError(
                f"Element text must be a string, not {type(self.element_text).__name__}"
            )
        self.element_text = self.element_text.lower()

        if self.extract_strategy is not None:
            if not isinstance(self.extract_strategy, PymordialExtractStrategy):
                raise TypeError(
                    f"Extract strategy must be a PymordialExtractStrategy, not {type(self.extract_strategy).__name__}"
                )

    def __repr__(self) -> str:
        """Returns a string representation of the text element."""
        return (
            f"PymordialText("
            f"label='{self.label}', "
            f"element_text='{self.element_text}', "
            f"position={self.position}, "
            f"size={self.size})"
        )
