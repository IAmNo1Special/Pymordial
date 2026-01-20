"""Pymordial top-level package.

This package exposes the main controller, app, and element classes for
automating BlueStacks interactions.
"""

from pymordial.assets import BluestacksElements
from pymordial.controller import (
    ImageController,
    PymordialAdbDevice,
    PymordialBluestacksDevice,
    PymordialController,
    TextController,
)
from pymordial.core import PymordialApp, PymordialElement, PymordialScreen
from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.elements.pymordial_pixel import PymordialPixel
from pymordial.core.elements.pymordial_text import PymordialText
from pymordial.core.pymordial_emulator import EmulatorState
from pymordial.exceptions import (
    PymordialAppError,
    PymordialConnectionError,
    PymordialEmulatorError,
    PymordialError,
    PymordialStateError,
    PymordialTimeoutError,
)
from pymordial.state_machine import AppState, StateMachine

__all__ = [
    "PymordialAdbDevice",
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
    "PymordialBluestacksDevice",
    "BluestacksElements",
    "EmulatorState",
    "ImageController",
    "TextController",
    "StateMachine",
]

__version__ = "0.2.0"
