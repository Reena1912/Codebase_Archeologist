"""
Unit tests for Complexity Analyzer and Code Analysis modules
"""

import pytest
from src.analysis.complexity_analyzer import ComplexityAnalyzer
from src.analysis.metrics_calculator import MetricsCalculator
from src.analysis.ast_parser import ASTParser
from src.extraction.code_smell_detector import CodeSmellDetector
from src.extraction.dependency_extractor import DependencyExtractor

# Sample code for testing
SIMPLE_CODE = """
def add(a, b):
    '''Add two numbers'''
    return a + b
"""

COMPLEX_CODE = """
def complex_function(data, flag1, flag2, flag3):
    result = 0
    if flag1:
        if data > 10:
            for i in range(data):
                if i % 2 == 0:
                    result += i
                else:
                    result -= i
        elif data > 5:
            while result < 100:
                result += 1
                if result % 10 == 0:
                    break
        else:
            try:
                result = data / 0
            except:
                result = -1
    elif flag2:
        for i in range(data):
            for j in range(i):
                if i + j > 10:
                    result += i * j
    elif flag3:
        result = data ** 2
    else:
        result = data
    return result
"""

CODE_WITH_SMELLS = """
# Global variable (smell)
global_counter = 0

def very_long_function(a, b, c, d, e, f, g):
    '''Function with too many parameters'''
    x = a + b
    y = c + d
    z = e + f
    result = x * y * z * g
    
    # Magic number
    if result > 42:
        result = 100
    
    temp1 = result + 1
    temp2 = result + 2
    temp3 = result + 3
    temp4 = result + 4
    temp5 = result + 5
    temp6 = result + 6
    temp7 = result + 7
    temp8 = result + 8
    temp9 = result + 9
    temp10 = result + 10
    
    final = temp1 + temp2 + temp3 + temp4 + temp5
    final += temp6 + temp7 + temp8 + temp9 + temp10
    
    return final

def unused_function():
    '''This function is never called'''
    return "I'm dead code"

class Calculator:
    def add(self, a, b):
        return a + b
"""


@pytest.fixture
def config():
    """Return test configuration"""
    return {
        'analysis': {
            'supported_languages': ['python'],
            'max_file_size_mb': 10,
            'exclude_dirs': ['__pycache__'],
            'exclude_extensions': ['.pyc']
        },
        'quality': {
            'max_complexity': 10,
            'max_function_length': 20,
            'max_class_length': 100,
            'duplicate_threshold': 0.8
        },
        'ai': {
            'use_local_model': False
        }
    }


class TestComplexityAnalyzer:
    """Test ComplexityAnalyzer class"""
    
    def test_analyzer_initialization(self, config):
        """Test analyzer can be initialized"""
        analyzer = ComplexityAnalyzer(config)
        assert analyzer is not None
        assert analyzer.max_complexity == 10
    
    def test_analyze_simple_code(self, config):
        """Test analyzing simple code"""
        analyzer = ComplexityAnalyzer(config)
        result = analyzer.analyze_file("test.py", SIMPLE_CODE)
        
        assert result is not None
        assert 'cyclomatic_complexity' in result
        assert 'maintainability_index' in result
    
    def test_complexity_metrics(self, config):
        """Test complexity metrics are calculated"""
        analyzer = ComplexityAnalyzer(config)
        result = analyzer.analyze_file("test.py", SIMPLE_CODE)
        
        cc = result['cyclomatic_complexity']
        assert 'average' in cc
        assert 'max' in cc
        assert cc['average'] >= 0
    
    def test_high_complexity_detection(self, config):
        """Test high complexity functions are flagged"""
        analyzer = ComplexityAnalyzer(config)
        result = analyzer.analyze_file("test.py", COMPLEX_CODE)
        
        cc = result['cyclomatic_complexity']
        # Complex function should have high complexity
        assert cc['average'] > 1
    
    def test_maintainability_index(self, config):
        """Test maintainability index calculation"""
        analyzer = ComplexityAnalyzer(config)
        result = analyzer.analyze_file("test.py", SIMPLE_CODE)
        
        mi = result['maintainability_index']
        assert 'score' in mi
        assert 'rank' in mi
        assert mi['score'] >= 0
    
    def test_empty_code(self, config):
        """Test analyzing empty code"""
        analyzer = ComplexityAnalyzer(config)
        result = analyzer.analyze_file("test.py", "")
        
        assert result is not None
        assert result['cyclomatic_complexity']['average'] == 0


