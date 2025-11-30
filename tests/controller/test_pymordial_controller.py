"""Tests for PymordialController."""

from unittest.mock import patch

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.pymordial_app import PymordialApp


def test_pymordial_controller_init():
    """Test PymordialController initialization."""
    with patch("pymordial.controller.pymordial_controller.AdbController"):
        with patch("pymordial.controller.pymordial_controller.BluestacksController"):
            with patch("pymordial.controller.pymordial_controller.ImageController"):
                controller = PymordialController()
                assert controller.adb is not None
                assert controller.bluestacks is not None
                assert controller.image is not None


def test_add_app():
    """Test adding an app."""
    with patch("pymordial.controller.pymordial_controller.AdbController"):
        with patch("pymordial.controller.pymordial_controller.BluestacksController"):
            with patch("pymordial.controller.pymordial_controller.ImageController"):
                controller = PymordialController()
                app = PymordialApp(app_name="TestApp", package_name="com.test")
                controller.add_app(app)
                assert "TestApp" in controller._apps
