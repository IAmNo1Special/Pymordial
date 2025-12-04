"""Tests for Pymordial extract strategies."""

import numpy as np

from pymordial.ocr.extract_strategy import (
    DefaultExtractStrategy,
    RevomonTextStrategy,
)


def test_default_extract_strategy_preprocess(mock_config):
    """Test default strategy preprocessing."""
    strategy = DefaultExtractStrategy()

    # Create a simple test image
    image = np.ones((100, 100, 3), dtype=np.uint8) * 128

    result = strategy.preprocess(image)

    # Should return a processed numpy array
    assert isinstance(result, np.ndarray)
    # Should be grayscale after processing
    assert len(result.shape) == 2 or result.shape[2] == 1


def test_default_extract_strategy_tesseract_config(mock_config):
    """Test default strategy returns Tesseract config."""
    strategy = DefaultExtractStrategy()

    config = strategy.tesseract_config()

    assert isinstance(config, str)
    assert "--oem" in config
    assert "--psm" in config


def test_default_extract_strategy_postprocess_text(mock_config):
    """Test default strategy text postprocessing."""
    strategy = DefaultExtractStrategy()

    text = "  Sample Text  "
    result = strategy.postprocess_text(text)

    # Default implementation returns stripped text
    assert result == "Sample Text"


def test_revomon_text_strategy_init_default_mode(mock_config):
    """Test RevomonTextStrategy initialization with default mode."""
    strategy = RevomonTextStrategy()

    assert strategy.mode == "default"
    assert strategy.debug_output_dir is None


def test_revomon_text_strategy_init_move_mode(mock_config):
    """Test RevomonTextStrategy initialization with move mode."""
    strategy = RevomonTextStrategy(mode="move")

    assert strategy.mode == "move"


def test_revomon_text_strategy_init_level_mode(mock_config):
    """Test RevomonTextStrategy initialization with level mode."""
    strategy = RevomonTextStrategy(mode="level")

    assert strategy.mode == "level"


def test_revomon_text_strategy_preprocess(mock_config):
    """Test Revomon strategy preprocessing."""
    strategy = RevomonTextStrategy(mode="default")

    # Create a test image
    image = np.ones((100, 100, 3), dtype=np.uint8) * 128

    result = strategy.preprocess(image)

    assert isinstance(result, np.ndarray)


def test_revomon_text_strategy_tesseract_config_default(mock_config):
    """Test Revomon strategy Tesseract config for default mode."""
    strategy = RevomonTextStrategy(mode="default")

    config = strategy.tesseract_config()

    assert isinstance(config, str)


def test_revomon_text_strategy_tesseract_config_move(mock_config):
    """Test Revomon strategy Tesseract config for move mode."""
    strategy = RevomonTextStrategy(mode="move")

    config = strategy.tesseract_config()

    assert isinstance(config, str)
    # Move mode should have specific whitelist config


def test_revomon_text_strategy_postprocess_text(mock_config):
    """Test Revomon strategy text postprocessing."""
    strategy = RevomonTextStrategy(mode="default")

    text = "  Power  "
    result = strategy.postprocess_text(text)

    # Should clean up the text
    assert isinstance(result, str)


def test_revomon_text_strategy_postprocess_text_level_mode(mock_config):
    """Test Revomon strategy postprocessing in level mode."""
    strategy = RevomonTextStrategy(mode="level")

    text = "Lvl 42"
    result = strategy.postprocess_text(text)

    # Level mode should extract digits
    assert "42" in result or result.isdigit()


def test_revomon_text_strategy_preprocess_default_mode(mock_config):
    """Test preprocessing in default mode with actual image manipulation."""
    strategy = RevomonTextStrategy(mode="default")

    # Create a test image with some content
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    result = strategy.preprocess(image)

    # Should return processed image
    assert isinstance(result, np.ndarray)
    # Should have upscaled dimensions (2x factor)
    assert result.shape[0] >= image.shape[0]


def test_revomon_text_strategy_preprocess_move_mode(mock_config):
    """Test preprocessing in move mode."""
    strategy = RevomonTextStrategy(mode="move")

    # Create a test image
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    result = strategy.preprocess(image)

    # Should return processed image
    assert isinstance(result, np.ndarray)
    # Move mode uses 3x upscale factor
    assert result.shape[0] >= image.shape[0] * 2


def test_revomon_text_strategy_preprocess_level_mode(mock_config):
    """Test preprocessing in level mode."""
    strategy = RevomonTextStrategy(mode="level")

    # Create a test image
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

    result = strategy.preprocess(image)

    # Should return processed image with cropping applied
    assert isinstance(result, np.ndarray)


def test_revomon_text_strategy_with_debug_output(mock_config, tmp_path):
    """Test Revomon strategy with debug output."""
    debug_dir = str(tmp_path / "debug")
    strategy = RevomonTextStrategy(mode="default", debug_output_dir=debug_dir)

    assert strategy.debug_output_dir == debug_dir

    # Process an image to trigger debug save
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    strategy.preprocess(image)

    # Check debug file was created
    import os

    assert os.path.exists(debug_dir)


def test_default_extract_strategy_color_inversion(mock_config):
    """Test default strategy handles color inversion."""
    strategy = DefaultExtractStrategy()

    # Create a dark image (should trigger inversion)
    dark_image = np.ones((100, 100, 3), dtype=np.uint8) * 50

    result = strategy.preprocess(dark_image)

    # Should be processed
    assert isinstance(result, np.ndarray)


def test_revomon_text_strategy_postprocess_move_mode(mock_config):
    """Test Revomon move mode postprocessing."""
    strategy = RevomonTextStrategy(mode="move")

    # Test with multi-line text
    text = "Phantom\nForce\n"
    result = strategy.postprocess_text(text)

    # Should combine lines and clean up
    assert "Phantom" in result
    assert "\n" not in result


def test_revomon_tesseract_config_level(mock_config):
    """Test level mode Tesseract config."""
    strategy = RevomonTextStrategy(mode="level")

    config = strategy.tesseract_config()

    # Should include digit whitelist
    assert "tessedit_char_whitelist" in config
    assert "0123456789" in config
    assert "0123456789" in config
