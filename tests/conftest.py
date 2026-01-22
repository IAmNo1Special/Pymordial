import pytest

from pymordial.core.app import PymordialApp
from pymordial.core.controller import PymordialController


class ConcreteController(PymordialController):
    """Concrete implementation of PymordialController for testing."""

    def _resolve_plugin(self, name, default_factory, configure_found_plugin=None):
        return default_factory()

    def capture_screen(self):
        return None

    def click_coord(self, coords, times=1):
        return True

    def click_element(self, element, times=1, screenshot=None, max_tries=1):
        return True

    def click_elements(self, elements, screenshot=None, max_tries=1):
        return True

    def find_element(self, element, screenshot=None, max_tries=1):
        return (0, 0)

    def is_element_visible(self, element, screenshot=None, max_tries=None):
        return True

    def open_app(self, app_name, package_name, timeout, wait_time):
        return True

    def close_app(self, package_name, timeout, wait_time):
        return True

    def read_text(self, image_path, case_sensitive=False, strategy=None):
        return []

    def check_text(self, text_to_find, image_path, case_sensitive=False, strategy=None):
        return True


@pytest.fixture
def mock_controller():
    return ConcreteController()


@pytest.fixture
def app():
    return PymordialApp("TestApp", "com.test.app")
