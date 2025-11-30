"""Integration test fixtures."""

import pytest

from pymordial.controller.adb_controller import AdbController
from pymordial.controller.pymordial_controller import PymordialController
from pymordial.controller.bluestacks_controller import BluestacksController
from pymordial.controller.image_controller import ImageController


@pytest.fixture(scope="session")
def real_adb_controller():
    """Returns a real AdbController connected to a device."""
    controller = AdbController()
    if not controller.connect():
        pytest.skip("No ADB device connected. Skipping integration tests.")
    return controller


@pytest.fixture(scope="session")
def real_image_controller():
    """Returns a real ImageController."""
    return ImageController()


@pytest.fixture(scope="session")
def real_bluestacks_controller(real_adb_controller, real_image_controller):
    """Returns a real BluestacksController with BlueStacks already open."""
    controller = BluestacksController(
        adb_controller=real_adb_controller, image_controller=real_image_controller
    )

    # Ensure BlueStacks is open and ready (open() now waits for load automatically)
    try:
        controller.open()
    except Exception as e:
        pytest.skip(f"BlueStacks not available: {e}")

    return controller


@pytest.fixture(scope="session")
def real_pymordial_controller():
    """Returns a real PymordialController."""
    controller = PymordialController()
    controller.bluestacks.open()
    if not controller.adb.connect():
        pytest.skip("No ADB device connected. Skipping integration tests.")
    return controller
