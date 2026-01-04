"""
AST Parser Module
Parses Python code using Abstract Syntax Trees
"""

import ast
from typing import List, Dict, Optional, Set
from src.utils.logger import logger

class ASTParser:
    """Parse Python code using AST"""
    
    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.global_vars = []
        
    def parse_file(self, filepath: str, content: str) -> Dict:
        """
        Parse a Python file and extract structure
        
        Args:
            filepath: Path to the file
            content: File content
            
        Returns:
            Dictionary containing parsed information
        """
        try:
            tree = ast.parse(content, filename=filepath)
            
            # Reset collections
            self.functions = []
            self.classes = []
            self.imports = []
            self.global_vars = []
            
            # Analyze AST
            self._analyze_node(tree, filepath)
            
            return {
                'filepath': filepath,
                'functions': self.functions,
                'classes': self.classes,
                'imports': self.imports,
                'global_variables': self.global_vars,
                'total_functions': len(self.functions),
                'total_classes': len(self.classes)
            }
            
        except SyntaxError as e:
            logger.warning(f"Syntax error in {filepath}: {e}")
            return self._empty_result(filepath)
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            return self._empty_result(filepath)
    
    def _analyze_node(self, node: ast.AST, filepath: str, parent_class: str = None):
        """Recursively analyze AST nodes"""
        
        for child in ast.walk(node):
            # Extract functions
            if isinstance(child, ast.FunctionDef):
                func_info = self._extract_function(child, filepath, parent_class)
                self.functions.append(func_info)
            
            # Extract classes
            elif isinstance(child, ast.ClassDef):
                class_info = self._extract_class(child, filepath)
                self.classes.append(class_info)
                
                # Analyze methods within class
                for item in child.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = self._extract_function(item, filepath, child.name)
                        self.functions.append(method_info)
            
            # Extract imports
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                import_info = self._extract_import(child)
                self.imports.append(import_info)
            
            # Extract global variables
            elif isinstance(child, ast.Assign) and isinstance(node, ast.Module):
                var_info = self._extract_variable(child)
                if var_info:
                    self.global_vars.append(var_info)
    
    def _extract_function(self, node: ast.FunctionDef, filepath: str, 
                         parent_class: Optional[str] = None) -> Dict:
        """Extract function/method information"""
        
        # Get parameters
        args = [arg.arg for arg in node.args.args]
        
        # Get return annotation
        returns = ast.unparse(node.returns) if node.returns else None
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Calculate metrics
        num_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
        
        # Extract function calls
        calls = self._extract_calls(node)
        
        return {
            'name': node.name,
            'type': 'method' if parent_class else 'function',
            'parent_class': parent_class,
            'parameters': args,
            'returns': returns,
            'docstring': docstring,
            'line_start': node.lineno,
            'line_end': node.end_lineno,
            'num_lines': num_lines,
            'calls': calls,
            'decorators': [ast.unparse(d) for d in node.decorator_list],
            'is_async': isinstance(node, ast.AsyncFunctionDef)
        }
    
    def _extract_class(self, node: ast.ClassDef, filepath: str) -> Dict:
        """Extract class information"""
        
        # Get base classes
        bases = [ast.unparse(base) for base in node.bases]
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Count methods
        methods = [item for item in node.body if isinstance(item, ast.FunctionDef)]
        
        # Calculate metrics
        num_lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
        
        return {
            'name': node.name,
            'bases': bases,
            'docstring': docstring,
            'line_start': node.lineno,
            'line_end': node.end_lineno,
            'num_lines': num_lines,
            'num_methods': len(methods),
            'method_names': [m.name for m in methods],
            'decorators': [ast.unparse(d) for d in node.decorator_list]
        }
    
    def _extract_import(self, node) -> Dict:
        """Extract import information"""
        if isinstance(node, ast.Import):
            return {
                'type': 'import',
                'modules': [alias.name for alias in node.names],
                'aliases': {alias.name: alias.asname for alias in node.names if alias.asname}
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                'type': 'from_import',
                'module': node.module,
                'names': [alias.name for alias in node.names],
                'level': node.level
            }
    
    def _extract_variable(self, node: ast.Assign) -> Optional[Dict]:
        """Extract global variable information"""
        if node.targets:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                return {
                    'name': target.id,
                    'line': node.lineno
                }
        return None
    
    def _extract_calls(self, node: ast.FunctionDef) -> List[str]:
        """Extract function calls within a function"""
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls.append(ast.unparse(child.func))
        return list(set(calls))  # Remove duplicates
    
    def _empty_result(self, filepath: str) -> Dict:
        """Return empty result for failed parsing"""
        return {
            'filepath': filepath,
            'functions': [],
            'classes': [],
            'imports': [],
            'global_variables': [],
            'total_functions': 0,
            'total_classes': 0
        }

# Example usage
if __name__ == "__main__":
    sample_code = """
import math
from typing import List

def calculate_area(radius: float) -> float:
    '''Calculate circle area'''
    return math.pi * radius ** 2

class Calculator:
    '''Simple calculator class'''
    
    def add(self, a: int, b: int) -> int:
        '''Add two numbers'''
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        return a - b
"""
    
    parser = ASTParser()
    result = parser.parse_file("test.py", sample_code)
    
    print("Parsed Results:")
    print(f"Functions: {result['total_functions']}")
    print(f"Classes: {result['total_classes']}")
    print(f"Imports: {len(result['imports'])}")
    
    print("\nFunction Details:")
    for func in result['functions']:
        print(f"  - {func['name']} ({func['type']})")
    
    print("\nClass Details:")
    for cls in result['classes']:
        print(f"  - {cls['name']} with {cls['num_methods']} methods")