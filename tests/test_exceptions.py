"""Tests for Pymordial exceptions."""

import pytest
from pymordial.exceptions import (
    PymordialAppError,
    PymordialConnectionError,
    PymordialEmulatorError,
    PymordialError,
    PymordialStateError,
    PymordialTimeoutError,
)


def test_pymordial_error_base():
    """Test base exception inheritance and instantiation."""
    err = PymordialError("Something went wrong")
    assert isinstance(err, Exception)
    assert str(err) == "Something went wrong"


def test_pymordial_emulator_error():
    """Test emulator error."""
    err = PymordialEmulatorError("Emulator failed")
    assert isinstance(err, PymordialError)
    assert str(err) == "Emulator failed"


def test_pymordial_app_error():
    """Test app error."""
    err = PymordialAppError("App crashed")
    assert isinstance(err, PymordialError)
    assert str(err) == "App crashed"


def test_pymordial_state_error():
    """Test state error."""
    err = PymordialStateError("Invalid state")
    assert isinstance(err, PymordialError)
    assert str(err) == "Invalid state"


def test_pymordial_connection_error():
    """Test connection error."""
    err = PymordialConnectionError("Connection lost")
    assert isinstance(err, PymordialError)
    assert str(err) == "Connection lost"


def test_pymordial_timeout_error():
    """Test timeout error."""
    err = PymordialTimeoutError("Operation timed out")
    assert isinstance(err, PymordialError)
    assert str(err) == "Operation timed out"
    assert str(err) == "Operation timed out"
