"""Tests for Tesseract OCR implementation."""

from unittest.mock import patch
import numpy as np

from pymordial.ocr.tesseract_ocr import TesseractOCR


def test_tesseract_ocr_init(mock_config):
    """Test Tesseract OCR initialization."""
    ocr = TesseractOCR()
    # Matches the 'tesseract_config' in your src/pymordial/config.yaml
    assert ocr.config == "--oem 3 --psm 6"


def test_tesseract_ocr_init_with_config(mock_config):
    """Test Tesseract OCR with custom config."""
    ocr = TesseractOCR(config="--psm 6")
    assert ocr.config == "--psm 6"


def test_tesseract_ocr_read(mock_config):
    """Test reading text with Tesseract."""
    # We must mock cv2 because extract_text tries to decode the bytes into a numpy array
    with patch("pymordial.ocr.tesseract_ocr.pytesseract.image_to_string") as mock_ocr:
        with patch("pymordial.ocr.tesseract_ocr.cv2.imdecode") as mock_imdecode:
            # Return a valid dummy numpy array for cv2.resize to work
            mock_imdecode.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            mock_ocr.return_value = "Sample Text"

            ocr = TesseractOCR()
            result = ocr.extract_text(b"fake_image")

            assert result == "Sample Text"
            mock_ocr.assert_called_once()


def test_tesseract_ocr_read_with_config(mock_config):
    """Test reading text with custom Tesseract config."""
    with patch("pymordial.ocr.tesseract_ocr.pytesseract.image_to_string") as mock_ocr:
        with patch("pymordial.ocr.tesseract_ocr.cv2.imdecode") as mock_imdecode:
            mock_imdecode.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            mock_ocr.return_value = "Configured Text"

            ocr = TesseractOCR(config="--psm 7")
            result = ocr.extract_text(b"fake_image")

            assert result == "Configured Text"