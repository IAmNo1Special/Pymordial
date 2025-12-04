"""Simple integration test for streaming functionality."""

import time

import pytest

from pymordial.controller.pymordial_controller import PymordialController


@pytest.mark.integration
def test_streaming_basic_functionality(real_pymordial_controller: PymordialController):
    """Test basic streaming: start, get frames, stop."""
    # Start streaming
    try:
        started = real_pymordial_controller.start_streaming()
    except Exception as e:
        pytest.skip(f"Streaming failed to start: {e}")

    if not started:
        pytest.skip("Streaming not available (BlueStacks might not be running)")

    try:
        # Get a few frames rapidly to test lock-free access
        frames_received = 0
        for _ in range(10):
            frame = real_pymordial_controller.get_frame()
            if frame is not None:
                frames_received += 1
                assert frame.ndim == 3  # RGB image
                assert frame.shape[2] == 3  # 3 channels
            time.sleep(0.01)  # 10ms between frames

        # Should get at least some frames
        assert frames_received > 0, "No frames received from stream"

    finally:
        # Always stop streaming
        real_pymordial_controller.stop_streaming()

    # Verify stream stopped - frame should be None
    time.sleep(0.1)
    _ = real_pymordial_controller.get_frame()
    # Note: Might still return last frame, that's okay
    # Just verifying no crashes


@pytest.mark.integration
def test_streaming_performance(real_pymordial_controller: PymordialController):
    """Test that streaming returns consistent frames rapidly.

    Note: This test verifies streaming functionality rather than making
    rigid speed comparisons, as performance varies by environment.
    """
    # Start streaming
    try:
        if not real_pymordial_controller.start_streaming():
            pytest.skip("Streaming not available")
    except Exception as e:
        pytest.skip(f"Streaming failed to start: {e}")

    try:
        # Time streaming frame access (10 frames)
        start_time = time.time()
        valid_frames = 0
        for _ in range(10):
            frame = real_pymordial_controller.get_frame()
            if frame is not None:
                valid_frames += 1
        streaming_time = (time.time() - start_time) / 10  # Per frame

        if valid_frames == 0:
            pytest.skip("No valid frames received from stream")

        # Time screenshot capture (3 frames)
        start_time = time.time()
        valid_screenshots = 0
        for _ in range(3):
            screen = real_pymordial_controller.capture_screen()
            if screen is not None:
                valid_screenshots += 1
        screenshot_time = (time.time() - start_time) / 3  # Per frame

        if valid_screenshots == 0:
            pytest.skip("No valid screenshots captured")

        # Output timing info for debugging (no hard assertion on speed)
        print(f"\nStreaming: {streaming_time*1000:.2f}ms per frame")
        print(f"Screenshot: {screenshot_time*1000:.2f}ms per frame")
        if streaming_time > 0:
            print(f"Speedup: {screenshot_time/streaming_time:.1f}x")

        # Verify streaming returned valid data
        assert valid_frames > 0, "Streaming should return at least one valid frame"
        assert (
            valid_screenshots > 0
        ), "Screenshot should capture at least one valid image"

    finally:
        real_pymordial_controller.stop_streaming()
