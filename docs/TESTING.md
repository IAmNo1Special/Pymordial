# Testing Pymordial

Pymordial has a comprehensive test suite ensuring reliability across ADB, BlueStacks, and Image Recognition components.

## Running Tests

We use `pytest` for testing.

### 1. Run All Tests
```bash
uv run pytest
```

### 2. Run Unit Tests Only (Fast)
To skip integration tests that require a running BlueStacks emulator:
```bash
uv run pytest -m "not integration"
```
*This is used in CI environments.*

### 3. Run Integration Tests
To run tests that interact with a real BlueStacks instance:
```bash
uv run pytest tests/integration/
```
**Prerequisites for Integration Tests:**
- BlueStacks must be installed.
- ADB must be enabled.
- A running emulator instance is recommended (though tests will attempt to launch one).

## Test Structure

- `tests/controller/`: Unit tests for `AdbController`, `BluestacksController`, etc.
- `tests/core/`: Unit tests for `PymordialApp`, `PymordialElement`.
- `tests/integration/`: End-to-end tests verifying real interaction with BlueStacks.

## Writing Tests

When adding new features, please add corresponding tests.

### Mocking
Use `unittest.mock` to mock ADB responses for unit tests.
```python
@patch("pymordial.controller.adb_controller.AdbShell")
def test_my_feature(mock_adb):
    controller = PymordialController()
    # ...
```

### Integration Markers
Mark tests that require an emulator with `@pytest.mark.integration`.
```python
import pytest

@pytest.mark.integration
def test_real_click():
    # ...
```
