"""Basic BlueStacks connection example.

This script demonstrates how to:
1. Create a PymordialController (connection is automatic!)
2. Check connection status
3. Execute shell commands
4. Disconnect cleanly

Note: ADB connection happens automatically via the state machine.
You don't need to manually call connect() in normal usage.
"""

from logging import INFO, basicConfig, getLogger

from pymordial.controller.pymordial_controller import PymordialController

logger = getLogger(__name__)


def main():
    """Connect to BlueStacks and verify the connection."""
    basicConfig(level=INFO)
    logger.info("=== Pymordial Basic Connection Example ===\n")

    # Create controller - this automatically:
    # 1. Discovers BlueStacks
    # 2. Opens BlueStacks if needed
    # 3. Connects ADB (via state machine handler)
    logger.info("1. Creating PymordialController...")
    controller = PymordialController()
    if controller:
        controller.bluestacks.open()
        logger.info("   ✓ Controller created (ADB connected automatically)")
    else:
        logger.info("   ✗ Controller failed initialization!!!")
        return

    # Check connection status
    logger.info("\n2. Verifying ADB connection...")
    if controller.adb.is_connected():
        logger.info("   ✓ ADB is connected")
    else:
        logger.info("   ✗ ADB not connected. Is BlueStacks running?")
        return

    # Get device info via shell command
    logger.info("\n3. Getting device info...")
    result = controller.shell_command("getprop ro.build.version.release")
    if result:
        android_version = result.decode("utf-8").strip()
        logger.info(f"   Android Version: {android_version}")

    # Disconnect (optional - usually not needed)
    logger.info("\n4. Disconnecting...")
    controller.adb.disconnect()
    logger.info("   ✓ Disconnected\n")

    logger.info("Tip: Connection usually happens automatically!")
    logger.info("Example completed successfully!")


if __name__ == "__main__":
    main()
