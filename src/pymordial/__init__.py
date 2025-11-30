"""Pymordial top-level package.

This package exposes the main controller, app, and element classes for
automating BlueStacks interactions.
"""

from pymordial.controller import (
    AdbController,
    BluestacksController,
    BluestacksElements,
    ImageController,
    PymordialController,
)
from pymordial.core import PymordialApp, PymordialElement, PymordialScreen
from pymordial.core.elements.pymordial_button import PymordialButton
from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.elements.pymordial_pixel import PymordialPixel
from pymordial.core.elements.pymordial_text import PymordialText
from pymordial.exceptions import (
    PymordialAppError,
    PymordialConnectionError,
    PymordialEmulatorError,
    PymordialError,
    PymordialStateError,
    PymordialTimeoutError,
)
from pymordial.state_machine import AppLifecycleState, BluestacksState, StateMachine
from pymordial.utils.image_text_checker import ImageTextChecker

__all__ = [
    "AdbController",
    "AppLifecycleState",
    "PymordialApp",
    "PymordialAppError",
    "PymordialButton",
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
    "BluestacksController",
    "BluestacksElements",
    "BluestacksState",
    "ImageController",
    "ImageTextChecker",
    "StateMachine",
]

__version__ = "0.1.0"
