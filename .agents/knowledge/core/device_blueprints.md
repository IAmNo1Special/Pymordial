---
type: Device Specification
title: "Pymordial Core — Device Blueprints & Abstraction Interfaces"
description: "Abstract device blueprints defining driver contracts: BridgeDevice, EmulatorDevice, VisionDevice, and OCRDevice."
resource: package:pymordial.core.blueprints
tags: [pymordial, blueprints, bridge, emulator, vision, ocr, driver-contracts]
status: stable
generated:
  by: human:IAmNo1Special
  at: 2026-09-16T12:00:00Z
verified:
  - by: human:IAmNo1Special
    at: 2026-09-16T12:00:00Z
sources:
  - id: pymordial-blueprints-source
    resource: package:pymordial.core.blueprints
    title: "Pymordial Core Blueprints"
---

# Pymordial Core — Device Blueprints & Abstraction Interfaces

Pymordial enforces clean inversion of control by specifying driver interfaces through abstract base classes (`blueprints`). Specific hardware backends (physical Android devices via `PymordialDroid` or emulators via `PymordialBlue`) implement these contracts.

---

## 1. Bridge Device (`BridgeDevice`)

Defines the low-level communication and input injection channel:
- **Lifecycle**: `connect()`, `disconnect()`, `is_connected()`.
- **Input Injection**: `tap(x, y)`, `swipe(x1, y1, x2, y2, duration)`, `key_event(code)`.
- **Display Frame Capture**: `capture_screenshot() -> bytes`.
- **Process Management**: `start_app(package, activity)`, `stop_app(package)`.

---

## 2. Emulator Device (`EmulatorDevice`)

Specialized blueprint extending bridge capabilities for desktop Android virtualization:
- **Instance Management**: `launch_instance(instance_name)`, `terminate_instance(instance_name)`.
- **Port Mapping**: Auto-discovers dynamic ADB ports assigned to virtual machines.
- **Window Management**: Integrates with OS window handles for desktop-level frame capture.

---

## 3. Vision Device (`VisionDevice`)

Provides perceptual analysis routines:
- **Template Matching**: `match_template(image, template, threshold, region) -> Optional[Tuple[int, int]]`.
- **Feature Detection**: SIFT/ORB keypoint matching for scale-invariant visual anchors.

---

## 4. OCR Device (`OCRDevice`)

Standardized text recognition contract:
- **Text Extraction**: `extract_text(image, region) -> str`.
- **Word Coordinates**: `find_text_bounds(image, text, threshold) -> List[BoundingBox]`.

See also: [Architecture](./architecture.md) and [Configuration](./configuration.md).