"""Tests for PymordialController convenience methods."""

from unittest.mock import Mock, patch

import pytest

from pymordial.controller.pymordial_controller import PymordialController


class TestConvenienceMethods:
    """Test convenience delegation methods in PymordialController."""

    @pytest.fixture
    def controller(self):
        """Create a PymordialController with mocked sub-controllers."""
        with (
            patch("pymordial.controller.pymordial_controller.AdbController"),
            patch("pymordial.controller.pymordial_controller.ImageController"),
            patch("pymordial.controller.pymordial_controller.TextController"),
            patch("pymordial.controller.pymordial_controller.BluestacksController"),
        ):
            controller = PymordialController()
            # Mock the sub-controllers
            controller.adb = Mock()
            controller.image = Mock()
            controller.text = Mock()
            controller.bluestacks = Mock()
            return controller

    def test_go_home_delegates_to_adb(self, controller):
        """Test that go_home() delegates to adb.go_home()."""
        controller.go_home()
        controller.adb.go_home.assert_called_once()

    def test_go_back_delegates_to_adb(self, controller):
        """Test that go_back() delegates to adb.go_back()."""
        controller.go_back()
        controller.adb.go_back.assert_called_once()

    def test_tap_delegates_to_adb(self, controller):
        """Test that tap() delegates to adb.tap() with correct arguments."""
        controller.tap(100, 200)
        controller.adb.tap.assert_called_once_with(100, 200)

    def test_swipe_delegates_to_adb(self, controller):
        """Test that swipe() delegates to adb.swipe() with correct arguments."""
        controller.swipe(100, 200, 300, 400, duration=500)
        controller.adb.swipe.assert_called_once_with(100, 200, 300, 400, 500)

    def test_swipe_with_default_duration(self, controller):
        """Test that swipe() uses default duration of 300ms."""
        controller.swipe(100, 200, 300, 400)
        controller.adb.swipe.assert_called_once_with(100, 200, 300, 400, 300)

    def test_capture_screen_delegates_to_adb(self, controller):
        """Test that capture_screen() delegates to adb.capture_screenshot()."""
        # Setup mock return value
        controller.adb.is_connected.return_value = True
        mock_screenshot = b"screenshot_data"
        controller.adb.capture_screenshot.return_value = mock_screenshot

        # Call method
        result = controller.capture_screen()

        # Verify
        controller.adb.capture_screenshot.assert_called_once()  # Verify ADB call
        assert result == mock_screenshot

    def test_capture_screen_returns_none_on_failure(self, controller):
        """Test that capture_screen() properly returns None on failure."""
        controller.adb.is_connected.return_value = False
        controller.adb.capture_screenshot.return_value = None

        result = controller.capture_screen()

        assert result is None

    # --- Phase 1 & 2 Convenience Method Tests ---

    def test_press_enter_delegates_to_adb(self, controller):
        """Test that press_enter() delegates to adb.press_enter()."""
        controller.press_enter()
        controller.adb.press_enter.assert_called_once()

    def test_press_esc_delegates_to_adb(self, controller):
        """Test that press_esc() delegates to adb.press_esc()."""
        controller.press_esc()
        controller.adb.press_esc.assert_called_once()

    def test_send_text_delegates_to_adb(self, controller):
        """Test that send_text() delegates to adb.send_text()."""
        controller.send_text("Hello World")
        controller.adb.send_text.assert_called_once_with("Hello World")

    def test_shell_command_delegates_to_adb(self, controller):
        """Test that shell_command() delegates to adb.shell_command()."""
        mock_output = b"command output"
        controller.adb.shell_command.return_value = mock_output

        result = controller.shell_command("pm list packages")

        controller.adb.shell_command.assert_called_once_with("pm list packages")
        assert result == mock_output

    def test_get_current_app_delegates_to_adb(self, controller):
        """Test that get_current_app() delegates to adb.get_current_app()."""
        mock_package = "com.example.app"
        controller.adb.get_current_app.return_value = mock_package

        result = controller.get_current_app()

        controller.adb.get_current_app.assert_called_once()
        assert result == mock_package

    def test_read_text_delegates_to_text_controller(self, controller):
        """Test that read_text() delegates to text.read_text()."""
        mock_text = ["Line 1", "Line 2", "Line 3"]
        controller.text.read_text.return_value = mock_text

        result = controller.read_text(b"screenshot_bytes")

        controller.text.read_text.assert_called_once_with(
            b"screenshot_bytes", False, None
        )
        assert result == mock_text

    def test_read_text_with_strategy(self, controller):
        """Test that read_text() passes strategy parameter."""
        from unittest.mock import Mock

        mock_strategy = Mock()
        mock_text = ["Text with strategy"]
        controller.text.read_text.return_value = mock_text

        result = controller.read_text("image.png", strategy=mock_strategy)

        controller.text.read_text.assert_called_once_with(
            "image.png", False, mock_strategy
        )
        assert result == mock_text

    def test_check_text_delegates_to_text_controller(self, controller):
        """Test that check_text() delegates to text.check_text()."""
        controller.text.check_text.return_value = True

        result = controller.check_text("Victory", b"screenshot", case_sensitive=False)

        controller.text.check_text.assert_called_once_with(
            "Victory", b"screenshot", False, None
        )
        assert result is True

    def test_is_ready_delegates_to_bluestacks(self, controller):
        """Test that is_ready() delegates to bluestacks.is_ready()."""
        controller.bluestacks.is_ready.return_value = True

        result = controller.is_bluestacks_ready()

        controller.bluestacks.is_ready.assert_called_once()
        assert result is True

    def test_is_loading_delegates_to_bluestacks(self, controller):
        """Test that is_bluestacks_loading() delegates to bluestacks.is_loading()."""
        controller.bluestacks.is_loading.return_value = False

        result = controller.is_bluestacks_loading()

        controller.bluestacks.is_loading.assert_called_once()
        assert result is False
