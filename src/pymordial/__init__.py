"""Pymordial top-level package.

This package exposes the main controller, app, and element classes for
automating BlueStacks interactions.
"""

from pymordial.core.app import PymordialApp
from pymordial.core.blueprints.element import PymordialElement
from pymordial.core.blueprints.emulator_device import EmulatorState
from pymordial.core.bluestacks_controller import PymordialBluestacksController
from pymordial.core.screen import PymordialScreen
from pymordial.core.state_machine import AppState, StateMachine
from pymordial.devices.adb_device import PymordialAdbDevice
from pymordial.devices.bluestacks_device import PymordialBluestacksDevice
from pymordial.devices.ui_device import PymordialUiDevice
from pymordial.ui.image import PymordialImage
from pymordial.ui.pixel import PymordialPixel
from pymordial.ui.text import PymordialText
from pymordial.utils.exceptions import (
    PymordialAppError,
    PymordialConnectionError,
    PymordialEmulatorError,
    PymordialError,
    PymordialStateError,
    PymordialTimeoutError,
)

__all__ = [
    "PymordialAdbDevice",
    "AppState",
    "PymordialApp",
    "PymordialAppError",
    "PymordialConnectionError",
    "PymordialBluestacksController",
    "PymordialElement",
    "PymordialEmulatorError",
    "PymordialError",
    "PymordialImage",
    "PymordialPixel",
    "PymordialScreen",
    "PymordialStateError",
    "PymordialText",
    "PymordialTimeoutError",
    "PymordialBluestacksDevice",
    "EmulatorState",
    "PymordialUiDevice",
    "StateMachine",
]

__version__ = "0.3.1"
