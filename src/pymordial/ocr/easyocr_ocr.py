"""OCR implementation using EasyOCR."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import easyocr
import numpy as np

from pymordial.ocr.base import PymordialOCR
from pymordial.ocr.extract_strategy import PymordialExtractStrategy
from pymordial.utils.config import get_config

if TYPE_CHECKING:
    pass

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

    def extract_text(self, image_path: "Path | bytes | str | np.ndarray") -> str:
        """Extracts text from an image.

        Args:
            image_path: Path to image file, image bytes, or numpy array.

        Returns:
            Extracted text combined into a single string.
        """
        lines = self.read_text(image_path)
        return "\n".join(lines)

    def read_text(
        self,
        image_path: "Path | bytes | str | np.ndarray",
        strategy: PymordialExtractStrategy | None = None,
    ) -> list[str]:
        """Extracts text from an image using EasyOCR.

        Args:
            image_path: Path to the image file, bytes, string path, or numpy array.
            strategy: Optional preprocessing strategy. Currently not implemented
                for EasyOCR, but planned for future versions.

        Returns:
            A list of strings found in the image.
        """
        # TODO: Implement preprocessing strategies for EasyOCR
        try:
            image_bytes = self._load_image(image_path)
            # EasyOCR can read from bytes directly
            result = self.reader.readtext(image_bytes, detail=0)
            return result
        except Exception as e:
            logger.error(f"Error reading text with EasyOCR: {e}")
            return []

    def find_text(
        self,
        search_text: str,
        image_path: "Path | bytes | str | np.ndarray",
    ) -> tuple[int, int] | None:
        """Finds the coordinates (center) of the specified text in the image.

        Args:
            search_text: Text to search for.
            image_path: Path to image file, image bytes, string path, or numpy array.

        Returns:
            (x, y) coordinates of the center of the found text, or None if not found.
        """
        try:
            image_bytes = self._load_image(image_path)
            # EasyOCR readtext returns (bbox, text, confidence)
            result = self.reader.readtext(image_bytes, detail=1)

            search_text_lower = search_text.lower()
            for bbox, text, confidence in result:
                if search_text_lower in text.lower():
                    # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                    # Calculate center from bounding box
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    center_x = int(sum(x_coords) / len(x_coords))
                    center_y = int(sum(y_coords) / len(y_coords))
                    return (center_x, center_y)
            return None
        except Exception as e:
            logger.error(f"Error finding text with EasyOCR: {e}")
            return None

    def _load_image(self, image_path: "Path | bytes | str | np.ndarray") -> bytes:
        """Helper to load image into bytes.

        Args:
            image_path: Path to image file, bytes, string path, or numpy array.

        Returns:
            Image bytes.

        Raises:
            ValueError: If image path type is invalid.
        """
        if isinstance(image_path, bytes):
            return image_path
        elif isinstance(image_path, np.ndarray):
            # Convert numpy array to bytes
            success, buffer = cv2.imencode(".png", image_path)
            if not success:
                raise ValueError("Failed to encode numpy array to image bytes")
            return buffer.tobytes()
        elif isinstance(image_path, (str, Path)):
            with open(image_path, "rb") as f:
                return f.read()
        else:
            raise ValueError(f"Invalid image path type: {type(image_path)}")
