"""Basic BlueStacks connection example.

This script demonstrates how to:
1. Create a PymordialBluestacksController
2. Connect to BlueStacks via ADB
3. Execute shell commands
4. Disconnect cleanly
"""

from logging import INFO, basicConfig, getLogger

from pymordial.core.bluestacks_controller import PymordialBluestacksController

logger = getLogger(__name__)


def main():
    """Connect to BlueStacks and verify the connection."""
    basicConfig(level=INFO)
    logger.info("=== Pymordial Basic Connection Example ===\n")

    # Create controller - BlueStacks must be running
    logger.info("1. Creating PymordialBluestacksController...")
    controller = PymordialBluestacksController()
    logger.info("   ✓ Controller created\n")

    # Check if BlueStacks is running
    logger.info("2. Checking BlueStacks status...")
    if controller.bluestacks.is_ready():
        logger.info("   ✓ BlueStacks is running and ready")
    else:
        logger.info("   ⚠ BlueStacks not ready. Opening...")
        controller.bluestacks.open()

    # Verify ADB connection
    logger.info("\n3. Verifying ADB connection...")
    if controller.adb.is_connected():
        logger.info("   ✓ ADB is connected")
    else:
        logger.error("   ✗ ADB not connected. Please check BlueStacks.")
        return

    # Get Android version via shell command
    logger.info("\n4. Getting Android version...")
    result = controller.adb.run_command("getprop ro.build.version.release", decode=True)
    if result:
        android_version = result.strip()
        logger.info(f"   Android Version: {android_version}")

    # Get device model
    logger.info("\n5. Getting device model...")
    result = controller.adb.run_command("getprop ro.product.model", decode=True)
    if result:
        device_model = result.strip()
        logger.info(f"   Device Model: {device_model}")

    logger.info("\n✓ Example completed successfully!\n")


if __name__ == "__main__":
    main()
