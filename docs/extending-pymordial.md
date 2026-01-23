# Extending Pymordial

To support a new platform (e.g. a new emulator or device), implement the abstract base classes.

## Implement Controller

Inherit from `PymordialController` and implement:
- `capture_screen()`: Return image data.
- `click_coord(x, y)`: Perform click.
- `open_app(name)`: Launch command.
- `close_app(name)`: Kill command.

## Implement App

Inherit from `PymordialApp`.
- Implement `open()` and `close()` to delegate to your controller.
