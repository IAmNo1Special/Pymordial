"""OCR implementation using EasyOCR."""

import logging
from pathlib import Path

import easyocr

from pymordial.core.extract_strategy import PymordialExtractStrategy
from pymordial.ocr.base import PymordialOCR
from pymordial.utils.config import get_config

logger = logging.getLogger(__name__)

_CONFIG = get_config()

# --- EasyOCR Configuration ---
DEFAULT_LANGUAGES = _CONFIG["easyocr"]["default_languages"]


class EasyOcrOCR(PymordialOCR):
    """OCR implementation using EasyOCR.

    Attributes:
        languages: List of language codes to use.
        reader: The EasyOCR reader instance.
    """

    def __init__(self, languages: list[str] | None = None, gpu: bool = True):
        """Initializes EasyOcrOCR.

        Args:
            languages: List of language codes. Defaults to config values.
            gpu: Whether to use GPU acceleration.
        """
        self.languages = languages if languages else DEFAULT_LANGUAGES
        self.reader = easyocr.Reader(self.languages, gpu=gpu)

    def extract_text(self, image_path: Path | bytes | str) -> str:
        """Extracts text from an image.

        Args:
            image_path: Path to image file, or image bytes.

        Returns:
            Extracted text combined into a single string.
        """
        lines = self.read_text(image_path)
        return "\n".join(lines)

    def read_text(
        self,
        image_path: Path | bytes | str,
        strategy: PymordialExtractStrategy | None = None,
    ) -> list[str]:
        """Extracts text from an image using EasyOCR.

        Args:
            image_path: Path to the image file, bytes, or string path.
            strategy: Optional preprocessing strategy (ignored by EasyOCR for now,
                but kept for interface compatibility).

        Returns:
            A list of strings found in the image.
        """
        try:
            image_bytes = self._load_image(image_path)
            # EasyOCR can read from bytes directly
            result = self.reader.readtext(image_bytes, detail=0)
            return result
        except Exception as e:
            logger.error(f"Error reading text with EasyOCR: {e}")
            return []

    def _load_image(self, image_path: Path | bytes | str) -> bytes:
        """Helper to load image into bytes.

        Args:
            image_path: Path to image file, bytes, or string path.

        Returns:
            Image bytes.

        Raises:
            ValueError: If image path type is invalid.
        """
        if isinstance(image_path, bytes):
            return image_path
        elif isinstance(image_path, (str, Path)):
            with open(image_path, "rb") as f:
                return f.read()
        else:
            raise ValueError("Invalid image path type")
