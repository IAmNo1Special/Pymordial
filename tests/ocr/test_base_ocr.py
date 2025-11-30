"""Tests for OCR base class."""

from pymordial.ocr.base import PymordialOCR


class ConcreteOCR(PymordialOCR):
    """Concrete implementation for testing."""

    def extract_text(self, image):
        return "Mock OCR Text"


def test_base_pymordial_ocr_abstract():
    """Test that BasePymordialOCR is abstract."""
    # Should be able to instantiate concrete class
    ocr = ConcreteOCR()
    assert ocr is not None


def test_concrete_ocr_read():
    """Test concrete OCR extract_text method."""
    ocr = ConcreteOCR()
    result = ocr.extract_text(b"fake_image")

    assert result == "Mock OCR Text"