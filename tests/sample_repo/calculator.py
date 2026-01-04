"""
Sample Calculator Module
This is a sample codebase for testing the Codebase Archaeologist
"""

import math
from typing import Union

# Global variable (code smell)
calculation_history = []

class Calculator:
    """
    A simple calculator class with basic operations
    """
    
    def __init__(self):
        self.result = 0
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers"""
        result = a + b
        self.history.append(f"add: {a} + {b} = {result}")
        return result
    
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a"""
        result = a - b
        self.history.append(f"subtract: {a} - {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers"""
        result = a * b
        self.history.append(f"multiply: {a} * {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        """
        Divide a by b
        Raises ValueError if b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"divide: {a} / {b} = {result}")
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """Calculate base raised to exponent"""
        result = math.pow(base, exponent)
        self.history.append(f"power: {base}^{exponent} = {result}")
        return result
    
    def square_root(self, number: float) -> float:
        """Calculate square root"""
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = math.sqrt(number)
        self.history.append(f"sqrt: √{number} = {result}")
        return result
    
    def get_history(self):
        """Return calculation history"""
        return self.history
    
    def clear_history(self):
        """Clear calculation history"""
        self.history = []
    
    # Long function (code smell) - cyclomatic complexity
    def complex_calculation(self, a, b, c, d, e, operation):
        """
        Perform complex calculation based on operation
        This function has high cyclomatic complexity (code smell)
        """
        result = 0
        
        if operation == 'add_all':
            result = a + b + c + d + e
        elif operation == 'multiply_all':
            result = a * b * c * d * e
        elif operation == 'mixed1':
            result = (a + b) * (c - d) / e
        elif operation == 'mixed2':
            result = math.pow(a, 2) + math.pow(b, 2) + c
        elif operation == 'mixed3':
            result = (a * b) / (c + d) - e
        elif operation == 'average':
            result = (a + b + c + d + e) / 5
        elif operation == 'weighted_avg':
            result = (a * 0.1) + (b * 0.2) + (c * 0.3) + (d * 0.2) + (e * 0.2)
        elif operation == 'sum_of_squares':
            result = a**2 + b**2 + c**2 + d**2 + e**2
        elif operation == 'product_sum':
            result = (a * b) + (c * d) + e
        elif operation == 'custom1':
            if a > 10:
                result = a * b
            elif a > 5:
                result = a + b
            else:
                result = a - b
        else:
            result = 0
        
        # Magic number (code smell)
        if result > 1000:
            result = result * 0.95  # Apply 5% discount for large results
        
        return result

# Function without docstring (code smell)
def unused_function(x, y):
    return x + y

def validate_input(value: Union[int, float]) -> bool:
    """Validate numeric input"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

# Duplicate function (code smell - similar to Calculator.add)
def add_numbers(a, b):
    """Add two numbers - duplicate of Calculator.add"""
    return a + b