"""
Unit tests for AST Parser
"""

import pytest
from src.analysis.ast_parser import ASTParser

# Sample code for testing
SAMPLE_CODE = """
def add(a, b):
    '''Add two numbers'''
    return a + b

def subtract(a, b):
    '''Subtract b from a'''
    return a - b

class Calculator:
    '''Simple calculator'''
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

import math
from typing import List

global_var = 42
"""

def test_parser_initialization():
    """Test parser can be initialized"""
    parser = ASTParser()
    assert parser is not None
    assert parser.functions == []
    assert parser.classes == []

def test_parse_functions():
    """Test parsing functions"""
    parser = ASTParser()
    result = parser.parse_file("test.py", SAMPLE_CODE)
    
    assert result is not None
    assert 'functions' in result
    assert len(result['functions']) >= 2
    
    # Check function names
    func_names = [f['name'] for f in result['functions']]
    assert 'add' in func_names
    assert 'subtract' in func_names

def test_parse_classes():
    """Test parsing classes"""
    parser = ASTParser()
    result = parser.parse_file("test.py", SAMPLE_CODE)
    
    assert 'classes' in result
    assert len(result['classes']) >= 1
    
    calc_class = result['classes'][0]
    assert calc_class['name'] == 'Calculator'
    assert calc_class['docstring'] == 'Simple calculator'

def test_parse_imports():
    """Test parsing imports"""
    parser = ASTParser()
    result = parser.parse_file("test.py", SAMPLE_CODE)
    
    assert 'imports' in result
    assert len(result['imports']) >= 2
    
    # Check import types
    import_modules = [imp.get('modules') or [imp.get('module')] 
                     for imp in result['imports']]
    flat_imports = [item for sublist in import_modules for item in sublist if item]
    
    assert 'math' in flat_imports

def test_function_parameters():
    """Test extracting function parameters"""
    parser = ASTParser()
    result = parser.parse_file("test.py", SAMPLE_CODE)
    
    add_func = next((f for f in result['functions'] if f['name'] == 'add'), None)
    assert add_func is not None
    assert 'parameters' in add_func
    assert 'a' in add_func['parameters']
    assert 'b' in add_func['parameters']

def test_function_docstrings():
    """Test extracting docstrings"""
    parser = ASTParser()
    result = parser.parse_file("test.py", SAMPLE_CODE)
    
    add_func = next((f for f in result['functions'] if f['name'] == 'add'), None)
    assert add_func['docstring'] == 'Add two numbers'

def test_class_methods():
    """Test extracting class methods"""
    parser = ASTParser()
    result = parser.parse_file("test.py", SAMPLE_CODE)
    
    calc_class = result['classes'][0]
    assert 'method_names' in calc_class
    assert 'multiply' in calc_class['method_names']
    assert 'divide' in calc_class['method_names']

def test_syntax_error_handling():
    """Test handling of syntax errors"""
    parser = ASTParser()
    invalid_code = "def bad_function( # Missing closing paren"
    
    result = parser.parse_file("bad.py", invalid_code)
    
    # Should return empty result, not crash
    assert result is not None
    assert result['total_functions'] == 0
    assert result['total_classes'] == 0

def test_empty_file():
    """Test parsing empty file"""
    parser = ASTParser()
    result = parser.parse_file("empty.py", "")
    
    assert result is not None
    assert result['total_functions'] == 0
    assert result['total_classes'] == 0

def test_global_variables():
    """Test extracting global variables"""
    parser = ASTParser()
    result = parser.parse_file("test.py", SAMPLE_CODE)
    
    assert 'global_variables' in result
    var_names = [v['name'] for v in result['global_variables']]
    assert 'global_var' in var_names

if __name__ == "__main__":
    pytest.main([__file__, "-v"])