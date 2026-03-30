"""Basic arithmetic functions: add, subtract, multiply, divide."""


def add(a: int | float, b: int | float) -> int | float:
    """Add two numbers and return the result."""
    return a + b


def subtract(a: int | float, b: int | float) -> int | float:
    """Subtract b from a and return the result."""
    return a - b


def multiply(a: int | float, b: int | float) -> int | float:
    """Multiply two numbers and return the result."""
    return a * b


def divide(a: int | float, b: int | float) -> int | float:
    """Divide a by b and return the result.
    
    Raises:
        ValueError: If b is 0 (division by zero).
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b