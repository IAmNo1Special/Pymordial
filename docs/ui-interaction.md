# UI Interaction

All UI interaction is handled through the `Controller`.

## Defining Elements

```python
from pymordial.ui.image import PymordialImage

play_btn = PymordialImage(
    label="Play Button",
    filepath="assets/play.png",
    confidence=0.8
)
```

## Operations

- `find_element(element)`: Returns (x, y) coordinates.
- `click_element(element)`: Finds and clicks.
- `is_element_visible(element)`: Boolean check.
