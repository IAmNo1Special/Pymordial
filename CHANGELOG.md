# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2026-01-25

### Changed
- Converted `PymordialApp`, `PymordialScreen`, and `PymordialElement` to pure dataclasses.
- **Import refactor**: Removed unnecessary `TYPE_CHECKING` blocks and `from __future__ import annotations` across core modules; moved internal inter-core imports to top-level for better clarity.
- **Blueprint Cleanup**:
    - Removed `basicConfig` from device blueprints (`PymordialBridgeDevice`, `PymordialVisionDevice`, `PymordialEmulatorDevice`).
    - Aligned `PymordialEmulatorDevice` state machine to be an instance attribute.
- **Testing**:
    - Added rigorous testing for dataclass validation and state machine logic.
- Moved `element.py` from `core/blueprints/` to `ui/`.

## [0.4.0] - 2026-01-23

### Changed
- **Platform Agnostic Core**:
    - Removed all Android-specific logical dependencies (package name, ADB commands) from core.
    - Cleaned `configs.yaml` of ADB/BlueStacks settings; now only contains generic `app`, `element`, `controller` config.
    - Updated `PymordialElement` to default to 1920x1080 resolution if not specified, removing dependency on BlueStacks config.
- **Configuration**:
    - Updated `pymordial_config.example.yaml` to match the new minimal schema.
s    - Restored `ConcreteApp` fixtures to verify core lifecycle logic without platform dependencies.
- **Build**:
    - Updated `uv-build` dependency constraints.

## [0.3.1] - 2026-01-21

### Changed
- **Documentation**: Clarified platform agnostic design in README; project now marketed as "Extensible Automation Framework".
- **Config**: Removed `easyocr` config section from `configs.yaml` and `pymordial_config.example.yaml`.

## [0.3.0] - 2026-01-20

### Added
- **Unified Vision System**: Introduced `PymordialUiDevice` (`devices/ui_device.py`) as the single source of truth for all visual interactions (Images, Text, Pixels).
- **H.264 Streaming**: Low-latency screen streaming using `screenrecord` and PyAV decoding.
- **Typed Configuration**: Full `TypedDict` support for `pymordial_config.yaml` with rigorous validation.
- **Extraction Strategies**: `DefaultExtractStrategy` and `RevomonTextStrategy` for OCR preprocessing.

### Changed
- **Architecture Refactor**:
    - `core/element.py` → `core/blueprints/element.py`
    - `ocr/extract_strategies.py` → `devices/extract_strategies.py`
    - `utils/state_machine.py` → `core/state_machine.py`
- **Controller API**: `PymordialController` now delegates all UI logic to `self.ui` (`PymordialUiDevice`).
- **Dependencies**: Removed hard dependency on `easyocr`.

### Removed
- `controller/image_controller.py`: Merged into `PymordialUiDevice`.
- `controller/text_controller.py`: Merged into `PymordialUiDevice`.
- `ocr/` directory: Consolidated into `devices/` and `core/blueprints/`.

## [0.2.0] - 2025-12-10

### Added
- **BlueStacks Support**: Full end-to-end control of BlueStacks 5 (open, close, window management).
- **App Lifecycle**: `PymordialApp` with `StateMachine` (CLOSED → LOADING → READY).
- **Configuration System**: `pymordial_config.yaml` for user overrides.
- **Image/Text Controllers**: Initial separate controllers for template matching and OCR.

### Changed
- **ADB Module**: Removed bundled ADB binaries; now uses pure-Python `adb-shell`.
- **Controller Refactor**: Improved `find_element`, `click_element` APIs.

## [0.1.1] - 2025-11-30

### Fixed
- Minor bug fixes and internal improvements.

## [0.1.0] - 2025-11-30

### Added
- **Initial Release**: Core automation framework.
- **ADB Integration**: Pure Python ADB communication via `adb-shell`.
- **Screen Capture**: Basic screencap via `screencap -p`.
- **Element Types**: `PymordialImage`, `PymordialPixel`, `PymordialText`.
- **Documentation**: Initial README, examples, and tests.
