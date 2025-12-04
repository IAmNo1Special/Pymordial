# Changelog

All notable changes to Pymordial will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-12-04

### Added
- **Real-Time Streaming API**: `start_streaming()`, `get_frame()`, `stop_streaming()` for low-latency frame access.
- **Convenience Methods**: `capture_screen()`, `click_element()`, `read_text()`, `check_text()` on `PymordialController`.
- **3-Tier Project Intelligence Docs**: `.protel/` directory with stakeholder, junior dev, and architect documentation.

### Changed
- **Element Dataclasses**: All elements now use `@dataclass(kw_only=True)` with comprehensive `__post_init__` validation.
- **Renamed Parameters**: `bluestacks_resolution` → `og_resolution`, `asset_path` → `filepath`.
- **Renamed `ImageTextChecker`** → `TextController` for clarity.
- **Moved `extract_strategy.py`** from `core/` to `ocr/` module.

### Removed
- **`PymordialButton`**: Deprecated element type. Use `PymordialImage` instead.
- **`.match()` Method**: Removed from elements. Use `ImageController.where_element()` instead.

### Fixed
- Integration test fixtures now properly skip when BlueStacks/ADB unavailable.
- All 163 tests passing.

## [0.1.1] - 2025-11-30

### Added
- **Initial Open Source Release** (MIT License)
- **Bundled Tesseract OCR**: Zero-configuration text extraction with portable binary included.
- **PymordialController Facade**: Unified API for ADB, BlueStacks, and Image recognition.
  - **17 Convenience Methods**: `tap()`, `swipe()`, `go_home()`, `read_text()`, `is_app_running()`, etc.
- **High-Performance Streaming**: Real-time H.264 video decoding (16-33ms latency) via `av`.
- **Robust State Management**: Automatic handling of `LOADING`, `READY`, and `CLOSED` states for apps and emulator.
- **Configuration System**: YAML-based config with `config.example.yaml` template.
- **Comprehensive Test Suite**: 100% pass rate on unit and integration tests.
- **Documentation**: Full suite including API Reference, Quickstart, and Architecture overview.

---

## Changelog Conventions

**When adding changes:**
1. Add to `[Unreleased]` section
2. Use categories: Added, Changed, Deprecated, Removed, Fixed, Security
3. On release: Move to versioned section with date

**Version numbering (SemVer):**
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: Breaking changes
- MINOR: New features (backwards-compatible)
- PATCH: Bug fixes (backwards-compatible)

**Example entry:**
```markdown
### Added
- New `smart_click()` method for element detection (#42)
```
