"""OCR engines for Pymordial.

This module provides a pluggable OCR architecture using the Strategy Pattern.
"""

from pymordial.ocr.base import PymordialOCR
from pymordial.ocr.tesseract_ocr import TesseractOCR

# Optional OCR engines (require additional dependencies)
try:
    from pymordial.ocr.easyocr_ocr import EasyOCR
except ImportError:
    EasyOCR = None

__all__ = ["PymordialOCR", "TesseractOCR", "EasyOCR"]
