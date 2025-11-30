"""Abstract base class for OCR engines."""

from abc import ABC, abstractmethod
from pathlib import Path


class PymordialOCR(ABC):
    """Abstract base class for OCR engines.

    All OCR implementations must inherit from this class and implement
    the extract_text method.
    """

    @abstractmethod
    def extract_text(self, image_path: Path | bytes | str) -> str:
        """Extracts text from an image.

        Args:
            image_path: Path to image file, or image bytes.

        Returns:
            Extracted text from the image.

        Raises:
            ValueError: If image cannot be processed.
        """
        pass

    def contains_text(self, search_text: str, image_path: Path | bytes | str) -> bool:
        """Checks if image contains specific text.

        Args:
            search_text: Text to search for.
            image_path: Path to image file, or image bytes.

        Returns:
            True if text is found, False otherwise.
        """
        extracted = self.extract_text(image_path)
        return search_text.lower() in extracted.lower()

    def extract_lines(self, image_path: Path | bytes | str) -> list[str]:
        """Extracts text as individual lines.

        Args:
            image_path: Path to image file, or image bytes.

        Returns:
            List of text lines.
        """
        text = self.extract_text(image_path)
        return [line.strip() for line in text.split("\n") if line.strip()]
