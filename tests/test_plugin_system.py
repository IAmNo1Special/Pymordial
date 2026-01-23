"""Tests for the Pymordial Plugin System."""

from unittest.mock import MagicMock, patch

import pytest

from pymordial.core.registry import PluginRegistry


class MockPlugin:
    """A simple mock plugin for testing."""

    name: str = "mock_plugin"
    version: str = "1.0.0"

    def __init__(self):
        self.initialized = False
        self.config = {}

    def initialize(self, config: dict) -> None:
        self.initialized = True
        self.config = config

    def shutdown(self) -> None:
        pass


def test_registry_register_and_get():
    """Test manual registration and retrieval."""
    registry = PluginRegistry()
    plugin = MockPlugin()

    registry.register(plugin)

    retrieved = registry.get("mock_plugin")
    assert retrieved is plugin
    assert retrieved.name == "mock_plugin"


def test_registry_get_missing():
    """Test retrieving a missing plugin raises KeyError."""
    registry = PluginRegistry()
    with pytest.raises(KeyError, match="Plugin 'missing' not found"):
        registry.get("missing")


def test_registry_duplicate_registration_logs_warning(caplog):
    """Test that registering a duplicate name logs a warning."""
    registry = PluginRegistry()
    p1 = MockPlugin()
    p2 = MockPlugin()
    p2.version = "2.0.0"

    registry.register(p1)
    registry.register(p2)  # Should overwrite

    assert "Overwriting existing plugin registration: mock_plugin" in caplog.text
    assert registry.get("mock_plugin") is p2


def test_load_from_entry_points():
    """Test loading plugins from entry points using mocks."""
    registry = PluginRegistry()

    # Mocking importlib.metadata.entry_points
    with patch("importlib.metadata.entry_points") as mock_entry_points:
        # Create a mock entry point
        mock_ep = MagicMock()
        mock_ep.name = "mock_ep"
        mock_ep.load.return_value = MockPlugin  # load() returns the class

        # Configure the select() return
        mock_select = MagicMock()
        mock_select.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_select

        registry.load_from_entry_points()

        # Verify it was loaded and registered
        plugin = registry.get("mock_plugin")
        assert isinstance(plugin, MockPlugin)
        assert plugin.name == "mock_plugin"

        # Verify default init calls (depends on implementation details in load_from_entry_points)
        # Current implementation calls initialize(config)
        assert plugin.initialized is False  # Config was empty in registry init locally

        # Test with config
        config = {"foo": "bar"}
        registry_with_config = PluginRegistry(config=config)

        # Reset mocks for second run
        mock_ep_2 = MagicMock()
        mock_ep_2.name = "mock_ep_2"
        mock_ep_2.load.return_value = MockPlugin

        mock_select_2 = MagicMock()
        mock_select_2.select.return_value = [mock_ep_2]
        mock_entry_points.return_value = mock_select_2

        registry_with_config.load_from_entry_points()

        plugin_2 = registry_with_config.get("mock_plugin")
        assert plugin_2.initialized is True
        assert plugin_2.config == config
