"""Tests for PymordialElement coordinate scaling to a new screen size."""

import pytest

from pymordial.ui.element import PymordialElement


def make_element(**kwargs):
    defaults = {
        "label": "button",
        "position": (960, 540),
        "size": (200, 100),
    }
    defaults.update(kwargs)
    return PymordialElement(**defaults)


class TestScaledPosition:
    def test_unchanged_at_original_resolution(self):
        element = make_element()
        assert element.scaled_position((1920, 1080)) == (960, 540)

    def test_scales_to_smaller_screen(self):
        element = make_element()
        assert element.scaled_position((1280, 720)) == (640, 360)

    def test_scales_to_larger_screen(self):
        element = make_element()
        assert element.scaled_position((3840, 2160)) == (1920, 1080)

    def test_axes_scale_independently(self):
        element = make_element()
        # Portrait target: x scales by 1080/1920, y by 1920/1080.
        assert element.scaled_position((1080, 1920)) == (540, 960)

    def test_respects_custom_og_resolution(self):
        element = make_element(
            position=(400, 300), size=(100, 50), og_resolution=(800, 600)
        )
        assert element.scaled_position((1600, 1200)) == (800, 600)

    def test_none_position_returns_none(self):
        element = make_element(position=None)
        assert element.scaled_position((1280, 720)) is None

    def test_original_values_unchanged(self):
        element = make_element()
        element.scaled_position((1280, 720))
        assert element.position == (960, 540)
        assert element.og_resolution == (1920, 1080)


class TestScaledSizeRegionCenter:
    def test_scaled_size(self):
        element = make_element()
        assert element.scaled_size((1280, 720)) == (133, 67)

    def test_scaled_region(self):
        element = make_element()
        assert element.scaled_region((1280, 720)) == (640, 360, 773, 427)

    def test_scaled_region_unchanged_at_original(self):
        element = make_element()
        assert element.scaled_region((1920, 1080)) == element.region

    def test_scaled_center(self):
        element = make_element()
        # Scaled box (640, 360, 773, 427): center mirrors the
        # position + size // 2 rule used by center.
        assert element.scaled_center((1280, 720)) == (706, 393)

    def test_scaled_center_unchanged_at_original(self):
        element = make_element()
        assert element.scaled_center((1920, 1080)) == element.center

    def test_scaled_center_without_size_falls_back_to_position(self):
        element = make_element(size=None)
        assert element.scaled_center((1280, 720)) == (640, 360)

    def test_scaled_region_without_size_returns_none(self):
        element = make_element(size=None)
        assert element.scaled_region((1280, 720)) is None
        assert element.scaled_size((1280, 720)) is None


class TestScaledResolutionValidation:
    @pytest.mark.parametrize(
        "bad_resolution",
        [
            [1280, 720],
            (1280,),
            (0, 720),
            (1280, -720),
            (1280.0, 720),
        ],
    )
    def test_invalid_resolution_raises(self, bad_resolution):
        element = make_element()
        with pytest.raises((TypeError, ValueError)):
            element.scaled_position(bad_resolution)
