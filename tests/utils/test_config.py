"""Tests for config utility."""

from unittest.mock import patch

from pymordial.utils.config import _deep_merge, get_config


def test_get_config_returns_dict(mock_config):
    """Test that get_config returns a dictionary."""
    config = get_config()
    assert isinstance(config, dict)


def test_get_config_has_required_keys(mock_config):
    """Test that config has required keys."""
    config = get_config()

    assert "adb" in config
    assert "bluestacks" in config
    assert "controller" in config


def test_deep_merge():
    """Test deep merge function."""
    base = {"a": 1, "b": {"c": 2, "d": 3}}
    override = {"b": {"d": 4, "e": 5}, "f": 6}

    _deep_merge(base, override)

    assert base["a"] == 1
    assert base["b"]["c"] == 2
    assert base["b"]["d"] == 4  # Overridden
    assert base["b"]["e"] == 5  # Added
    assert base["f"] == 6  # Added


def test_deep_merge_nested():
    """Test deep merge with nested dictionaries."""
    base = {"level1": {"level2": {"key1": "value1", "key2": "value2"}}}
    override = {"level1": {"level2": {"key2": "overridden"}}}

    _deep_merge(base, override)

    assert base["level1"]["level2"]["key1"] == "value1"
    assert base["level1"]["level2"]["key2"] == "overridden"


def test_config_caching():
    """Test that config is cached after first load."""
    import pymordial.utils.config as config_module

    # Reset state
    config_module._CONFIG = None

    with patch("pymordial.utils.config._load_config") as mock_load:
        # Side effect to actually set the config when called, mocking real behavior
        def mock_load_impl():
            config_module._CONFIG = {"test": "value"}
            return config_module._CONFIG

        mock_load.side_effect = mock_load_impl

        # First call should load
        config1 = get_config()
        assert mock_load.call_count == 1

        # Second call should use cache (mock_load not called again)
        config2 = get_config()
        assert mock_load.call_count == 1

        assert config1 == config2
