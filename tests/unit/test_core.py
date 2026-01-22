from unittest.mock import MagicMock

from pymordial.core.app import AppState
from pymordial.core.controller import PymordialController


def test_controller_instantiation_and_app_lifecycle(mock_controller, app):
    """Test full app lifecycle with verified mock interactions."""
    # Instantiation check
    assert isinstance(mock_controller, PymordialController)
    assert mock_controller.apps == {}

    # Registration
    mock_controller.add_app(app)
    assert "TestApp" in mock_controller.list_apps()
    assert mock_controller.TestApp is app
    assert app.pymordial_controller is mock_controller

    # Mock open_app on the controller instance
    mock_controller.open_app = MagicMock(return_value=True)

    # Open App
    assert app.open() is True

    # Verify delegation
    mock_controller.open_app.assert_called_once()
    args, kwargs = mock_controller.open_app.call_args
    assert args[0] == "TestApp"
    assert kwargs.get("package_name") == "com.test.app"

    assert app.app_state.current_state == AppState.LOADING

    # Mock close_app
    app.app_state.transition_to(AppState.READY)
    mock_controller.close_app = MagicMock(return_value=True)

    # Close App
    assert app.close() is True

    # Verify delegation
    mock_controller.close_app.assert_called_once()
    assert mock_controller.close_app.call_args[1]["package_name"] == "com.test.app"

    assert app.app_state.current_state == AppState.CLOSED
    assert mock_controller.close_app.call_args[1]["package_name"] == "com.test.app"

    assert app.app_state.current_state == AppState.CLOSED
