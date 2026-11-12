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
        self.shutdown_called = False

    def initialize(self, config: dict) -> None:
        self.initialized = True
        self.config = config

    def shutdown(self) -> None:
        self.shutdown_called = True


class FailingPlugin(MockPlugin):
    """A mock plugin whose shutdown always fails."""

    name: str = "failing_plugin"

    def shutdown(self) -> None:
        raise RuntimeError("shutdown failed")


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


def test_shutdown_all_calls_shutdown_on_each_plugin():
    """Test that shutdown_all calls shutdown on every plugin."""
    registry = PluginRegistry()
    p1 = MockPlugin()
    p2 = MockPlugin()
    p2.name = "mock_plugin_2"

    registry.register(p1)
    registry.register(p2)
    registry.shutdown_all()

    assert p1.shutdown_called is True
    assert p2.shutdown_called is True


def test_shutdown_all_continues_when_one_plugin_fails(caplog):
    """Test that one failing plugin does not stop the rest shutting down."""
    registry = PluginRegistry()
    failing = FailingPlugin()
    ok = MockPlugin()

    registry.register(failing)
    registry.register(ok)
    registry.shutdown_all()

    assert ok.shutdown_called is True
    assert "Failed to shut down plugin 'failing_plugin'" in caplog.text


def test_shutdown_all_clears_registry():
    """Test that plugins are removed from the registry after shutdown."""
    registry = PluginRegistry()
    registry.register(MockPlugin())

    registry.shutdown_all()

    assert registry.list_plugins() == []
    # A second call is a safe no-op.
    registry.shutdown_all()
    assert registry.list_plugins() == []


def test_shutdown_all_empty_registry():
    """Test that shutting down an empty registry does nothing."""
    registry = PluginRegistry()
    registry.shutdown_all()
    assert registry.list_plugins() == []


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

        # Verify default init calls: initialize() runs even with an empty
        # config, so the plugin can set up its own defaults.
        assert plugin.initialized is True
        assert plugin.config == {}

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


def test_load_from_entry_points_initializes_with_empty_config():
    """A plugin loaded with no registry config is still initialized."""
    registry = PluginRegistry(config={})

    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_ep = MagicMock()
        mock_ep.name = "mock_ep"
        mock_ep.load.return_value = MockPlugin

        mock_select = MagicMock()
        mock_select.select.return_value = [mock_ep]
        mock_entry_points.return_value = mock_select

        registry.load_from_entry_points()

        plugin = registry.get("mock_plugin")
        assert plugin.initialized is True
        assert plugin.config == {}
