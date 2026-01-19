from abc import ABC, abstractmethod
from logging import DEBUG, basicConfig, getLogger


class PymordialBridgeDevice(ABC):
    logger = getLogger("PymordialBridgeDevice")
    basicConfig(
        level=DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def run_command(self):
        pass

    @abstractmethod
    def open_app(self):
        pass

    @abstractmethod
    def is_app_running(self):
        pass

    @abstractmethod
    def show_recent_apps(self):
        pass

    @abstractmethod
    def close_app(self):
        pass

    @abstractmethod
    def tap(self):
        pass

    @abstractmethod
    def type_text(self):
        pass

    @abstractmethod
    def go_home(self):
        pass

    @abstractmethod
    def press_enter(self):
        pass

    @abstractmethod
    def press_esc(self):
        pass

    @abstractmethod
    def capture_screenshot(self):
        pass

    @abstractmethod
    def start_stream(self):
        pass

    @abstractmethod
    def stop_stream(self):
        pass

    @abstractmethod
    def get_latest_frame(self):
        pass
