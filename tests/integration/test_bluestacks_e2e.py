"""End-to-end integration tests for BlueStacks."""

import pytest


@pytest.mark.integration
def test_adb_connection(real_adb_controller):
    """Verifies that ADB is connected.
    
    ADB is connected only when BlueStacks is in the READY state.

    Args:
        real_adb_controller: The ADB controller instance.
    """
    assert real_adb_controller.is_connected()


@pytest.mark.integration
def test_adb_shell_command(real_adb_controller):
    """Verifies basic ADB shell command execution.
    
    Args:
        real_adb_controller: The ADB controller instance.
    """
    # Run a simple command like 'ls' or 'date'
    output = real_adb_controller.shell_command("date")
    assert output is not None
    assert len(output) > 0


@pytest.mark.integration
def test_screenshot_capture(real_adb_controller):
    """Verifies that a screenshot can be captured via ADB.
    
    Args:
        real_adb_controller: The ADB controller instance.
    """
    screenshot = real_adb_controller.capture_screenshot()
    assert screenshot is not None
    assert len(screenshot) > 0
