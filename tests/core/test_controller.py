"""Tests for PymordialController."""

from unittest.mock import patch

from pymordial.core.app import PymordialApp
from pymordial.core.controller import PymordialController


def test_pymordial_controller_init():
    """Test PymordialController initialization."""
    with patch("pymordial.core.controller.PymordialAdbDevice"):
        with patch("pymordial.core.controller.PymordialBluestacksDevice"):
            with patch("pymordial.core.controller.PymordialUiDevice"):
                controller = PymordialController()
                assert controller.adb is not None
                assert controller.bluestacks is not None
                assert controller.ui is not None


def test_add_app():
    """Test adding an app."""
    with patch("pymordial.core.controller.PymordialAdbDevice"):
        with patch("pymordial.core.controller.PymordialBluestacksDevice"):
            with patch("pymordial.core.controller.PymordialUiDevice"):
                controller = PymordialController()
                app = PymordialApp(app_name="TestApp", package_name="com.test")
                controller.add_app(app)
                assert "TestApp" in controller._apps
