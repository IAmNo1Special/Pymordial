from importlib.resources import files

from pymordial.core.elements.pymordial_image import PymordialImage
from pymordial.core.pymordial_element import PymordialElement
from pymordial.utils.config import BluestacksConfig


class BluestacksElements:
    """Stores BlueStacks UI elements.

    Attributes:
        og_resolution: The original resolution of the BlueStacks window.
        config: The BlueStacks configuration dictionary.
        bluestacks_my_games_button: Button element for 'My games'.
        bluestacks_store_search_input: Input element for store search.
        bluestacks_store_button: Button element for store.
        bluestacks_playstore_search_inpput: Input element for Play Store search.
        bluestacks_loading_screen_img: Image element for full loading screen.
    """

    def __init__(self, bluestacks_device):
        """Initializes BluestacksElements.

        Args:
            bluestacks_device: The PymordialBluestacksDevice instance.
        """
        self.og_resolution: tuple[int, int] = bluestacks_device.ref_window_size
        self.config: BluestacksConfig = bluestacks_device.config

        self.bluestacks_my_games_button: PymordialElement = PymordialImage(
            label=self.config["ui"]["my_games_button_label"],
            og_resolution=self.og_resolution,
            filepath=files("pymordial.assets").joinpath(
                self.config["ui"]["assets"]["my_games_button"]
            ),
            confidence=0.6,
            image_text=self.config["ui"]["my_games_text"],
        )

        self.bluestacks_store_search_input: PymordialElement = PymordialImage(
            label=self.config["ui"]["store_search_input_label"],
            og_resolution=self.og_resolution,
            filepath=files("pymordial.assets").joinpath(
                self.config["ui"]["assets"]["store_search_input"]
            ),
            confidence=0.6,
            image_text=self.config["ui"]["store_search_text"],
        )

        self.bluestacks_store_button: PymordialElement = PymordialImage(
            label=self.config["ui"]["store_button_label"],
            og_resolution=self.og_resolution,
            filepath=files("pymordial.assets").joinpath(
                self.config["ui"]["assets"]["store_button"]
            ),
            confidence=0.6,
        )

        self.bluestacks_playstore_search_input: PymordialElement = PymordialImage(
            label=self.config["ui"]["playstore_search_input_label"],
            og_resolution=self.og_resolution,
            filepath=files("pymordial.assets").joinpath(
                self.config["ui"]["assets"]["playstore_search_input"]
            ),
            confidence=0.5,
            image_text=self.config["ui"]["store_search_text"],
        )

        # Loading elements
        self.bluestacks_loading_screen_img: PymordialElement = PymordialImage(
            label=self.config["ui"]["loading_screen_img_label"],
            og_resolution=self.og_resolution,
            filepath=files("pymordial.assets").joinpath(
                self.config["ui"]["assets"]["loading_screen_img"]
            ),
            confidence=0.99,
        )

        # This shouldnt be here
        # self.adb_screenshot_img: PymordialElement = PymordialImage(
        #    label=UI_ADB_SCREENSHOT_IMG_LABEL,
        #    og_resolution=self.og_resolution,
        #    filepath=files("pymordial.assets").joinpath(ASSET_ADB_SCREENSHOT_IMG),
        #    confidence=0.99,
        # )


__all__ = [
    "BluestacksElements",
]
