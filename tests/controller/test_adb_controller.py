"""Tests for AdbController."""

from unittest.mock import patch

from pymordial.controller.adb_controller import AdbController
from pymordial.core.pymordial_app import PymordialApp


def test_adb_controller_init_default_params(mock_config):
    """Test AdbController initialization with default parameters."""
    with patch("pymordial.controller.adb_controller.DEFAULT_TIMEOUT", 10):
        controller = AdbController()

        assert controller.host == "127.0.0.1"  # From config
        assert controller.port == 5555  # From config
        assert controller.timeout == 10  # From config
        assert controller.device is None
        assert controller._stream_thread is None


def test_adb_controller_init_custom_params(mock_config):
    """Test AdbController initialization with custom parameters."""
    controller = AdbController(host="192.168.1.100", port=5556, timeout=20)

    assert controller.host == "192.168.1.100"
    assert controller.port == 5556
    assert controller.timeout == 20


def test_connect_success(mock_config, mock_adb_device):
    """Test successful ADB connection."""
    controller = AdbController()

    result = controller.connect()

    assert result is True
    assert controller.device is not None


def test_connect_failure(mock_config):
    """Test ADB connection failure."""
    with patch("pymordial.controller.adb_controller.AdbDeviceTcp") as mock_device_class:
        mock_instance = mock_device_class.return_value
        mock_instance.connect.side_effect = Exception("Connection failed")
        mock_instance.available = False

        controller = AdbController()
        result = controller.connect()

        assert result is False
        assert controller.device is None


def test_disconnect_success(mock_config, mock_adb_device):
    """Test successful ADB disconnection."""
    controller = AdbController()
    controller.connect()

    # Ensure device is initially available
    mock_adb_device.available = True

    # Define side effect for close() to update availability
    def side_effect_close():
        mock_adb_device.available = False

    mock_adb_device.close.side_effect = side_effect_close

    result = controller.disconnect()

    assert result is True
    mock_adb_device.close.assert_called_once()


def test_disconnect_when_not_connected(mock_config):
    """Test disconnecting when not connected."""
    controller = AdbController()

    result = controller.disconnect()

    assert result is True


def test_is_connected_true(mock_config, mock_adb_device):
    """Test is_connected returns True when connected."""
    controller = AdbController()
    controller.connect()

    # mock_adb_device.available is set to True by the fixture
    assert controller.is_connected() is True


def test_is_connected_false(mock_config):
    """Test is_connected returns False when not connected."""
    controller = AdbController()

    assert controller.is_connected() is False


def test_shell_command_success(mock_config, mock_adb_device):
    """Test executing shell command successfully."""
    controller = AdbController()
    controller.connect()

    mock_adb_device.shell.return_value = b"command output"

    result = controller.shell_command("ls")

    assert result == b"command output"
    mock_adb_device.shell.assert_called_once()
    args, _ = mock_adb_device.shell.call_args
    assert args[0] == "ls"


def test_shell_command_not_connected(mock_config):
    """Test shell command when not connected."""
    controller = AdbController()

    result = controller.shell_command("ls")

    assert result is None


def test_tap(mock_config, mock_adb_device):
    """Test tap command."""
    controller = AdbController()
    controller.connect()

    controller.tap(100, 200)

    mock_adb_device.shell.assert_called()


def test_open_app_success(mock_config, mock_adb_device):
    """Test opening an app successfully."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")

    controller = AdbController()
    controller.connect()

    with patch.object(controller, "is_app_running", return_value=True):
        result = controller.open_app(app, timeout=5, wait_time=1)

        assert result is True


def test_is_app_running_true(mock_config, mock_adb_device):
    """Test checking if app is running (returns True)."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")

    controller = AdbController()
    controller.connect()

    mock_adb_device.shell.return_value = b"com.test.app"

    result = controller.is_app_running(app, max_retries=5, wait_time=1)

    assert result is True


def test_is_app_running_false(mock_config, mock_adb_device):
    """Test checking if app is running (returns False)."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")

    controller = AdbController()
    controller.connect()

    mock_adb_device.shell.return_value = b""

    result = controller.is_app_running(app, max_retries=1, wait_time=1)

    assert result is False


def test_close_app(mock_config, mock_adb_device):
    """Test closing an app."""
    app = PymordialApp(app_name="TestApp", package_name="com.test.app")

    controller = AdbController()
    controller.connect()

    controller.close_app(app, timeout=5, wait_time=1)

    mock_adb_device.shell.assert_called()


def test_press_home(mock_config, mock_adb_device):
    """Test pressing home button."""
    controller = AdbController()
    controller.connect()

    result = controller.go_home()

    assert result is True
    mock_adb_device.shell.assert_called()


def test_press_enter(mock_config, mock_adb_device):
    """Test pressing enter button."""
    controller = AdbController()
    controller.connect()

    result = controller.press_enter()

    assert result is True


def test_press_esc(mock_config, mock_adb_device):
    """Test pressing esc button."""
    controller = AdbController()
    controller.connect()

    result = controller.press_esc()

    assert result is True


def test_start_stream(mock_config, mock_adb_device):
    """Test starting screen stream."""
    controller = AdbController()
    controller.connect()

    # mock_adb_device.available is True from fixture
    with patch.object(controller, "shell_command", return_value=b""):
        result = controller.start_stream()
        assert isinstance(result, bool)


def test_stop_stream(mock_config):
    """Test stopping screen stream."""
    controller = AdbController()

    controller.stop_stream()

    assert controller._stream_thread is None


def test_get_latest_frame_no_frame(mock_config):
    """Test getting latest frame when no frame available."""
    controller = AdbController()

    frame = controller.get_latest_frame()

    assert frame is None
