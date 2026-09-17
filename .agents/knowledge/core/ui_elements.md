---
type: UI Specification
title: "Pymordial Core — UI Elements & Perception Abstractions"
description: "UI component hierarchy and perceptual matching abstractions: UIElement, PymordialImage template matching, Pixel color verification, and TextElement OCR."
resource: package:pymordial.ui
tags: [pymordial, ui, element, image, pixel, text, template-matching, ocr]
status: stable
generated:
  by: human:IAmNo1Special
  at: 2026-09-16T12:00:00Z
verified:
  - by: human:IAmNo1Special
    at: 2026-09-16T12:00:00Z
sources:
  - id: pymordial-ui-source
    resource: package:pymordial.ui
    title: "Pymordial UI Module"
---

# Pymordial Core — UI Elements & Perception Abstractions

Pymordial models user interface elements declaratively to provide robust visual anchoring, tolerance to animation artifacts, and normalized cross-resolution support.

---

## 1. UI Element Base (`UIElement`)

Every interactive on-screen target inherits from `UIElement`:
- **Bounding Box Geometry**: Defined by `(x, y)` position and `(width, height)` size.
- **Search Region Windowing**: Enables constraining computer vision searches to specific sub-regions of the screen, drastically reducing latency and false-positive matches.
- **Wait & Find Primitives**: Provides `find()`, `wait_until_present()`, and `click()` semantics with configurable timeouts and polling intervals.

---

## 2. Perception Types

### 2.1 Template Matching (`PymordialImage`)
- **OpenCV Match Template**: Evaluates normalized cross-correlation (`cv2.TM_CCOEFF_NORMED`).
- **Confidence Thresholding**: Matches above configurable thresholds (default $\ge 0.80$) are accepted.
- **Search Region Guard**: Automatically ensures search window dimensions strictly exceed template asset dimensions to prevent OpenCV crop assertion failures.

### 2.2 Color & Pixel Verification (`PixelElement`)
- **Exact & Range Matching**: Verifies specific RGB/HSV pixel values or color distributions within bounding regions.
- **Fast State Checks**: Used for instantaneous state detection (e.g. active tab indicators, loading spinners, health gauge fullness).

### 2.3 Optical Character Recognition (`TextElement`)
- **Text Anchoring**: Uses configured OCR engines (Tesseract, PaddleOCR, or local models) to locate textual buttons and labels.
- **Fuzzy Matching**: Matches strings with Levenshtein distance tolerance for stylized game typography.

See also: [Architecture](./architecture.md) and [Device Blueprints](./device_blueprints.md).