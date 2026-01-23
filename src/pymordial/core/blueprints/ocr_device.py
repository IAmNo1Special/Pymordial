"""Abstract base class for OCR engines."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class PymordialOCRDevice(ABC):
    """Abstract base class for OCR engines.

    All OCR implementations must inherit from this class and implement
    the extract_text method.
    """

    @abstractmethod
    def extract_text(self, image_path: Path | bytes | str | Any) -> str:
        """Extracts text from an image.

        Args:
            image_path: The image source (file path, bytes, or numpy array).

        Returns:
            The raw text extracted from the image.

        Raises:
            ValueError: If the image format is unsupported or cannot be processed.
        """
        pass

    @abstractmethod
    def find_text(self, search_text: str, image_path: Any) -> tuple[int, int] | None:
        """Finds the coordinates (center) of the specified text in the image.

        Args:
            search_text: The text string to search for.
            image_path: The image source (file path, bytes, or numpy array).

        Returns:
            A tuple of (x, y) coordinates for the center of the found text,
            or None if the text is not found.
        """
        pass

    def contains_text(
        self, search_text: str, image_path: Path | bytes | str | Any
    ) -> bool:
        """Checks if image contains specific text.

        Args:
            search_text: The text string to search for.
            image_path: The image source (file path, bytes, or numpy array).

        Returns:
            True if the search text is found (case-insensitive), False otherwise.
        """
        extracted = self.extract_text(image_path)
        return search_text.lower() in extracted.lower()

    def extract_lines(self, image_path: Path | bytes | str | Any) -> list[str]:
        """Extracts text as individual lines.

        Args:
            image_path: The image source (file path, bytes, or numpy array).

        Returns:
            A list of non-empty text lines extracted from the image.
        """
        text = self.extract_text(image_path)
        return [line.strip() for line in text.split("\n") if line.strip()]
