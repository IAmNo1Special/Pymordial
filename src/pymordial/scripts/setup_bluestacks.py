"""BlueStacks Setup Script.

This script checks for an existing BlueStacks 5 installation and downloads/installs it if missing.

Usage:
    uv run src/pymordial/scripts/setup_bluestacks.py [--force]
"""

import argparse
import logging
import subprocess
import sys
import urllib.request
import winreg
from pathlib import Path
from tempfile import gettempdir

from pymordial.utils.config import get_config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

_CONFIG = get_config()

BLUESTACKS_DOWNLOAD_URL = _CONFIG["setup"]["download_url"]
BLUESTACKS_REG_KEY = _CONFIG["setup"]["reg_key"]
INSTALLER_NAME = _CONFIG["setup"]["installer_name"]


def is_bluestacks_installed() -> bool:
    """Checks if BlueStacks 5 is installed via Windows Registry.

    Returns:
        True if installed, False otherwise.
    """
    try:
        # Check HKEY_LOCAL_MACHINE
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, BLUESTACKS_REG_KEY, 0, winreg.KEY_READ
        ) as key:
            install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
            logger.info(f"BlueStacks found at: {install_dir}")
            return True
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.warning(f"Error checking registry: {e}")
        return False


def download_installer(url: str, dest_path: Path) -> None:
    """Downloads the installer with a progress bar.

    Args:
        url: The URL to download from.
        dest_path: The destination path to save the file.
    """
    logger.info(f"Downloading BlueStacks installer from {url}...")

    try:
        urllib.request.urlretrieve(url, dest_path)
        logger.info(f"Download complete: {dest_path}")
    except Exception as e:
        logger.error(f"Download failed: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(description="BlueStacks Setup Script")
    parser.add_argument(
        "--force", action="store_true", help="Force download even if installed"
    )
    args = parser.parse_args()

    logger.info("Checking for BlueStacks 5 installation...")

    if not args.force and is_bluestacks_installed():
        logger.info("✅ BlueStacks 5 is already installed.")
        logger.info("Use --force to bypass this check.")
        return

    if args.force:
        logger.info("Force mode enabled: Ignoring existing installation.")
    else:
        logger.info("BlueStacks 5 not found.")

    # Ask for confirmation
    response = (
        input("Would you like to download and install BlueStacks 5 now? [y/N]: ")
        .strip()
        .lower()
    )
    if response not in ("y", "yes"):
        logger.info("Installation aborted by user.")
        return

    # Prepare download path
    temp_dir = Path(gettempdir())
    installer_path = temp_dir / INSTALLER_NAME

    # Download
    download_installer(BLUESTACKS_DOWNLOAD_URL, installer_path)

    # Install
    logger.info("Launching installer...")
    try:
        subprocess.Popen([str(installer_path)])
        logger.info("Installer launched. Please follow the on-screen instructions.")
        logger.info(
            "Note: Once the installer window appears, wait about 5 seconds before interacting with it (an admin permission dialog may appear)."
        )
    except Exception as e:
        logger.error(f"Failed to launch installer: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
