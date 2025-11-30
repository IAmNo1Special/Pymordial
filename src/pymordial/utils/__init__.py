"""
Pymordial utilities module.
"""


def validate_and_convert_int(value: int | str, param_name: str) -> int:
    """Validate and convert value to int if possible"""
    if not isinstance(value, int):
        try:
            value: int = int(value)
        except ValueError as e:
            raise ValueError(f"Error in {param_name}: {e}")
    return value
