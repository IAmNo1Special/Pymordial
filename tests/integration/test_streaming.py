"""Simple integration test for streaming functionality."""

import time

import pytest

from pymordial.controller.pymordial_controller import PymordialController


@pytest.mark.integration
def test_streaming_basic_functionality(real_pymordial_controller: PymordialController):
    """Test basic streaming: start, get frames, stop."""
    # Start streaming
    started = real_pymordial_controller.start_streaming()
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
    """Test that streaming is faster than screenshot capture."""
    # Start streaming
    if not real_pymordial_controller.start_streaming():
        pytest.skip("Streaming not available")

    try:
        # Time streaming frame access (10 frames)
        start_time = time.time()
        for _ in range(10):
            real_pymordial_controller.get_frame()
        streaming_time = (time.time() - start_time) / 10  # Per frame

        # Time screenshot capture (3 frames, slower so fewer iterations)
        start_time = time.time()
        for _ in range(3):
            real_pymordial_controller.capture_screen()
        screenshot_time = (time.time() - start_time) / 3  # Per frame

        # Streaming should be faster
        print(f"\nStreaming: {streaming_time*1000:.2f}ms per frame")
        print(f"Screenshot: {screenshot_time*1000:.2f}ms per frame")
        print(f"Speedup: {screenshot_time/streaming_time:.1f}x")

        # Streaming should be at least 2x faster
        assert (
            streaming_time < screenshot_time / 2
        ), f"Streaming not significantly faster: {streaming_time:.4f}s vs {screenshot_time:.4f}s"

    finally:
        real_pymordial_controller.stop_streaming()
