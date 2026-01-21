"""Integration test fixtures."""

import pytest

from pymordial.core.controller import PymordialController
from pymordial.devices.adb_device import PymordialAdbDevice


@pytest.fixture(scope="session")
def real_adb_controller():
    """Returns a real PymordialAdbDevice connected to a device."""
    controller = PymordialAdbDevice()
    if not controller.connect():
        pytest.skip("No ADB device connected. Skipping integration tests.")
    return controller


@pytest.fixture(scope="session")
def real_ui_device(real_pymordial_controller):
    """Returns a real PymordialUiDevice."""
    return real_pymordial_controller.ui


@pytest.fixture(scope="session")
def real_bluestacks_controller(real_pymordial_controller):
    """Returns a real PymordialBluestacksDevice with BlueStacks already open."""
    return real_pymordial_controller.bluestacks


@pytest.fixture(scope="session")
def real_pymordial_controller():
    """Returns a real PymordialController."""
    controller = PymordialController()
    try:
        controller.bluestacks.open()
    except Exception as e:
        pytest.skip(f"BlueStacks not available: {e}")

    if not controller.adb.connect():
        pytest.skip("No ADB device connected. Skipping integration tests.")
    return controller
