"""Pymordial top-level package.

This package exposes the main controller, app, and element classes for
automating BlueStacks interactions.
"""

from pymordial.core.app import PymordialApp
from pymordial.core.blueprints.emulator_device import EmulatorState
from pymordial.core.controller import PymordialController
from pymordial.core.screen import PymordialScreen
from pymordial.core.state_machine import AppState, StateMachine
from pymordial.ui.element import PymordialElement
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
    "AppState",
    "PymordialApp",
    "PymordialAppError",
    "PymordialConnectionError",
    "PymordialController",
    "PymordialElement",
    "PymordialEmulatorError",
    "PymordialError",
    "PymordialImage",
    "PymordialPixel",
    "PymordialScreen",
    "PymordialStateError",
    "PymordialText",
    "PymordialTimeoutError",
    "EmulatorState",
    "StateMachine",
]

__version__ = "0.4.0"
