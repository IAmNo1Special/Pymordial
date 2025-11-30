"""Utility for checking text in images using OCR."""

import logging
from pathlib import Path

from pymordial.core.extract_strategy import PymordialExtractStrategy
from pymordial.ocr.base import PymordialOCR
from pymordial.ocr.tesseract_ocr import TesseractOCR

logger = logging.getLogger(__name__)


class ImageTextChecker:
    """Checks for text in images using a pluggable OCR engine.

    Supports optional preprocessing strategies when using TesseractOCR.
    """

    def __init__(self, ocr_engine: PymordialOCR | None = None):
        """Initialize with a specific OCR engine.

        Args:
            ocr_engine: The OCR engine instance to use. Defaults to TesseractOCR.
        """
        if ocr_engine is None:
            self.ocr_engine = TesseractOCR()
        else:
            self.ocr_engine = ocr_engine

    def check_text(
        self,
        text_to_find: str,
        image_path: Path | bytes | str,
        strategy: PymordialExtractStrategy | None = None,
    ) -> bool:
        """Checks if specific text is present in the image.

        Args:
            text_to_find: Text to search for in the image.
            image_path: Path to image file or image bytes.
            strategy: Preprocessing strategy to use. Only supported by
                TesseractOCR. If None, uses default strategy.

        Returns:
            True if the text is found, False otherwise.

        Raises:
            ValueError: If the image cannot be read.
        """
        try:
            # Extract text with optional strategy (if supported)
            if strategy is not None and isinstance(self.ocr_engine, TesseractOCR):
                extracted = self.ocr_engine.extract_text(image_path, strategy=strategy)
            else:
                extracted = self.ocr_engine.extract_text(image_path)
            return text_to_find.lower() in extracted.lower()
        except Exception as e:
            logger.error(f"Error checking text in image: {e}")
            raise ValueError(f"Error checking text in image: {e}")

    def read_text(
        self,
        image_path: Path | bytes | str,
        strategy: PymordialExtractStrategy | None = None,
    ) -> list[str]:
        """Reads text from the image.

        Args:
            image_path: Path to image file or image bytes.
            strategy: Preprocessing strategy to use. Only supported by
                TesseractOCR. If None, uses default strategy.

        Returns:
            List of detected text lines.

        Raises:
            ValueError: If the image cannot be read.
        """
        try:
            # Extract text with optional strategy (if supported)
            if strategy is not None and isinstance(self.ocr_engine, TesseractOCR):
                text = self.ocr_engine.extract_text(image_path, strategy=strategy)
            else:
                text = self.ocr_engine.extract_text(image_path)
            return [line.strip() for line in text.split("\n") if line.strip()]
        except Exception as e:
            logger.error(f"Error reading text from image: {e}")
            raise ValueError(f"Error reading text from image: {e}")
