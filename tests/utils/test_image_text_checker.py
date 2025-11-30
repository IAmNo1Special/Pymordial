"""Tests for ImageTextChecker utility."""

from unittest.mock import Mock, patch

import pytest

from pymordial.core.extract_strategy import DefaultExtractStrategy
from pymordial.ocr.tesseract_ocr import TesseractOCR
from pymordial.utils.image_text_checker import ImageTextChecker


def test_image_text_checker_init_default(mock_config):
    """Test ImageTextChecker initialization with default OCR engine."""
    checker = ImageTextChecker()

    assert isinstance(checker.ocr_engine, TesseractOCR)


def test_image_text_checker_init_custom_ocr(mock_config):
    """Test ImageTextChecker initialization with custom OCR engine."""
    mock_ocr = Mock()
    checker = ImageTextChecker(ocr_engine=mock_ocr)

    assert checker.ocr_engine == mock_ocr


def test_check_text_found(mock_config):
    """Test checking text when found in image."""
    mock_ocr = Mock()
    mock_ocr.extract_text.return_value = "Hello World Sample Text"

    checker = ImageTextChecker(ocr_engine=mock_ocr)
    result = checker.check_text(text_to_find="Sample", image_path=b"fake_image")

    assert result is True


def test_check_text_not_found(mock_config):
    """Test checking text when not found in image."""
    mock_ocr = Mock()
    mock_ocr.extract_text.return_value = "Hello World"

    checker = ImageTextChecker(ocr_engine=mock_ocr)
    result = checker.check_text(text_to_find="Missing", image_path=b"fake_image")

    assert result is False


def test_check_text_case_insensitive(mock_config):
    """Test text checking is case insensitive."""
    mock_ocr = Mock()
    mock_ocr.extract_text.return_value = "HELLO WORLD"

    checker = ImageTextChecker(ocr_engine=mock_ocr)
    result = checker.check_text(text_to_find="hello", image_path=b"fake_image")

    assert result is True


def test_check_text_with_strategy(mock_config):
    """Test checking text with preprocessing strategy."""
    mock_ocr = TesseractOCR()
    strategy = DefaultExtractStrategy()

    with patch.object(mock_ocr, "extract_text", return_value="Processed Text"):
        checker = ImageTextChecker(ocr_engine=mock_ocr)
        result = checker.check_text(
            text_to_find="Processed", image_path=b"fake_image", strategy=strategy
        )

        assert result is True
        mock_ocr.extract_text.assert_called_once()


def test_check_text_error_handling(mock_config):
    """Test error handling when OCR fails."""
    mock_ocr = Mock()
    mock_ocr.extract_text.side_effect = Exception("OCR failed")

    checker = ImageTextChecker(ocr_engine=mock_ocr)

    with pytest.raises(ValueError, match="Error checking text"):
        checker.check_text(text_to_find="Sample", image_path=b"fake_image")


def test_read_text(mock_config):
    """Test reading text from image."""
    mock_ocr = Mock()
    mock_ocr.extract_text.return_value = "Line 1\nLine 2\nLine 3"

    checker = ImageTextChecker(ocr_engine=mock_ocr)
    result = checker.read_text(image_path=b"fake_image")

    assert result == ["Line 1", "Line 2", "Line 3"]


def test_read_text_filters_empty_lines(mock_config):
    """Test reading text filters empty lines."""
    mock_ocr = Mock()
    mock_ocr.extract_text.return_value = "Line 1\n\nLine 2\n   \nLine 3"

    checker = ImageTextChecker(ocr_engine=mock_ocr)
    result = checker.read_text(image_path=b"fake_image")

    assert result == ["Line 1", "Line 2", "Line 3"]


def test_read_text_with_strategy(mock_config):
    """Test reading text with preprocessing strategy."""
    mock_ocr = TesseractOCR()
    strategy = DefaultExtractStrategy()

    with patch.object(mock_ocr, "extract_text", return_value="Processed\nText"):
        checker = ImageTextChecker(ocr_engine=mock_ocr)
        result = checker.read_text(image_path=b"fake_image", strategy=strategy)

        assert result == ["Processed", "Text"]


def test_read_text_error_handling(mock_config):
    """Test error handling when reading text fails."""
    mock_ocr = Mock()
    mock_ocr.extract_text.side_effect = Exception("Read failed")

    checker = ImageTextChecker(ocr_engine=mock_ocr)

    with pytest.raises(ValueError, match="Error reading text"):
        checker.read_text(image_path=b"fake_image")
    with pytest.raises(ValueError, match="Error reading text"):
        checker.read_text(image_path=b"fake_image")
