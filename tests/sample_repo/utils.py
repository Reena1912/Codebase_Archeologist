"""
Utility functions for the sample calculator module
Used for testing Codebase Archaeologist
"""

import re
from typing import List, Union, Optional, Tuple
from functools import lru_cache

# Constants
PI = 3.14159265359
E = 2.71828182846
MAX_VALUE = 1000000
MIN_VALUE = -1000000


def format_number(number: float, decimal_places: int = 2) -> str:
    """
    Format a number with specified decimal places
    
    Args:
        number: The number to format
        decimal_places: Number of decimal places (default: 2)
        
    Returns:
        Formatted string representation
    """
    return f"{number:.{decimal_places}f}"


def is_valid_number(value: str) -> bool:
    """
    Check if a string represents a valid number
    
    Args:
        value: String to validate
        
    Returns:
        True if valid number, False otherwise
    """
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def parse_expression(expression: str) -> Tuple[float, str, float]:
    """
    Parse a simple math expression like "5 + 3"
    
    Args:
        expression: String expression to parse
        
    Returns:
        Tuple of (operand1, operator, operand2)
    """
    # Simple pattern for "number operator number"
    pattern = r'(-?\d+\.?\d*)\s*([+\-*/^])\s*(-?\d+\.?\d*)'
    match = re.match(pattern, expression.strip())
    
    if match:
        return float(match.group(1)), match.group(2), float(match.group(3))
    else:
        raise ValueError(f"Invalid expression: {expression}")


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


@lru_cache(maxsize=128)
def factorial(n: int) -> int:
    """
    Calculate factorial of n with caching
    
    Args:
        n: Non-negative integer
        
    Returns:
        Factorial of n
    """
    if n < 0:
        raise ValueError("Factorial not defined for negative numbers")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def calculate_percentage(value: float, percentage: float) -> float:
    """
    Calculate percentage of a value
    
    Args:
        value: Base value
        percentage: Percentage to calculate
        
    Returns:
        Calculated percentage
    """
    return (value * percentage) / 100


def round_to_nearest(value: float, nearest: float) -> float:
    """
    Round value to nearest specified interval
    
    Args:
        value: Value to round
        nearest: Interval to round to
        
    Returns:
        Rounded value
    """
    return round(value / nearest) * nearest


def get_statistics(numbers: List[float]) -> dict:
    """
    Calculate basic statistics for a list of numbers
    
    Args:
        numbers: List of numeric values
        
    Returns:
        Dictionary with mean, min, max, sum, count
    """
    if not numbers:
        return {
            'mean': 0,
            'min': 0,
            'max': 0,
            'sum': 0,
            'count': 0
        }
    
    return {
        'mean': sum(numbers) / len(numbers),
        'min': min(numbers),
        'max': max(numbers),
        'sum': sum(numbers),
        'count': len(numbers)
    }


class MathConstants:
    """Collection of mathematical constants"""
    
    PI = 3.14159265358979323846
    E = 2.71828182845904523536
    GOLDEN_RATIO = 1.61803398874989484820
    SQRT_2 = 1.41421356237309504880
    
    @classmethod
    def get_all(cls) -> dict:
        """Return all constants as dictionary"""
        return {
            'pi': cls.PI,
            'e': cls.E,
            'golden_ratio': cls.GOLDEN_RATIO,
            'sqrt_2': cls.SQRT_2
        }


# Example of a function with too many parameters (code smell)
def complex_operation(a: float, b: float, c: float, d: float, 
                      e: float, f: float, g: float, h: float) -> float:
    """
    Complex operation with too many parameters
    This is intentionally a code smell for testing
    """
    return a + b * c - d / e + f ** g - h


# Potentially unused function (dead code smell)
def internal_helper(x: float) -> float:
    """Internal helper function - may not be called"""
    return x * 2 + 1


if __name__ == "__main__":
    # Test the utilities
    print(f"Format: {format_number(3.14159, 3)}")
    print(f"Valid: {is_valid_number('42')}")
    print(f"Factorial 5: {factorial(5)}")
    print(f"Statistics: {get_statistics([1, 2, 3, 4, 5])}")
    print(f"Constants: {MathConstants.get_all()}")
