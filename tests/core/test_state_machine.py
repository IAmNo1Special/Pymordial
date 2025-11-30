"""Tests for Pymordial state machine."""

from enum import Enum, auto
from unittest.mock import Mock

import pytest

from pymordial.state_machine import AppLifecycleState, BluestacksState, StateMachine


class StateForTesting(Enum):
    STATE_A = auto()
    STATE_B = auto()
    STATE_C = auto()


def test_bluestacks_state_transitions():
    """Test BlueStacks state transitions definition."""
    transitions = BluestacksState.get_transitions()

    assert BluestacksState.CLOSED in transitions
    assert BluestacksState.LOADING in transitions[BluestacksState.CLOSED]
    assert BluestacksState.READY in transitions[BluestacksState.LOADING]
    assert BluestacksState.CLOSED in transitions[BluestacksState.READY]


def test_app_lifecycle_state_transitions():
    """Test App lifecycle state transitions definition."""
    transitions = AppLifecycleState.get_transitions()

    assert AppLifecycleState.CLOSED in transitions
    assert AppLifecycleState.LOADING in transitions[AppLifecycleState.CLOSED]
    assert AppLifecycleState.READY in transitions[AppLifecycleState.LOADING]
    assert AppLifecycleState.CLOSED in transitions[AppLifecycleState.READY]


def test_state_machine_init():
    """Test StateMachine initialization."""
    sm = StateMachine(current_state=StateForTesting.STATE_A)
    assert sm.current_state == StateForTesting.STATE_A
    assert sm.transitions == {}
    assert sm.state_handlers == {}


def test_state_machine_transition_valid():
    """Test valid state transition."""
    transitions = {
        StateForTesting.STATE_A: [StateForTesting.STATE_B],
        StateForTesting.STATE_B: [StateForTesting.STATE_C],
    }
    sm = StateMachine(current_state=StateForTesting.STATE_A, transitions=transitions)

    prev_state = sm.transition_to(StateForTesting.STATE_B)

    assert prev_state == StateForTesting.STATE_A
    assert sm.current_state == StateForTesting.STATE_B


def test_state_machine_transition_invalid():
    """Test invalid state transition raises ValueError."""
    transitions = {
        StateForTesting.STATE_A: [StateForTesting.STATE_B],
    }
    sm = StateMachine(current_state=StateForTesting.STATE_A, transitions=transitions)

    with pytest.raises(ValueError, match="Invalid state transition"):
        sm.transition_to(StateForTesting.STATE_C)


def test_state_machine_transition_ignore_validation():
    """Test forcing a transition with ignore_validation."""
    transitions = {
        StateForTesting.STATE_A: [StateForTesting.STATE_B],
    }
    sm = StateMachine(current_state=StateForTesting.STATE_A, transitions=transitions)

    sm.transition_to(StateForTesting.STATE_C, ignore_validation=True)
    assert sm.current_state == StateForTesting.STATE_C


def test_state_machine_handlers():
    """Test state entry and exit handlers."""
    sm = StateMachine(
        current_state=StateForTesting.STATE_A,
        transitions={StateForTesting.STATE_A: [StateForTesting.STATE_B]},
    )

    mock_exit_a = Mock()
    mock_enter_b = Mock()

    sm.register_handler(StateForTesting.STATE_A, on_exit=mock_exit_a)
    sm.register_handler(StateForTesting.STATE_B, on_enter=mock_enter_b)

    sm.transition_to(StateForTesting.STATE_B)

    mock_exit_a.assert_called_once()
    mock_enter_b.assert_called_once()


def test_state_machine_repr():
    """Test string representation."""
    sm = StateMachine(current_state=StateForTesting.STATE_A)
    assert "StateMachine(current_state=StateForTesting.STATE_A" in str(sm)
    assert "StateMachine(current_state=StateForTesting.STATE_A" in repr(sm)