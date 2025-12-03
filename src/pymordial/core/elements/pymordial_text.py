"""Implementation of PymordialText element."""

from dataclasses import dataclass
from pathlib import Path

from pymordial.core.extract_strategy import PymordialExtractStrategy
from pymordial.core.pymordial_element import PymordialElement


@dataclass(kw_only=True)
class PymordialText(PymordialElement):
    """PymordialElement that contains text (can be known/unknown).

    If the text is known and provided, this element can be passed to a PymordialController's `match` method.

    Attributes:
        filepath: Optional absolute path for where the element's image will be saved. When not provided, no image is saved.
        known_text: Optional known text that the element contains.
        extract_strategy: Optional OCR preprocessing strategy.
    """

    filepath: str | Path | None = None
    known_text: str | None = None
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

        if self.known_text is not None:
            if not isinstance(self.known_text, str):
                raise TypeError(
                    f"Known text must be a string, not {type(self.known_text).__name__}"
                )
            self.known_text = self.known_text.lower()

        if self.extract_strategy is not None:
            if not isinstance(self.extract_strategy, PymordialExtractStrategy):
                raise TypeError(
                    f"Extract strategy must be a PymordialExtractStrategy, not {type(self.extract_strategy).__name__}"
                )
