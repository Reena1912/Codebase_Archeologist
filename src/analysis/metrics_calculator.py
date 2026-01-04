"""
Metrics Calculator Module
Calculate various code metrics (LOC, complexity, etc.)
"""

from typing import Dict, List
from pathlib import Path
from src.utils.logger import logger

class MetricsCalculator:
    """Calculate code metrics"""
    
    def __init__(self):
        """Initialize metrics calculator"""
        pass
    
    def calculate_file_metrics(self, filepath: str, content: str, 
                               parsed_data: Dict) -> Dict:
        """
        Calculate comprehensive metrics for a file
        
        Args:
            filepath: Path to file
            content: File content
            parsed_data: Parsed AST data
            
        Returns:
            Dictionary with all metrics
        """
        try:
            # Basic line counts
            lines = content.split('\n')
            loc = len(lines)
            
            # Remove empty and comment lines for SLOC
            sloc = self._count_sloc(lines)
            
            # Comment lines
            comments = self._count_comments(lines)
            
            # Blank lines
            blank = loc - sloc - comments
            
            # Function and class counts
            total_functions = len(parsed_data.get('functions', []))
            total_classes = len(parsed_data.get('classes', []))
            
            # Average function length
            avg_function_length = self._calculate_avg_function_length(
                parsed_data.get('functions', [])
            )
            
            # Average class length
            avg_class_length = self._calculate_avg_class_length(
                parsed_data.get('classes', [])
            )
            
            # Import count
            total_imports = len(parsed_data.get('imports', []))
            
            # Documentation coverage
            doc_coverage = self._calculate_doc_coverage(parsed_data)
            
            return {
                'filepath': filepath,
                'lines_of_code': {
                    'total': loc,
                    'source': sloc,
                    'comments': comments,
                    'blank': blank,
                    'comment_ratio': round(comments / loc * 100, 2) if loc > 0 else 0,
                    'code_ratio': round(sloc / loc * 100, 2) if loc > 0 else 0
                },
                'structure': {
                    'functions': total_functions,
                    'classes': total_classes,
                    'imports': total_imports,
                    'avg_function_length': avg_function_length,
                    'avg_class_length': avg_class_length
                },
                'documentation': {
                    'coverage': doc_coverage,
                    'functions_with_docs': self._count_documented_functions(parsed_data),
                    'classes_with_docs': self._count_documented_classes(parsed_data)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics for {filepath}: {e}")
            return self._empty_metrics(filepath)
    
    def _count_sloc(self, lines: List[str]) -> int:
        """
        Count Source Lines of Code (non-empty, non-comment lines)
        
        Args:
            lines: List of code lines
            
        Returns:
            SLOC count
        """
        sloc = 0
        in_multiline_string = False
        
        for line in lines:
            stripped = line.strip()
            
            # Check for multiline strings
            if '"""' in stripped or "'''" in stripped:
                in_multiline_string = not in_multiline_string
                continue
            
            # Skip if in multiline string
            if in_multiline_string:
                continue
            
            # Skip empty lines and comments
            if stripped and not stripped.startswith('#'):
                sloc += 1
        
        return sloc
    
    def _count_comments(self, lines: List[str]) -> int:
        """
        Count comment lines
        
        Args:
            lines: List of code lines
            
        Returns:
            Comment line count
        """
        comments = 0
        in_docstring = False
        
        for line in lines:
            stripped = line.strip()
            
            # Multiline strings (docstrings)
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                comments += 1
                continue
            
            if in_docstring:
                comments += 1
                continue
            
            # Single line comments
            if stripped.startswith('#'):
                comments += 1
        
        return comments
    
    def _calculate_avg_function_length(self, functions: List[Dict]) -> float:
        """
        Calculate average function length
        
        Args:
            functions: List of function data
            
        Returns:
            Average length in lines
        """
        if not functions:
            return 0.0
        
        total_lines = sum(f.get('num_lines', 0) for f in functions)
        return round(total_lines / len(functions), 2)
    
    def _calculate_avg_class_length(self, classes: List[Dict]) -> float:
        """
        Calculate average class length
        
        Args:
            classes: List of class data
            
        Returns:
            Average length in lines
        """
        if not classes:
            return 0.0
        
        total_lines = sum(c.get('num_lines', 0) for c in classes)
        return round(total_lines / len(classes), 2)
    
    def _calculate_doc_coverage(self, parsed_data: Dict) -> float:
        """
        Calculate documentation coverage percentage
        
        Args:
            parsed_data: Parsed AST data
            
        Returns:
            Coverage percentage (0-100)
        """
        total_items = 0
        documented_items = 0
        
        # Count functions
        for func in parsed_data.get('functions', []):
            total_items += 1
            if func.get('docstring'):
                documented_items += 1
        
        # Count classes
        for cls in parsed_data.get('classes', []):
            total_items += 1
            if cls.get('docstring'):
                documented_items += 1
        
        if total_items == 0:
            return 0.0
        
        return round((documented_items / total_items) * 100, 2)
    
    def _count_documented_functions(self, parsed_data: Dict) -> int:
        """Count functions with docstrings"""
        return sum(1 for f in parsed_data.get('functions', []) 
                  if f.get('docstring'))
    
    def _count_documented_classes(self, parsed_data: Dict) -> int:
        """Count classes with docstrings"""
        return sum(1 for c in parsed_data.get('classes', []) 
                  if c.get('docstring'))
    
    def calculate_repository_metrics(self, all_files_metrics: List[Dict]) -> Dict:
        """
        Calculate aggregated metrics for entire repository
        
        Args:
            all_files_metrics: List of per-file metrics
            
        Returns:
            Aggregated metrics
        """
        if not all_files_metrics:
            return self._empty_repo_metrics()
        
        total_loc = sum(m['lines_of_code']['total'] for m in all_files_metrics)
        total_sloc = sum(m['lines_of_code']['source'] for m in all_files_metrics)
        total_comments = sum(m['lines_of_code']['comments'] for m in all_files_metrics)
        total_blank = sum(m['lines_of_code']['blank'] for m in all_files_metrics)
        
        total_functions = sum(m['structure']['functions'] for m in all_files_metrics)
        total_classes = sum(m['structure']['classes'] for m in all_files_metrics)
        total_imports = sum(m['structure']['imports'] for m in all_files_metrics)
        
        # Average documentation coverage
        avg_doc_coverage = sum(m['documentation']['coverage'] 
                              for m in all_files_metrics) / len(all_files_metrics)
        
        return {
            'total_files': len(all_files_metrics),
            'lines_of_code': {
                'total': total_loc,
                'source': total_sloc,
                'comments': total_comments,
                'blank': total_blank,
                'comment_ratio': round(total_comments / total_loc * 100, 2) if total_loc > 0 else 0
            },
            'structure': {
                'total_functions': total_functions,
                'total_classes': total_classes,
                'total_imports': total_imports,
                'avg_functions_per_file': round(total_functions / len(all_files_metrics), 2),
                'avg_classes_per_file': round(total_classes / len(all_files_metrics), 2)
            },
            'documentation': {
                'average_coverage': round(avg_doc_coverage, 2)
            },
            'per_language': self._calculate_language_metrics(all_files_metrics)
        }
    
    def _calculate_language_metrics(self, all_files_metrics: List[Dict]) -> Dict:
        """
        Calculate metrics broken down by language
        
        Args:
            all_files_metrics: List of per-file metrics
            
        Returns:
            Metrics by language
        """
        language_metrics = {}
        
        for metrics in all_files_metrics:
            filepath = metrics['filepath']
            ext = Path(filepath).suffix
            
            # Determine language
            language = self._get_language_from_extension(ext)
            
            if language not in language_metrics:
                language_metrics[language] = {
                    'files': 0,
                    'lines': 0,
                    'functions': 0,
                    'classes': 0
                }
            
            language_metrics[language]['files'] += 1
            language_metrics[language]['lines'] += metrics['lines_of_code']['total']
            language_metrics[language]['functions'] += metrics['structure']['functions']
            language_metrics[language]['classes'] += metrics['structure']['classes']
        
        return language_metrics
    
    def _get_language_from_extension(self, ext: str) -> str:
        """Map file extension to language name"""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }
        return language_map.get(ext, 'Unknown')
    
    def _empty_metrics(self, filepath: str) -> Dict:
        """Return empty metrics for failed calculation"""
        return {
            'filepath': filepath,
            'lines_of_code': {
                'total': 0,
                'source': 0,
                'comments': 0,
                'blank': 0,
                'comment_ratio': 0,
                'code_ratio': 0
            },
            'structure': {
                'functions': 0,
                'classes': 0,
                'imports': 0,
                'avg_function_length': 0,
                'avg_class_length': 0
            },
            'documentation': {
                'coverage': 0,
                'functions_with_docs': 0,
                'classes_with_docs': 0
            }
        }
    
    def _empty_repo_metrics(self) -> Dict:
        """Return empty repository metrics"""
        return {
            'total_files': 0,
            'lines_of_code': {
                'total': 0,
                'source': 0,
                'comments': 0,
                'blank': 0,
                'comment_ratio': 0
            },
            'structure': {
                'total_functions': 0,
                'total_classes': 0,
                'total_imports': 0,
                'avg_functions_per_file': 0,
                'avg_classes_per_file': 0
            },
            'documentation': {
                'average_coverage': 0
            },
            'per_language': {}
        }
    
    def get_metrics_summary(self, metrics: Dict) -> str:
        """
        Generate human-readable summary of metrics
        
        Args:
            metrics: Metrics dictionary
            
        Returns:
            Formatted summary string
        """
        loc = metrics['lines_of_code']
        struct = metrics['structure']
        doc = metrics['documentation']
        
        summary = f"""
Code Metrics Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Lines of Code:
  Total:    {loc['total']:>6} lines
  Source:   {loc['source']:>6} lines ({loc['code_ratio']}%)
  Comments: {loc['comments']:>6} lines ({loc['comment_ratio']}%)
  Blank:    {loc['blank']:>6} lines

Structure:
  Functions: {struct['functions']}
  Classes:   {struct['classes']}
  Imports:   {struct['imports']}

Documentation:
  Coverage: {doc['coverage']}%
  Functions with docs: {doc['functions_with_docs']}
  Classes with docs:   {doc['classes_with_docs']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return summary

# Example usage
if __name__ == "__main__":
    sample_code = """
import math

def calculate_area(radius):
    '''Calculate the area of a circle'''
    return math.pi * radius ** 2

def calculate_perimeter(radius):
    # Calculate perimeter
    return 2 * math.pi * radius

class Calculator:
    '''Simple calculator'''
    
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        '''Subtract two numbers'''
        return a - b
"""
    
    # Parse code first
    from src.analysis.ast_parser import ASTParser
    
    parser = ASTParser()
    parsed = parser.parse_file("test.py", sample_code)
    
    # Calculate metrics
    calculator = MetricsCalculator()
    metrics = calculator.calculate_file_metrics("test.py", sample_code, parsed)
    
    # Print summary
    print(calculator.get_metrics_summary(metrics))
    
    print("\nDetailed Metrics:")
    import json
    print(json.dumps(metrics, indent=2))