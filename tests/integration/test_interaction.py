"""Integration tests for element interaction and OCR."""

import time
import pytest

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.pymordial_app import PymordialApp


@pytest.mark.integration
def test_find_and_click_element(real_pymordial_controller: PymordialController):
    """Verifies that an element can be found and clicked."""
    # Ensure we are on home screen
    real_pymordial_controller.go_home()

    # Use the store button as a target element
    store_button = real_pymordial_controller.bluestacks.elements.bluestacks_store_button

    # Attempt to find and click the element
    result = real_pymordial_controller.click_element(store_button)

    # Assert that the element was found and clicked successfully
    assert result is True, "Store button not found or failed to click"


@pytest.mark.integration
def test_ocr_text_extraction(real_pymordial_controller: PymordialController):
    """Verifies that text can be extracted from the screen."""
    # Ensure we are on home screen
    real_pymordial_controller.go_home()

    # Capture screen
    screenshot = real_pymordial_controller.capture_screen()
    assert screenshot is not None, "Failed to capture screenshot"

    try:
        # Try to read text from the screenshot
        text = real_pymordial_controller.read_text(screenshot)

        assert text is not None, "OCR returned None"
        assert len(text) > 0, "OCR extracted empty text"

        # Log the extracted text for debugging
        print(f"Extracted text: {text}")
    except Exception as e:
        # If Tesseract is not configured properly, skip the test
        if "tesseract" in str(e).lower() or "not found" in str(e).lower():
            pytest.skip(f"Tesseract not available: {e}")
        else:
            raise


@pytest.mark.integration
def test_app_lifecycle(real_pymordial_controller: PymordialController):
    """Verifies app open/close lifecycle using Settings app."""
    # Create a PymordialApp for Settings
    settings_app = PymordialApp(
        app_name="settings", package_name="com.android.settings"
    )

    # Add app to controller
    real_pymordial_controller.add_app(settings_app)

    # Open App
    opened = real_pymordial_controller.settings.open()
    assert opened is True, "Settings app failed to open"

    # Verify it's running (quick check)
    is_running = real_pymordial_controller.adb.is_app_running(settings_app)
    assert is_running is True, "Settings app not detected as running"

    # Close App
    closed = real_pymordial_controller.settings.close()
    assert closed is True, "Settings app failed to close"

    # Verify it's closed (quick check)
    is_running = real_pymordial_controller.adb.is_app_running(settings_app)
    assert is_running is False, "Settings app still running after close"
