"""Utility for checking text in images using OCR."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from pymordial.ocr.base import PymordialOCR
from pymordial.ocr.extract_strategy import PymordialExtractStrategy
from pymordial.ocr.tesseract_ocr import TesseractOCR

if TYPE_CHECKING:
    import numpy as np

    from pymordial.controller.pymordial_controller import PymordialController

logger = logging.getLogger(__name__)


class TextController:
    """Checks for text in images using a pluggable OCR engine.

    Supports optional preprocessing strategies when using TesseractOCR.
    """

    def __init__(
        self,
        ocr_engine: PymordialOCR | None = None,
        pymordial_controller: "PymordialController | None" = None,
    ):
        """Initialize with a specific OCR engine.

        Args:
            ocr_engine: The OCR engine instance to use. Defaults to TesseractOCR.
        """
        if ocr_engine is None:
            self.ocr_engine = TesseractOCR()
        else:
            self.ocr_engine = ocr_engine
        self.pymordial_controller = pymordial_controller

    def check_text(
        self,
        text_to_find: str,
        pymordial_screenshot: "Path | bytes | str | np.ndarray",
        case_sensitive: bool = False,
        strategy: PymordialExtractStrategy | None = None,
    ) -> bool:
        """Checks if specific text is present in the image.

        Args:
            text_to_find: Text to search for in the image.
            pymordial_screenshot: Path to image file, image bytes, or numpy array.
            case_sensitive: Whether to perform a case-sensitive search. Defaults to False.
            strategy: Preprocessing strategy to use. Only supported by
                TesseractOCR. If None, uses default strategy.

        Returns:
            True if the text is found, False otherwise.

        Raises:
            ValueError: If the image cannot be read.
        """

        # Capture screen if we don't have an image to check
        if pymordial_screenshot is None:
            # Ensures PymordialController's ADB is connected
            if not self.pymordial_controller.adb.is_connected():
                self.pymordial_controller.adb.connect()
                if not self.pymordial_controller.adb.is_connected():
                    raise ValueError("PymordialController's ADB is not connected")

            try:
                pymordial_screenshot = self.pymordial_controller.capture_screen()
                if pymordial_screenshot is None:
                    logger.warning("Failed to capture screen.")
            # except TcpTimeoutException:
            #    raise TcpTimeoutException(
            #        f"TCP timeout while finding element {pymordial_element.label}"
            #    )
            except Exception as e:
                logger.error(f"Error capturing screen: {e}")

        try:
            # Extract text with optional strategy (if supported)
            if strategy is not None and isinstance(self.ocr_engine, TesseractOCR):
                extracted = self.ocr_engine.extract_text(
                    pymordial_screenshot, strategy=strategy
                )
            else:
                extracted = self.ocr_engine.extract_text(pymordial_screenshot)

            if case_sensitive:
                return text_to_find in extracted
            return text_to_find.lower() in extracted.lower()
        except Exception as e:
            logger.error(f"Error checking text in image: {e}")
            raise ValueError(f"Error checking text in image: {e}") from e

    def read_text(
        self,
        pymordial_screenshot: "Path | bytes | str | np.ndarray",
        case_sensitive: bool = False,
        strategy: PymordialExtractStrategy | None = None,
    ) -> list[str]:
        """Reads text from the image.

        Args:
            pymordial_screenshot: Path to image file, image bytes, or numpy array.
            case_sensitive: Whether to return text in its original case. Defaults to False.
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
                text = self.ocr_engine.extract_text(
                    pymordial_screenshot, strategy=strategy
                )
            else:
                text = self.ocr_engine.extract_text(pymordial_screenshot)
            if case_sensitive:
                return [line.strip() for line in text.split("\n") if line.strip()]
            return [
                line.strip().lower()
                for line in text.split("\n")
                if line.strip().lower()
            ]
        except Exception as e:
            logger.error(f"Error reading text from image: {e}")
            raise ValueError(f"Error reading text from image: {e}") from e

    def find_text(
        self,
        text_to_find: str,
        pymordial_screenshot: "Path | bytes | str | np.ndarray",
        strategy: PymordialExtractStrategy | None = None,
    ) -> tuple[int, int] | None:
        """Finds the coordinates of specific text in the image.

        Args:
            text_to_find: Text to search for.
            pymordial_screenshot: Path to image file or image bytes.
            strategy: Optional preprocessing strategy.

        Returns:
            (x, y) coordinates if found, None otherwise.
        """
        try:
            # Check if the OCR engine supports find_text (it should as per PymordialOCR)
            if hasattr(self.ocr_engine, "find_text"):
                # Pass strategy if it's TesseractOCR, otherwise just the required args
                if isinstance(self.ocr_engine, TesseractOCR):
                    return self.ocr_engine.find_text(
                        text_to_find, pymordial_screenshot, strategy=strategy
                    )
                return self.ocr_engine.find_text(text_to_find, pymordial_screenshot)
            else:
                logger.warning(
                    f"OCR engine {type(self.ocr_engine).__name__} does not support find_text"
                )
                return None
        except Exception as e:
            logger.error(f"Error finding text in image: {e}")
            return None

    def __repr__(self) -> str:
        """Returns a string representation of the TextController."""
        return f"TextController(" f"ocr_engine={type(self.ocr_engine).__name__})"
