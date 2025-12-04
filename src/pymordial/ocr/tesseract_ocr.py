"""Tesseract OCR implementation (requires Tesseract installation)."""

import logging
from pathlib import Path

import cv2
import numpy as np
import pytesseract

from pymordial.ocr.base import PymordialOCR
from pymordial.ocr.extract_strategy import (
    DefaultExtractStrategy,
    PymordialExtractStrategy,
)
from pymordial.utils.config import get_config

logger = logging.getLogger(__name__)

_CONFIG = get_config()

# --- Tesseract Configuration ---
DEFAULT_CONFIG = _CONFIG["extract_strategy"]["tesseract"]["default_config"]


class TesseractOCR(PymordialOCR):
    """Tesseract OCR implementation.

    Advantages:
    - Lightweight (~50MB)
    - Fast CPU-only inference
    - Good accuracy for clean text
    - Cross-platform

    Requirements:
    - Tesseract must be installed on the system
    - See TESSERACT_INSTALL.md for installation instructions

    Attributes:
        config: Tesseract configuration string.
    """

    def __init__(self, config: str = DEFAULT_CONFIG):
        """Initializes Tesseract OCR.

        Args:
            config: Tesseract configuration string.
        """
        self.config = config

        # Check for configured Tesseract path
        tesseract_cmd = _CONFIG["extract_strategy"]["tesseract"].get("tesseract_cmd")
        if tesseract_cmd and Path(tesseract_cmd).exists():
            pytesseract.pytesseract.tesseract_cmd = str(tesseract_cmd)
            logger.info(f"Using configured Tesseract: {tesseract_cmd}")
            return

        # Check for bundled Tesseract (fallback)
        bundled_tess = (
            Path(__file__).parent.parent / "bin" / "tesseract" / "tesseract.exe"
        )
        if bundled_tess.exists():
            pytesseract.pytesseract.tesseract_cmd = str(bundled_tess)
            logger.info(f"Using bundled Tesseract: {bundled_tess}")

    def extract_text(
        self,
        image_path: "Path | bytes | str | np.ndarray",
        strategy: PymordialExtractStrategy | None = None,
    ) -> str:
        """Extracts text from an image using Tesseract with optional preprocessing.

        Args:
            image_path: Path to image file, image bytes, numpy array, or a string path.
            strategy: Optional PymordialExtractStrategy instance. If None, a
                DefaultExtractStrategy is used, providing generic preprocessing
                suitable for any image.

        Returns:
            The extracted text.

        Raises:
            ValueError: If the image cannot be processed.
        """
        try:
            # Load image
            image = self._load_image(image_path)
            # Choose strategy
            if strategy is None:
                strategy = DefaultExtractStrategy()
            # Preprocess image using the strategy
            processed = strategy.preprocess(image)
            # Use strategy-provided Tesseract config (fallback to self.config)
            config = strategy.tesseract_config() or self.config
            # Extract text using Tesseract
            text = pytesseract.image_to_string(processed, config=config)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text with Tesseract: {e}")
            raise ValueError(f"Failed to extract text: {e}")

    def find_text(
        self,
        search_text: str,
        image_path: "Path | bytes | str | np.ndarray",
        strategy: PymordialExtractStrategy | None = None,
    ) -> tuple[int, int] | None:
        """Finds the coordinates (center) of the specified text in the image.

        Args:
            search_text: Text to search for.
            image_path: Path to image file, image bytes, or numpy array.
            strategy: Optional preprocessing strategy.

        Returns:
            (x, y) coordinates of the center of the found text, or None if not found.
        """
        try:
            image = self._load_image(image_path)
            if strategy is None:
                strategy = DefaultExtractStrategy()
            processed = strategy.preprocess(image)
            config = strategy.tesseract_config() or self.config

            data = pytesseract.image_to_data(
                processed, config=config, output_type=pytesseract.Output.DICT
            )

            search_text_lower = search_text.lower()
            n_boxes = len(data["text"])
            for i in range(n_boxes):
                # Check if confidence is sufficient (e.g. > 0) to avoid noise
                if int(data["conf"][i]) > 0:
                    text = data["text"][i].strip().lower()
                    if search_text_lower in text:
                        (x, y, w, h) = (
                            data["left"][i],
                            data["top"][i],
                            data["width"][i],
                            data["height"][i],
                        )
                        center_x = x + w // 2
                        center_y = y + h // 2
                        return (center_x, center_y)
            return None
        except Exception as e:
            logger.error(f"Error finding text with Tesseract: {e}")
            return None

    def _load_image(self, image_path: "Path | bytes | str | np.ndarray") -> np.ndarray:
        """Loads image from path, bytes, or numpy array.

        Args:
            image_path: Path to image file, image bytes, numpy array, or a string path.

        Returns:
            The loaded image as a numpy array.

        Raises:
            ValueError: If the image cannot be read.
        """
        if isinstance(image_path, np.ndarray):
            return image_path
        if isinstance(image_path, bytes):
            nparr = np.frombuffer(image_path, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            image = cv2.imread(str(image_path))

        if image is None:
            raise ValueError(f"Could not read image from {image_path}")

        return image
