"""Registry for discovering and managing Pymordial plugins."""

import importlib.metadata
import logging
from typing import Dict

from pymordial.core.plugin import PymordialPlugin
from pymordial.utils.config import PymordialConfig

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for Pymordial plugins.

    Handles discovery via Python entry points and manual registration.
    """

    ENTRY_POINT_GROUP = "pymordial.plugins"

    def __init__(self, config: PymordialConfig | None = None) -> None:
        self._plugins: Dict[str, PymordialPlugin] = {}
        self._config = config or {}

    def register(self, plugin: PymordialPlugin) -> None:
        """Registers a plugin instance.

        If a plugin with the same name is already registered, a warning is logged
        and the existing plugin is replaced with the new one.

        Args:
            plugin: The initialized plugin instance.
        """
        if plugin.name in self._plugins:
            logger.warning(f"Overwriting existing plugin registration: {plugin.name}")

        self._plugins[plugin.name] = plugin
        logger.debug(f"Registered plugin: {plugin.name} (v{plugin.version})")

    def get(self, name: str) -> PymordialPlugin:
        """Retrieves a registered plugin by name.

        Args:
            name: The name of the plugin to retrieve.

        Returns:
            The plugin instance.

        Raises:
            KeyError: If the plugin is not found.
        """
        if name not in self._plugins:
            raise KeyError(
                f"Plugin '{name}' not found. Available: {list(self._plugins.keys())}"
            )
        return self._plugins[name]

    def load_from_entry_points(self) -> None:
        """Discovers and loads plugins registered via Python entry points.

        Entry point group: 'pymordial.plugins'
        """
        logger.debug(
            f"Loading plugins from entry point group: {self.ENTRY_POINT_GROUP}"
        )

        # python 3.10+ select interface
        entry_points = importlib.metadata.entry_points().select(
            group=self.ENTRY_POINT_GROUP
        )

        for entry_point in entry_points:
            try:
                # Load the plugin class/factory
                plugin_factory = entry_point.load()

                # Instantiate
                plugin_instance = plugin_factory()

                # Verify protocol
                if not isinstance(plugin_instance, PymordialPlugin):
                    logger.warning(
                        f"Entry point '{entry_point.name}' does not implement PymordialPlugin protocol. Skipping."
                    )
                    continue

                # Initialize
                # TODO: Pass full config or specific config? For now passing empty/None is risky if they depend on it.
                # Ideally config is passed during register or init phase.
                # We'll assume for now plugins handle their own config logic or we pass the global one.
                if self._config:
                    plugin_instance.initialize(self._config)

                self.register(plugin_instance)

            except Exception as e:
                logger.error(
                    f"Failed to load plugin from entry point '{entry_point.name}': {e}"
                )

    def list_plugins(self) -> list[str]:
        """Returns a list of names of registered plugins."""
        return list(self._plugins.keys())
