"""App control example.

This script demonstrates how to:
1. Define a Pymordial app
2. Open and close apps
3. Check if an app is running
4. Use config values for timeouts
"""

import time

from pymordial.controller.pymordial_controller import PymordialController
from pymordial.core.pymordial_app import PymordialApp
from pymordial.utils.config import get_config


def main():
    """Control an Android app lifecycle."""
    print("=== Pymordial App Control Example ===\n")

    # Get config values (can be customized in config.yaml)
    config = get_config()
    # timeout = config["app"]["action_timeout"]
    wait_time = config["app"]["action_wait_time"]

    # Create controller
    print("1. Creating PymordialController...")
    controller = PymordialController()
    if controller:
        controller.bluestacks.open()
        print("   ✓ Controller created (ADB connected automatically)")
    else:
        print("   ✗ Controller failed initialization!!!")
        return

    # Define an app (using Android Settings as example)
    print("2. Defining Android Settings app...")
    settings_app = PymordialApp(
        app_name="Settings", package_name="com.android.settings"
    )

    # Register the app with the controller
    print("3. Registering app with controller...")
    controller.add_app(settings_app)

    # Open the app
    print("4. Opening Settings app...")
    settings_app.open()
    print("   ✓ App opened")

    # Wait a moment
    time.sleep(2)

    # Check if app is running (uses config values)
    print("5. Checking if app is running...")
    is_running = controller.adb.is_app_running(
        settings_app, wait_time=wait_time
    )
    if is_running:
        print("   ✓ Settings app is running")

    # Close the app
    print("6. Closing Settings app...")
    settings_app.close()
    print("   ✓ App closed")

    # Verify it's closed
    print("7. Verifying app is closed...")
    is_running = controller.adb.is_app_running(
        settings_app, wait_time=wait_time
    )
    if not is_running:
        print("   ✓ Settings app is not running\n")

    print("Tip: Customize timeout and wait_time in config.yaml")
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
