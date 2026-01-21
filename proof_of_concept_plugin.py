"""Proof of Concept for Pymordial Plugin System."""

import logging
import sys

from pymordial.core.registry import PluginRegistry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Plugin System POC...")

    # Initialize Registry
    registry = PluginRegistry()

    # 1. Load from Entry Points
    logger.info("Loading plugins from entry points...")
    try:
        import importlib.metadata

        all_eps = importlib.metadata.entry_points()
        logger.info(
            f"All Entry Point Groups: {all_eps.keys if hasattr(all_eps, 'keys') else 'unknown type'}"
        )
        if hasattr(all_eps, "groups"):
            logger.info(f"Groups: {all_eps.groups}")
        # Try finding our group specifically
        our_eps = all_eps.select(group="pymordial.plugins")
        logger.info(f"Found 'pymordial.plugins' entry points: {list(our_eps)}")
    except Exception as e:
        logger.error(f"Error inspecting entry points: {e}")

    registry.load_from_entry_points()

    # 2. Verify Built-in Plugins are present (adb, ui, bluestacks)
    expected_plugins = ["adb", "ui", "bluestacks"]
    available_plugins = registry.list_plugins()

    logger.info(f"Available plugins: {available_plugins}")

    missing = [p for p in expected_plugins if p not in available_plugins]

    if missing:
        logger.error(f"Missing expected plugins: {missing}")
        logger.error("Did you run `uv sync` to update entry points?")
        sys.exit(1)

    logger.info("All built-in plugins found!")

    # 3. Retrieve and inspect a plugin
    adb_plugin = registry.get("adb")
    logger.info(f"Retrieved 'adb' plugin: {adb_plugin}")
    logger.info(f"Plugin Name: {adb_plugin.name}")
    logger.info(f"Plugin Version: {adb_plugin.version}")

    logger.info("POC Successful!")


if __name__ == "__main__":
    main()
    main()
