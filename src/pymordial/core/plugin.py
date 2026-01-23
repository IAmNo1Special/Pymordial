"""Core Protocol definition for Pymordial Plugins."""

from typing import Protocol, runtime_checkable

from pymordial.utils.config import PymordialConfig


@runtime_checkable
class PymordialPlugin(Protocol):
    """Protocol defining the interface for all Pymordial plugins.

    Plugins are the mechanism for extending Pymordial with new device types,
    controllers, or utilities.

    Attributes:
        name: A unique identifier for the plugin.
        version: Semantic version string of the plugin.
    """

    name: str
    version: str

    def initialize(self, config: PymordialConfig) -> None:
        """Initializes the plugin with the provided configuration.

        Args:
            config: The global Pymordial configuration dictionary.
        """
        ...

    def shutdown(self) -> None:
        """Performs any necessary cleanup when the plugin is unloaded."""
        ...
