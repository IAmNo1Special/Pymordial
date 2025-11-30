"""Tests for ImageController."""

from unittest.mock import Mock, patch

from PIL import Image

from pymordial.controller.image_controller import ImageController
from pymordial.core.elements.pymordial_button import PymordialButton
from pymordial.state_machine import BluestacksState


def test_image_controller_init(mock_config):
    """Test ImageController initialization."""
    with patch("pymordial.controller.image_controller.ImageTextChecker"):
        controller = ImageController()
        assert controller.img_txt_checker is not None


def test_check_text(mock_config):
    """Test text checking in image."""
    with patch(
        "pymordial.controller.image_controller.ImageTextChecker"
    ) as mock_checker_class:
        controller = ImageController()
        mock_checker = mock_checker_class.return_value
        controller.img_txt_checker = mock_checker
        mock_checker.check_text.return_value = True

        result = controller.check_text(text_to_find="Hello", image_path=b"fake_image")

        assert result is True
        mock_checker.check_text.assert_called_once()


def test_read_text(mock_config):
    """Test reading text from image."""
    with patch(
        "pymordial.controller.image_controller.ImageTextChecker"
    ) as mock_checker_class:
        controller = ImageController()
        mock_checker = mock_checker_class.return_value
        controller.img_txt_checker = mock_checker
        mock_checker.read_text.return_value = "Sample Text"

        result = controller.read_text(image_path=b"fake_image")

        assert result == "Sample Text"
        mock_checker.read_text.assert_called_once()


def test_scale_img_to_screen(mock_config):
    """Test image scaling to screen."""
    with patch("pymordial.controller.image_controller.ImageTextChecker"):
        controller = ImageController()
        mock_screen = Image.new("RGB", (1280, 720))
        mock_template = Image.new("RGB", (100, 100))

        with patch(
            "pymordial.controller.image_controller.Image.open",
            return_value=mock_template,
        ):
            result = controller.scale_img_to_screen(
                image_path="template.png",
                screen_image=mock_screen,
                bluestacks_resolution=(1280, 720),
            )
            assert isinstance(result, Image.Image)


def test_check_pixel_color_exact_match(mock_config):
    """Test pixel color checking with exact match."""
    with patch("pymordial.controller.image_controller.ImageTextChecker"):
        controller = ImageController()
        test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))

        with patch(
            "pymordial.controller.image_controller.Image.open", return_value=test_image
        ):
            result = controller.check_pixel_color(
                target_coords=(50, 50),
                target_color=(255, 0, 0),
                image="test.png",
                tolerance=0,
            )
            assert result is True


def test_check_pixel_color_no_match(mock_config):
    """Test pixel color checking with no match."""
    with patch("pymordial.controller.image_controller.ImageTextChecker"):
        controller = ImageController()
        test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))

        with patch(
            "pymordial.controller.image_controller.Image.open", return_value=test_image
        ):
            result = controller.check_pixel_color(
                target_coords=(50, 50),
                target_color=(0, 255, 0),
                image="test.png",
                tolerance=0,
            )
            assert result is False


def test_check_pixel_color_with_tolerance(mock_config):
    """Test pixel color checking with tolerance."""
    with patch("pymordial.controller.image_controller.ImageTextChecker"):
        controller = ImageController()
        test_image = Image.new("RGB", (100, 100), color=(255, 0, 0))

        with patch(
            "pymordial.controller.image_controller.Image.open", return_value=test_image
        ):
            result = controller.check_pixel_color(
                target_coords=(50, 50),
                target_color=(250, 5, 5),
                image="test.png",
                tolerance=10,
            )
            assert result is True


def test_where_element_found(mock_config):
    """Test finding element successfully."""
    with patch("pymordial.controller.image_controller.ImageTextChecker"):
        controller = ImageController()
        element = PymordialButton(
            label="test", asset_path="test.png", bluestacks_resolution=(1280, 720)
        )
        mock_pymordial_controller = Mock()
        mock_pymordial_controller.bluestacks.bluestacks_state.current_state = (
            BluestacksState.READY
        )

        with patch.object(element, "match", return_value=(100, 200)):
            result = controller.where_element(
                pymordial_controller=mock_pymordial_controller,
                pymordial_element=element,
            )
            assert result == (100, 200)


def test_where_element_not_found(mock_config):
    """Test when element is not found."""
    with patch("pymordial.controller.image_controller.ImageTextChecker"):
        controller = ImageController()
        element = PymordialButton(
            label="test", asset_path="test.png", bluestacks_resolution=(1280, 720)
        )
        mock_pymordial_controller = Mock()
        mock_pymordial_controller.bluestacks.bluestacks_state.current_state = (
            BluestacksState.READY
        )

        with patch.object(element, "match", return_value=None):
            result = controller.where_element(
                pymordial_controller=mock_pymordial_controller,
                pymordial_element=element,
                max_retries=1,
            )
            assert result is None


def test_where_elements_first_found(mock_config):
    """Test finding first element from list."""
    with patch("pymordial.controller.image_controller.ImageTextChecker"):
        controller = ImageController()
        element1 = PymordialButton(
            label="test1", asset_path="test1.png", bluestacks_resolution=(1280, 720)
        )
        element2 = PymordialButton(
            label="test2", asset_path="test2.png", bluestacks_resolution=(1280, 720)
        )

        mock_pymordial_controller = Mock()
        mock_pymordial_controller.bluestacks.bluestacks_state.current_state = (
            BluestacksState.READY
        )

        # Mock where_element to return result for second element
        with patch.object(controller, "where_element") as mock_where:
            mock_where.side_effect = [None, (150, 250)]

            result = controller.where_elements(
                pymordial_controller=mock_pymordial_controller,
                ui_elements=[element1, element2],
            )

            # where_elements returns only coordinates of the found element
            assert result == (150, 250)


def test_where_elements_none_found(mock_config):
    """Test when no elements are found from list."""
    with patch("pymordial.controller.image_controller.ImageTextChecker"):
        controller = ImageController()
        element1 = PymordialButton(
            label="test1", asset_path="test1.png", bluestacks_resolution=(1280, 720)
        )

        mock_pymordial_controller = Mock()
        mock_pymordial_controller.bluestacks.bluestacks_state.current_state = (
            BluestacksState.READY
        )

        with patch.object(controller, "where_element", return_value=None):
            result = controller.where_elements(
                pymordial_controller=mock_pymordial_controller,
                ui_elements=[element1],
                max_tries=1,
            )
            assert result is None
