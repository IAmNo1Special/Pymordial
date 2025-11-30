"""Tests for PymordialElement abstract base class."""

from unittest.mock import Mock

from pymordial.core.pymordial_element import PymordialElement


class ConcretePymordialElement(PymordialElement):
    """Concrete implementation for testing."""

    def match(self, bs_controller, image_controller, screenshot=None):
        """Concrete implementation of match."""
        return (100, 100)


def test_pymordial_element_init(mock_config):
    """Test element initialization."""
    element = ConcretePymordialElement(
        label="TestElement",
        bluestacks_resolution=(1280, 720),
        position=(100, 200),
        size=(50, 30),
    )

    assert element.label == "testelement"  # Labels are lowercase
    assert element.bluestacks_resolution == (1280, 720)
    assert element.position == (100, 200)
    assert element.size == (50, 30)


def test_pymordial_element_label_lowercase(mock_config):
    """Test that labels are converted to lowercase."""
    element = ConcretePymordialElement(
        label="MyButton", bluestacks_resolution=(1280, 720)
    )

    assert element.label == "mybutton"


def test_region_property_with_position_and_size(mock_config):
    """Test region property calculation."""
    element = ConcretePymordialElement(
        label="test",
        bluestacks_resolution=(1280, 720),
        position=(100, 200),
        size=(50, 30),
    )

    region = element.region
    assert region == (100, 200, 150, 230)  # (left, top, right, bottom)


def test_region_property_without_position(mock_config):
    """Test region returns None when position not set."""
    element = ConcretePymordialElement(
        label="test", bluestacks_resolution=(1280, 720), size=(50, 30)
    )

    assert element.region is None


def test_region_property_without_size(mock_config):
    """Test region returns None when size not set."""
    element = ConcretePymordialElement(
        label="test", bluestacks_resolution=(1280, 720), position=(100, 200)
    )

    assert element.region is None


def test_center_property_with_position_and_size(mock_config):
    """Test center property calculation."""
    element = ConcretePymordialElement(
        label="test",
        bluestacks_resolution=(1280, 720),
        position=(100, 200),
        size=(50, 30),
    )

    center = element.center
    assert center == (125, 215)  # (x + w//2, y + h//2)


def test_center_property_with_only_position(mock_config):
    """Test center returns position when size not set."""
    element = ConcretePymordialElement(
        label="test", bluestacks_resolution=(1280, 720), position=(100, 200)
    )

    assert element.center == (100, 200)


def test_center_property_without_position(mock_config):
    """Test center returns None when position not set."""
    element = ConcretePymordialElement(label="test", bluestacks_resolution=(1280, 720))

    assert element.center is None


def test_match_abstract_method(mock_config):
    """Test that match is implemented in concrete class."""
    element = ConcretePymordialElement(label="test", bluestacks_resolution=(1280, 720))

    result = element.match(Mock(), Mock())
    assert result == (100, 100)
    assert result == (100, 100)
