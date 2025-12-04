"""Integration test fixtures."""

import pytest

from pymordial.controller.adb_controller import AdbController
from pymordial.controller.bluestacks_controller import BluestacksController
from pymordial.controller.image_controller import ImageController
from pymordial.controller.pymordial_controller import PymordialController


@pytest.fixture(scope="session")
def real_adb_controller():
    """Returns a real AdbController connected to a device."""
    controller = AdbController()
    if not controller.connect():
        pytest.skip("No ADB device connected. Skipping integration tests.")
    return controller


@pytest.fixture(scope="session")
def real_image_controller(real_pymordial_controller):
    """Returns a real ImageController."""
    return real_pymordial_controller.image


@pytest.fixture(scope="session")
def real_bluestacks_controller(real_pymordial_controller):
    """Returns a real BluestacksController with BlueStacks already open."""
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
