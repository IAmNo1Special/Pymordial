# Pymordial God Mode Architecture Review 🏛️

**Version**: 0.1.1  
**Analysis Date**: 2025-11-30

---

## 1. Executive Summary

Pymordial is a monolithic automation framework leveraging a Facade pattern to abstract ADB and OpenCV complexities. The codebase is clean, well-tested (100% coverage), and performant for its intended use case (BlueStacks automation).

**Grade**: A-

**Strengths**:
-   **Facade Implementation**: `PymordialController` effectively hides subsystem complexity.
-   **Performance**: H.264 streaming implementation is robust and low-latency.
-   **Testability**: High test coverage with effective mocking of ADB.

**Weaknesses**:
-   **Tight Coupling**: `BluestacksController` is tightly coupled to Windows-specific process management (`psutil`, `pywin32`).
-   **Hardcoded Resolution**: Assumption of 1920x1080 resolution permeates the `PymordialElement` logic.
-   **Sync-only API**: The entire API is synchronous, which may block the main thread during long operations.

## 2. Architectural Patterns

### 2.1. The Facade (`PymordialController`)
The central entry point. It instantiates and composes `AdbController`, `BluestacksController`, and `ImageController`. This is a classic Facade, simplifying the interface for the client.
*Critique*: Well-implemented. It prevents the "god object" anti-pattern by delegating logic to sub-controllers rather than implementing it directly.

### 2.2. Strategy Pattern (`ExtractStrategy`)
Used for OCR preprocessing. `PymordialExtractStrategy` defines the interface (`preprocess`, `tesseract_config`), and concrete classes (`RevomonTextStrategy`) implement game-specific logic.
*Critique*: Excellent use of Strategy. Allows easy extension for new games without modifying core OCR logic.

### 2.3. State Machine (`StateMachine`)
A generic `StateMachine` dataclass manages lifecycle states (`CLOSED` -> `LOADING` -> `READY`).
*Critique*: Essential for robustness. Prevents operations on a closed emulator. However, the state machine is currently somewhat implicit in `BluestacksController` logic rather than being a fully independent component.

## 3. Critical Analysis

### 3.1. Data Flow & Streaming
The streaming architecture (`AdbController.start_stream`) uses a producer-consumer model:
1.  **Producer Thread**: Reads raw bytes from `adb exec-out screenrecord`.
2.  **Consumer Thread**: Decodes frames using `av` (FFmpeg binding).
3.  **Storage**: Updates a `_latest_frame` variable using atomic assignment (GIL-protected).

*Risk*: If the consumer thread stalls (e.g., slow image processing on the main thread), the buffer might fill up. Currently, `queue_size=100` mitigates this, but frame dropping logic is implicit.

### 3.2. Dependency Injection
Dependencies (`adb_host`, `adb_port`) are injected via the constructor.
*Improvement*: `PymordialApp` instances are added via `add_app()`, but there's no formal Dependency Injection container. For a project this size, manual injection is acceptable.

## 4. Bottlenecks & Performance

-   **ADB Latency**: Standard `screencap` takes ~200ms. This is the primary bottleneck for non-streaming operations. The streaming implementation (~30ms) solves this but adds complexity.
-   **OCR Overhead**: Tesseract is CPU-intensive. Frequent `read_text()` calls will cap the bot's FPS.
    *Recommendation*: Use `check_text` (boolean existence) over `read_text` (full extraction) whenever possible.

## 5. Technical Debt & Refactoring

### Priority 1: Resolution Independence
**Issue**: `PymordialElement` takes absolute coordinates based on 1080p.
**Refactor**: Implement a coordinate scaling system. Store elements in normalized coordinates (0.0-1.0) and scale to the current device resolution at runtime.

### Priority 2: AsyncIO Support
**Issue**: All methods are blocking. `time.sleep()` is used extensively.
**Refactor**: Introduce `async def` versions of core methods. Use `asyncio.sleep()` and `aiofiles` for non-blocking I/O. This would allow running multiple bots in a single process.

### Priority 3: Cross-Platform Support
**Issue**: `BluestacksController` relies on `pywin32` for window management.
**Refactor**: Abstract window management into a `WindowProvider` interface. Implement `WindowsProvider` (current) and `LinuxProvider` (using `xdotool` or similar) to support Linux/macOS.

## 6. Verdict

Pymordial is a solid foundation. It follows good engineering practices and solves the core problem effectively. The next phase of development should focus on **scalability** (AsyncIO) and **flexibility** (Resolution independence).

---

## Outstanding Questions & Blockers

-   **Is multi-instance support planned?** The current architecture assumes one controller = one emulator. Managing multiple instances would require a higher-level `Orchestrator` class.
-   **What is the target scale?** If the goal is running 100 bots, the synchronous architecture will be a hard blocker. If the goal is 1-5 bots, it's fine.
