# Testing Pymordial

Pymordial uses pytest for comprehensive testing across all components.

## Running Tests

### All Tests
```bash
uv run pytest
```

### Unit Tests Only (No BlueStacks Required)
```bash
uv run pytest -m "not integration"
```
CI/CD uses this command.

### Integration Tests (Requires BlueStacks)
```bash
uv run pytest -m integration
```

**Prerequisites:**
- BlueStacks installed
- ADB enabled (Settings → Advanced → ADB)
- Emulator running

### With Coverage
```bash
uv run pytest --cov=pymordial --cov-report=html
```

View report: `open htmlcov/index.html`

---

## Test Structure

```
tests/
├── controller/         # AdbController, BluestacksController, etc.
├── core/              # PymordialApp, PymordialElement, Screens
├── ocr/               # Tesseract, EasyOCR, strategies
└── integration/       # End-to-end tests with real BlueStacks
```

---

## Writing Tests

### Unit Test Example

```python
from unittest.mock import MagicMock, patch
from pymordial.controller.adb_controller import AdbController

def test_tap():
    """Test ADB tap command."""
    controller = AdbController(ip="127.0.0.1", port=5555)
    
    # Mock the shell command
    with patch.object(controller, 'shell_command') as mock_shell:
        result = controller.tap(100, 200)
        
        # Verify correct command was called
        mock_shell.assert_called_once_with("input tap 100 200")
```

### Integration Test Example

```python
import pytest
from pymordial.controller.pymordial_controller import PymordialController

@pytest.mark.integration
def test_real_connection():
    """Test actual connection to BlueStacks."""
    controller = PymordialController()
    
    assert controller.adb.is_connected()
    
    # Test home navigation
    controller.adb.go_home()
    
    # Verify we're on launcher
    current_app = controller.adb.get_current_app()
    assert "launcher" in current_app.lower()
```

---

## Fixtures

Common fixtures are in `conftest.py`:

```python
@pytest.fixture
def mock_controller():
    """Returns a mocked PymordialController."""
    controller = MagicMock(spec=PymordialController)
    controller.adb.is_connected.return_value = True
    return controller

@pytest.fixture
def real_controller():
    """Returns a real controller (integration tests only)."""
    return PymordialController()
```

---

## Test Markers

Mark tests with pytest markers:

```python
@pytest.mark.integration  # Requires BlueStacks
@pytest.mark.slow         # Long-running test
@pytest.mark.ocr          # Requires Tesseract
```

Run specific markers:
```bash
uv run pytest -m "integration and not slow"
```

---

## Mocking Best Practices

### Mock ADB Responses

```python
@patch("pymordial.controller.adb_controller.AdbShell")
def test_get_android_version(mock_adb_shell):
    mock_device = MagicMock()
    mock_device.shell.return_value = b"11\n"
    mock_adb_shell.return_value = mock_device
    
    controller = AdbController()
    controller.connect()
    
    result = controller.shell_command("getprop ro.build.version.release")
    assert result == b"11\n"
```

### Mock Image Recognition

```python
@patch("pymordial.controller.image_controller.locate")
def test_find_button(mock_locate):
    from pyautogui import Box
    mock_locate.return_value = Box(left=100, top=200, width=50, height=30)
    
    controller = ImageController()
    result = controller.where_element(my_button)
    
    # Returns center coordinates
    assert result == (125, 215)
```

---

## Continuous Integration

GitHub Actions workflow (`.github/workflows/test.yml`):

```yaml
- name: Run unit tests
  run: uv run pytest -m "not integration" --cov=pymordial

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

---

## Tips

1. **Test one thing**: Each test should verify one behavior
2. **Use fixtures**: Avoid code duplication
3. **Mock external calls**: Don't rely on BlueStacks for unit tests
4. **Name clearly**: Test names should explain what they verify
5. **Fast by default**: Integration tests should opt-in with markers

---

## Debugging Failed Tests

### Verbose Output
```bash
uv run pytest -vv
```

### Stop on First Failure
```bash
uv run pytest -x
```

### Run Specific Test
```bash
uv run pytest tests/controller/test_adb.py::test_tap
```

### Show Print Statements
```bash
uv run pytest -s
```