class TestMetricsCalculator:
    """Test MetricsCalculator class"""
    
    def test_calculator_initialization(self):
        """Test calculator can be initialized"""
        calculator = MetricsCalculator()
        assert calculator is not None
    
    def test_calculate_file_metrics(self):
        """Test calculating file metrics"""
        calculator = MetricsCalculator()
        parser = ASTParser()
        
        parsed = parser.parse_file("test.py", SIMPLE_CODE)
        metrics = calculator.calculate_file_metrics("test.py", SIMPLE_CODE, parsed)
        
        assert metrics is not None
        assert 'lines_of_code' in metrics
        assert 'structure' in metrics
        assert 'documentation' in metrics
    
    def test_lines_of_code(self):
        """Test LOC calculation"""
        calculator = MetricsCalculator()
        parser = ASTParser()
        
        parsed = parser.parse_file("test.py", SIMPLE_CODE)
        metrics = calculator.calculate_file_metrics("test.py", SIMPLE_CODE, parsed)
        
        loc = metrics['lines_of_code']
        assert loc['total'] > 0
        assert loc['source'] > 0
    
    def test_documentation_coverage(self):
        """Test documentation coverage calculation"""
        calculator = MetricsCalculator()
        parser = ASTParser()
        
        parsed = parser.parse_file("test.py", SIMPLE_CODE)
        metrics = calculator.calculate_file_metrics("test.py", SIMPLE_CODE, parsed)
        
        doc = metrics['documentation']
        assert 'coverage' in doc
        # Simple code has docstring, so should have some coverage
        assert doc['coverage'] >= 0


class TestCodeSmellDetector:
    """Test CodeSmellDetector class"""
    
    def test_detector_initialization(self, config):
        """Test detector can be initialized"""
        detector = CodeSmellDetector(config)
        assert detector is not None
    
    def test_detect_smells(self, config):
        """Test code smell detection"""
        detector = CodeSmellDetector(config)
        parser = ASTParser()
        
        parsed = parser.parse_file("test.py", CODE_WITH_SMELLS)
        smells = detector.detect_smells(parsed, CODE_WITH_SMELLS)
        
        assert smells is not None
        assert 'smells' in smells
        assert 'total_smell_count' in smells
    
    def test_detect_too_many_parameters(self, config):
        """Test detection of functions with too many parameters"""
        detector = CodeSmellDetector(config)
        parser = ASTParser()
        
        parsed = parser.parse_file("test.py", CODE_WITH_SMELLS)
        smells = detector.detect_smells(parsed, CODE_WITH_SMELLS)
        
        many_params = smells['smells']['too_many_parameters']
        assert len(many_params) > 0
        assert many_params[0]['parameter_count'] > 5
    
    def test_detect_dead_code(self, config):
        """Test dead code detection"""
        detector = CodeSmellDetector(config)
        parser = ASTParser()
        
        parsed = parser.parse_file("test.py", CODE_WITH_SMELLS)
        smells = detector.detect_smells(parsed, CODE_WITH_SMELLS)
        
        dead_code = smells['smells']['dead_code']
        # unused_function should be detected
        func_names = [d['name'] for d in dead_code]
        assert 'unused_function' in func_names
    
    def test_detect_global_variables(self, config):
        """Test global variable detection"""
        detector = CodeSmellDetector(config)
        parser = ASTParser()
        
        parsed = parser.parse_file("test.py", CODE_WITH_SMELLS)
        smells = detector.detect_smells(parsed, CODE_WITH_SMELLS)
        
        global_vars = smells['smells']['global_variables']
        # global_counter should be detected (not a constant)
        var_names = [v['name'] for v in global_vars]
        assert 'global_counter' in var_names


class TestDependencyExtractor:
    """Test DependencyExtractor class"""
    
    def test_extractor_initialization(self):
        """Test extractor can be initialized"""
        extractor = DependencyExtractor()
        assert extractor is not None
    
    def test_extract_dependencies(self):
        """Test dependency extraction"""
        extractor = DependencyExtractor()
        parser = ASTParser()
        
        code1 = """
import os
from pathlib import Path
from module2 import helper
"""
        code2 = """
def helper():
    return "helper"
"""
        
        parsed1 = parser.parse_file("module1.py", code1)
        parsed2 = parser.parse_file("module2.py", code2)
        
        result = extractor.extract_dependencies([parsed1, parsed2])
        
        assert result is not None
        assert 'total_files' in result
        assert 'analysis' in result
        assert result['total_files'] == 2


class TestIntegration:
    """Integration tests combining multiple modules"""
    
    def test_full_analysis_pipeline(self, config):
        """Test complete analysis pipeline"""
        # Parse
        parser = ASTParser()
        parsed = parser.parse_file("test.py", COMPLEX_CODE)
        
        # Analyze complexity
        complexity_analyzer = ComplexityAnalyzer(config)
        complexity = complexity_analyzer.analyze_file("test.py", COMPLEX_CODE)
        
        # Calculate metrics
        metrics_calc = MetricsCalculator()
        metrics = metrics_calc.calculate_file_metrics("test.py", COMPLEX_CODE, parsed)
        
        # Detect smells
        smell_detector = CodeSmellDetector(config)
        smells = smell_detector.detect_smells(parsed, COMPLEX_CODE)
        
        # Verify all components work together
        assert parsed['total_functions'] > 0
        assert complexity['cyclomatic_complexity']['average'] > 0
        assert metrics['lines_of_code']['total'] > 0
        assert 'smells' in smells


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
