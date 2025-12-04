"""Abstract base class for OCR engines."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


class PymordialOCR(ABC):
    """Abstract base class for OCR engines.

    All OCR implementations must inherit from this class and implement
    the extract_text method.
    """

    @abstractmethod
    def extract_text(self, image_path: "Path | bytes | str | np.ndarray") -> str:
        """Extracts text from an image.

        Args:
            image_path: Path to image file, image bytes, or numpy array.

        Returns:
            Extracted text from the image.

        Raises:
            ValueError: If image cannot be processed.
        """
        pass

    @abstractmethod
    def find_text(
        self, search_text: str, image_path: "Path | bytes | str | np.ndarray"
    ) -> tuple[int, int] | None:
        """Finds the coordinates (center) of the specified text in the image.

        Args:
            search_text: Text to search for.
            image_path: Path to image file, image bytes, or numpy array.

        Returns:
            (x, y) coordinates of the center of the found text, or None if not found.
        """
        pass

    def contains_text(
        self, search_text: str, image_path: "Path | bytes | str | np.ndarray"
    ) -> bool:
        """Checks if image contains specific text.

        Args:
            search_text: Text to search for.
            image_path: Path to image file, image bytes, or numpy array.

        Returns:
            True if text is found, False otherwise.
        """
        extracted = self.extract_text(image_path)
        return search_text.lower() in extracted.lower()

    def extract_lines(self, image_path: "Path | bytes | str | np.ndarray") -> list[str]:
        """Extracts text as individual lines.

        Args:
            image_path: Path to image file, image bytes, or numpy array.

        Returns:
            List of text lines.
        """
        text = self.extract_text(image_path)
        return [line.strip() for line in text.split("\n") if line.strip()]
