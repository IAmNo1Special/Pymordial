from abc import ABC, abstractmethod
from logging import DEBUG, basicConfig, getLogger

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PIL import Image


class PymordialVisionDevice(ABC):
    logger = getLogger("PymordialVisionDevice")
    basicConfig(
        level=DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    @abstractmethod
    def scale_img_to_screen(self) -> "Image.Image":
        pass

    @abstractmethod
    def check_pixel_color(self) -> bool | None:
        pass

    @abstractmethod
    def where_element(self) -> tuple[int, int] | None:
        pass

    @abstractmethod
    def where_elements(self) -> tuple[int, int] | None:
        pass

    @abstractmethod
    def find_text(self) -> tuple[int, int] | None:
        pass

    @abstractmethod
    def check_text(self) -> bool:
        pass

    @abstractmethod
    def read_text(self) -> list[str]:
        pass
