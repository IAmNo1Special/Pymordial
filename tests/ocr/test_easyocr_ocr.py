"""Tests for EasyOCR implementation."""

from unittest.mock import patch
from pymordial.ocr.easyocr_ocr import EasyOcrOCR

def test_easyocr_init(mock_config):
    """Test EasyOCR initialization."""
    with patch("pymordial.ocr.easyocr_ocr.easyocr.Reader") as mock_reader:
        ocr = EasyOcrOCR()
        assert ocr.reader is not None
        mock_reader.assert_called_once()

def test_easyocr_read(mock_config):
    """Test reading text with EasyOCR."""
    with patch("pymordial.ocr.easyocr_ocr.easyocr.Reader") as mock_reader_class:
        mock_reader = mock_reader_class.return_value
        # EasyOCR returns list of (bbox, text, prob)
        mock_reader.readtext.return_value = [
            ([(0, 0), (100, 0), (100, 50), (0, 50)], "Hello", 0.95),
            ([(0, 60), (100, 60), (100, 110), (0, 110)], "World", 0.90),
        ]

        ocr = EasyOcrOCR()
        # read_text returns the raw list
        result = ocr.read_text(b"fake_image")

        # Check that the text components are present in the result tuples
        assert any(r[1] == "Hello" for r in result)
        assert any(r[1] == "World" for r in result)