# Core Concepts

## Controller (`PymordialController`)
The central coordinator. It manages:
- **Devices**: Hardware or emulator connections.
- **Apps**: Registered applications.
- **Input**: Sending clicks, swipes, text.
- **Vision**: Finding elements on screen.

## App (`PymordialApp`)
Represents a specific application. It uses a **State Machine** to track lifecycle:
- `CLOSED`: App is not running.
- `LOADING`: App has been launched but not ready.
- `READY`: App is fully loaded and interactive.

## Element (`PymordialElement`)
A UI component to interact with.
- **Image**: Template matching.
- **Pixel**: Color verification.
- **Text**: OCR text finding.
