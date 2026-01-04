"""
Code Smell Detector Module
Detect common code smells and quality issues
"""

import re
from typing import Dict, List, Set
from collections import defaultdict
from difflib import SequenceMatcher
from src.utils.logger import logger

class CodeSmellDetector:
    """Detect code smells and anti-patterns"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_function_length = config['quality'].get('max_function_length', 50)
        self.max_class_length = config['quality'].get('max_class_length', 300)
        self.duplicate_threshold = config['quality'].get('duplicate_threshold', 0.8)
    
    def detect_smells(self, parsed_data: Dict, content: str) -> Dict:
        """
        Detect code smells in a file
        
        Args:
            parsed_data: Parsed AST data
            content: File content
            
        Returns:
            Dictionary containing detected smells
        """
        smells = {
            'long_functions': self._detect_long_functions(parsed_data),
            'long_classes': self._detect_long_classes(parsed_data),
            'missing_docstrings': self._detect_missing_docstrings(parsed_data),
            'too_many_parameters': self._detect_many_parameters(parsed_data),
            'dead_code': self._detect_dead_code(parsed_data),
            'magic_numbers': self._detect_magic_numbers(content),
            'global_variables': self._detect_global_vars(parsed_data)
        }
        
        # Calculate total smell count
        total_smells = sum(len(v) for v in smells.values() if isinstance(v, list))
        
        return {
            'filepath': parsed_data['filepath'],
            'smells': smells,
            'total_smell_count': total_smells
        }
    
    def _detect_long_functions(self, parsed_data: Dict) -> List[Dict]:
        """Detect functions that are too long"""
        long_functions = []
        
        for func in parsed_data.get('functions', []):
            num_lines = func.get('num_lines', 0)
            if num_lines > self.max_function_length:
                long_functions.append({
                    'name': func['name'],
                    'lines': num_lines,
                    'line_start': func.get('line_start'),
                    'severity': 'high' if num_lines > self.max_function_length * 2 else 'medium'
                })
        
        return long_functions
    
    def _detect_long_classes(self, parsed_data: Dict) -> List[Dict]:
        """Detect classes that are too long"""
        long_classes = []
        
        for cls in parsed_data.get('classes', []):
            num_lines = cls.get('num_lines', 0)
            if num_lines > self.max_class_length:
                long_classes.append({
                    'name': cls['name'],
                    'lines': num_lines,
                    'methods': cls.get('num_methods', 0),
                    'line_start': cls.get('line_start'),
                    'severity': 'high' if num_lines > self.max_class_length * 2 else 'medium'
                })
        
        return long_classes
    
    def _detect_missing_docstrings(self, parsed_data: Dict) -> List[Dict]:
        """Detect functions and classes without docstrings"""
        missing = []
        
        # Check functions
        for func in parsed_data.get('functions', []):
            if not func.get('docstring'):
                missing.append({
                    'type': 'function',
                    'name': func['name'],
                    'line': func.get('line_start')
                })
        
        # Check classes
        for cls in parsed_data.get('classes', []):
            if not cls.get('docstring'):
                missing.append({
                    'type': 'class',
                    'name': cls['name'],
                    'line': cls.get('line_start')
                })
        
        return missing
    
    def _detect_many_parameters(self, parsed_data: Dict, max_params: int = 5) -> List[Dict]:
        """Detect functions with too many parameters"""
        many_params = []
        
        for func in parsed_data.get('functions', []):
            params = func.get('parameters', [])
            # Filter out 'self' and 'cls'
            real_params = [p for p in params if p not in ['self', 'cls']]
            
            if len(real_params) > max_params:
                many_params.append({
                    'name': func['name'],
                    'parameter_count': len(real_params),
                    'parameters': real_params,
                    'line': func.get('line_start')
                })
        
        return many_params
    
    def _detect_dead_code(self, parsed_data: Dict) -> List[Dict]:
        """
        Detect potentially unused functions
        Note: This is a simplified detection - not 100% accurate
        """
        dead_code = []
        
        # Get all function names
        all_functions = {func['name'] for func in parsed_data.get('functions', [])}
        
        # Get all function calls across all functions
        all_calls = set()
        for func in parsed_data.get('functions', []):
            calls = func.get('calls', [])
            for call in calls:
                # Extract function name from call (handle method calls)
                call_name = call.split('.')[-1] if '.' in call else call
                all_calls.add(call_name)
        
        # Find functions that are never called
        # Exclude special methods and main functions
        for func_name in all_functions:
            if (func_name not in all_calls and 
                not func_name.startswith('__') and 
                func_name not in ['main', 'run', 'execute']):
                
                func_data = next((f for f in parsed_data['functions'] if f['name'] == func_name), None)
                if func_data:
                    dead_code.append({
                        'name': func_name,
                        'line': func_data.get('line_start'),
                        'note': 'Potentially unused (not called within file)'
                    })
        
        return dead_code
    
    def _detect_magic_numbers(self, content: str) -> List[Dict]:
        """Detect magic numbers (hardcoded numeric values)"""
        magic_numbers = []
        
        # Pattern to find numeric literals (excluding 0, 1, -1)
        pattern = r'\b(?<![\w.])\d{2,}\b(?![\w.])'
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip comments and strings
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                continue
            
            matches = re.finditer(pattern, line)
            for match in matches:
                number = match.group()
                if number not in ['0', '1', '10', '100']:  # Common acceptable numbers
                    magic_numbers.append({
                        'number': number,
                        'line': line_num,
                        'context': line.strip()[:50]
                    })
        
        return magic_numbers[:10]  # Limit to first 10
    
    def _detect_global_vars(self, parsed_data: Dict) -> List[Dict]:
        """Detect global variables (potential smell)"""
        global_vars = parsed_data.get('global_variables', [])
        
        # Filter out common constants (all uppercase)
        non_constants = [
            var for var in global_vars 
            if not var['name'].isupper() and var['name'] not in ['__name__', '__main__']
        ]
        
        return non_constants
    
    def detect_duplicates(self, all_parsed_data: List[Dict]) -> List[Dict]:
        """
        Detect duplicate or similar code across files
        
        Args:
            all_parsed_data: List of parsed data from all files
            
        Returns:
            List of duplicate code blocks
        """
        duplicates = []
        function_signatures = defaultdict(list)
        
        # Collect all function signatures
        for file_data in all_parsed_data:
            for func in file_data.get('functions', []):
                signature = f"{func['name']}_{len(func.get('parameters', []))}"
                function_signatures[signature].append({
                    'file': file_data['filepath'],
                    'function': func['name'],
                    'line': func.get('line_start')
                })
        
        # Find duplicates
        for signature, occurrences in function_signatures.items():
            if len(occurrences) > 1:
                duplicates.append({
                    'signature': signature.split('_')[0],
                    'occurrences': occurrences,
                    'count': len(occurrences)
                })
        
        return duplicates