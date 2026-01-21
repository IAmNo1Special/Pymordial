"""Tests for PymordialUiDevice (Text functions)."""

from unittest.mock import Mock, patch

import pytest

from pymordial.devices.extract_strategies import DefaultExtractStrategy
from pymordial.devices.tesseract_device import PymordialTesseractDevice
from pymordial.devices.ui_device import PymordialUiDevice


@pytest.fixture
def mock_adb_device():
    """Create a mock PymordialAdbDevice."""
    adb = Mock()
    adb.is_connected.return_value = True
    return adb


def test_ui_device_text_init_default(mock_config, mock_adb_device):
    """Test PymordialUiDevice initialization defaults."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)
    assert isinstance(device._ocr_device, PymordialTesseractDevice)


def test_check_text_found(mock_config, mock_adb_device):
    """Test checking text when found in image."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    # Mock the internal OCR device's extract_text method
    mock_ocr = Mock(spec=PymordialTesseractDevice)
    mock_ocr.extract_text.return_value = "Hello World Sample Text"
    device._ocr_device = mock_ocr

    result = device.check_text(
        text_to_find="Sample", pymordial_screenshot=b"fake_image"
    )

    assert result is True


def test_check_text_not_found(mock_config, mock_adb_device):
    """Test checking text when not found in image."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    mock_ocr = Mock(spec=PymordialTesseractDevice)
    mock_ocr.extract_text.return_value = "Hello World"
    device._ocr_device = mock_ocr

    result = device.check_text(
        text_to_find="Missing", pymordial_screenshot=b"fake_image"
    )

    assert result is False


def test_check_text_case_insensitive(mock_config, mock_adb_device):
    """Test text checking is case insensitive."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    mock_ocr = Mock(spec=PymordialTesseractDevice)
    mock_ocr.extract_text.return_value = "HELLO WORLD"
    device._ocr_device = mock_ocr

    result = device.check_text(text_to_find="hello", pymordial_screenshot=b"fake_image")

    assert result is True


def test_check_text_with_strategy(mock_config, mock_adb_device):
    """Test checking text with preprocessing strategy."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)
    strategy = DefaultExtractStrategy()

    # We need a real Tesseract device instance (or mock spec) for isinstance check in check_text
    # but we want to mock extract_text

    with patch.object(
        PymordialTesseractDevice, "extract_text", return_value="Processed Text"
    ):
        device = PymordialUiDevice(bridge_device=mock_adb_device)
        # Ensure it initialized a Tesseract device (default)
        assert isinstance(device._ocr_device, PymordialTesseractDevice)

        result = device.check_text(
            text_to_find="Processed",
            pymordial_screenshot=b"fake_image",
            strategy=strategy,
        )

        assert result is True


def test_check_text_error_handling(mock_config, mock_adb_device):
    """Test error handling when OCR fails."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    mock_ocr = Mock(spec=PymordialTesseractDevice)
    mock_ocr.extract_text.side_effect = Exception("OCR failed")
    device._ocr_device = mock_ocr

    with pytest.raises(ValueError, match="Error checking text"):
        device.check_text(text_to_find="Sample", pymordial_screenshot=b"fake_image")


def test_read_text(mock_config, mock_adb_device):
    """Test reading text from image."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    mock_ocr = Mock(spec=PymordialTesseractDevice)
    mock_ocr.extract_text.return_value = "Line 1\nLine 2\nLine 3"
    device._ocr_device = mock_ocr

    result = device.read_text(pymordial_screenshot=b"fake_image")

    # read_text lowercases by default
    assert result == ["line 1", "line 2", "line 3"]


def test_read_text_filters_empty_lines(mock_config, mock_adb_device):
    """Test reading text filters empty lines."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    mock_ocr = Mock(spec=PymordialTesseractDevice)
    mock_ocr.extract_text.return_value = "Line 1\n\nLine 2\n   \nLine 3"
    device._ocr_device = mock_ocr

    result = device.read_text(pymordial_screenshot=b"fake_image")

    assert result == ["line 1", "line 2", "line 3"]


def test_read_text_with_strategy(mock_config, mock_adb_device):
    """Test reading text with preprocessing strategy."""
    strategy = DefaultExtractStrategy()

    with patch.object(
        PymordialTesseractDevice, "extract_text", return_value="Processed\nText"
    ):
        device = PymordialUiDevice(bridge_device=mock_adb_device)

        result = device.read_text(pymordial_screenshot=b"fake_image", strategy=strategy)

        assert result == ["processed", "text"]


def test_read_text_error_handling(mock_config, mock_adb_device):
    """Test error handling when reading text fails."""
    device = PymordialUiDevice(bridge_device=mock_adb_device)

    mock_ocr = Mock(spec=PymordialTesseractDevice)
    mock_ocr.extract_text.side_effect = Exception("Read failed")
    device._ocr_device = mock_ocr

    with pytest.raises(ValueError, match="Error reading text"):
        device.read_text(pymordial_screenshot=b"fake_image")
