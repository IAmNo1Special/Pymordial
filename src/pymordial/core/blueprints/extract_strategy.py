from abc import ABC, abstractmethod
from typing import Any


class PymordialExtractStrategy(ABC):
    """Abstract base class for OCR preprocessing strategies."""

    @abstractmethod
    def preprocess(self, image: Any) -> Any:
        """Returns a pre‑processed image ready for OCR.

        Args:
            image: The input image as a numpy array.

        Returns:
            The processed image as a numpy array.
        """
        pass

    @abstractmethod
    def tesseract_config(self) -> str:
        """Returns the Tesseract command‑line configuration string.

        Returns:
            The configuration string.
        """
        pass

    def postprocess_text(self, text: str) -> str:
        """Optional post-processing of OCR text. Override to customize.

        Args:
            text: The raw text extracted by OCR.

        Returns:
            The cleaned text.
        """
        return text.strip()
