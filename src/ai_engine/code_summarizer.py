"""
Code Summarizer Module
Generate natural language explanations using AI
"""

from typing import Dict, List, Optional
import re
from src.utils.logger import logger

class CodeSummarizer:
    """
    Generate code summaries and explanations
    
    Note: This implementation uses rule-based summarization.
    For production, integrate with Hugging Face Transformers or GPT models.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.use_ai_model = config['ai'].get('use_local_model', False)
        
        # Initialize AI model if configured
        if self.use_ai_model:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize AI model (placeholder for actual model loading)"""
        try:
            # In production, load actual model:
            # from transformers import AutoTokenizer, AutoModel
            # self.tokenizer = AutoTokenizer.from_pretrained('microsoft/codebert-base')
            # self.model = AutoModel.from_pretrained('microsoft/codebert-base')
            logger.info("AI model initialized (placeholder)")
        except Exception as e:
            logger.warning(f"Could not initialize AI model: {e}")
            logger.info("Falling back to rule-based summarization")
    
    def summarize_function(self, func_data: Dict, content: str = None) -> str:
        """
        Generate natural language summary for a function
        
        Args:
            func_data: Function metadata from AST
            content: Optional function source code
            
        Returns:
            Natural language summary
        """
        name = func_data.get('name', 'unknown')
        params = func_data.get('parameters', [])
        returns = func_data.get('returns')
        docstring = func_data.get('docstring')
        calls = func_data.get('calls', [])
        is_async = func_data.get('is_async', False)
        
        # If docstring exists, use it
        if docstring:
            return f"Function '{name}': {docstring}"
        
        # Otherwise, generate summary
        summary_parts = []
        
        # Async indicator
        if is_async:
            summary_parts.append("This asynchronous function")
        else:
            summary_parts.append("This function")
        
        # Infer purpose from name
        purpose = self._infer_purpose_from_name(name)
        if purpose:
            summary_parts.append(purpose)
        
        # Parameters
        if params:
            filtered_params = [p for p in params if p not in ['self', 'cls']]
            if filtered_params:
                summary_parts.append(f"takes {len(filtered_params)} parameter(s): {', '.join(filtered_params)}")
        else:
            summary_parts.append("takes no parameters")
        
        # Returns
        if returns:
            summary_parts.append(f"and returns {returns}")
        
        # Function calls
        if calls and len(calls) <= 5:
            summary_parts.append(f"It calls: {', '.join(calls[:5])}")
        elif calls:
            summary_parts.append(f"It makes {len(calls)} function calls")
        
        return '. '.join(summary_parts) + '.'
    
    def summarize_class(self, class_data: Dict) -> str:
        """
        Generate natural language summary for a class
        
        Args:
            class_data: Class metadata from AST
            
        Returns:
            Natural language summary
        """
        name = class_data.get('name', 'unknown')
        bases = class_data.get('bases', [])
        methods = class_data.get('method_names', [])
        docstring = class_data.get('docstring')
        
        # If docstring exists, use it
        if docstring:
            return f"Class '{name}': {docstring}"
        
        # Generate summary
        summary_parts = [f"Class '{name}'"]
        
        # Inheritance
        if bases:
            summary_parts.append(f"inherits from {', '.join(bases)}")
        
        # Methods
        if methods:
            summary_parts.append(f"and implements {len(methods)} methods")
            
            # List key methods
            key_methods = [m for m in methods if not m.startswith('_')]
            if key_methods:
                summary_parts.append(f"including: {', '.join(key_methods[:5])}")
        
        # Infer purpose
        purpose = self._infer_purpose_from_name(name)
        if purpose:
            summary_parts.append(f". {purpose}")
        
        return ' '.join(summary_parts) + '.'
    
    def summarize_file(self, parsed_data: Dict) -> str:
        """
        Generate natural language summary for an entire file
        
        Args:
            parsed_data: Complete parsed file data
            
        Returns:
            Natural language summary
        """
        filepath = parsed_data.get('filepath', 'unknown')
        filename = filepath.split('/')[-1]
        
        functions = parsed_data.get('functions', [])
        classes = parsed_data.get('classes', [])
        imports = parsed_data.get('imports', [])
        
        summary_parts = [f"File '{filename}'"]
        
        # Classes
        if classes:
            class_names = [c['name'] for c in classes]
            summary_parts.append(f"defines {len(classes)} class(es): {', '.join(class_names)}")
        
        # Functions
        if functions:
            # Filter out methods
            standalone_funcs = [f for f in functions if not f.get('parent_class')]
            if standalone_funcs:
                summary_parts.append(f"and {len(standalone_funcs)} function(s)")
        
        # Imports
        if imports:
            summary_parts.append(f"It imports {len(imports)} module(s)")
        
        # Infer file purpose
        file_purpose = self._infer_file_purpose(filename, classes, functions)
        if file_purpose:
            summary_parts.append(f". {file_purpose}")
        
        return ' '.join(summary_parts) + '.'
    
    def _infer_purpose_from_name(self, name: str) -> Optional[str]:
        """Infer purpose from function/class name"""
        name_lower = name.lower()
        
        # Common patterns
        if name_lower.startswith('get') or name_lower.startswith('fetch'):
            return "retrieves data"
        elif name_lower.startswith('set') or name_lower.startswith('update'):
            return "updates data"
        elif name_lower.startswith('create') or name_lower.startswith('make'):
            return "creates new data or objects"
        elif name_lower.startswith('delete') or name_lower.startswith('remove'):
            return "removes data"
        elif name_lower.startswith('validate') or name_lower.startswith('check'):
            return "validates data or conditions"
        elif name_lower.startswith('calculate') or name_lower.startswith('compute'):
            return "performs calculations"
        elif name_lower.startswith('parse') or name_lower.startswith('process'):
            return "processes data"
        elif name_lower.startswith('save') or name_lower.startswith('write'):
            return "saves or writes data"
        elif name_lower.startswith('load') or name_lower.startswith('read'):
            return "loads or reads data"
        elif 'handler' in name_lower or 'handle' in name_lower:
            return "handles events or requests"
        elif 'manager' in name_lower:
            return "manages resources or operations"
        elif 'controller' in name_lower:
            return "controls application logic"
        elif 'helper' in name_lower or 'util' in name_lower:
            return "provides utility functions"
        
        return None
    
    def _infer_file_purpose(self, filename: str, classes: List, functions: List) -> Optional[str]:
        """Infer file purpose from name and contents"""
        name_lower = filename.lower()
        
        if 'test' in name_lower:
            return "This appears to be a test file"
        elif 'config' in name_lower or 'settings' in name_lower:
            return "This file contains configuration settings"
        elif 'util' in name_lower or 'helper' in name_lower:
            return "This file provides utility functions"
        elif 'model' in name_lower:
            return "This file defines data models"
        elif 'view' in name_lower:
            return "This file handles view logic"
        elif 'controller' in name_lower:
            return "This file contains controller logic"
        elif 'main' in name_lower or '__main__' in name_lower:
            return "This is the main entry point"
        elif classes and not functions:
            return "This file primarily defines classes"
        elif functions and not classes:
            return "This file primarily defines functions"
        
        return None
    
    def generate_documentation(self, parsed_data: Dict) -> Dict:
        """
        Generate complete documentation for a file
        
        Args:
            parsed_data: Complete parsed file data
            
        Returns:
            Structured documentation
        """
        return {
            'file_summary': self.summarize_file(parsed_data),
            'classes': [
                {
                    'name': cls['name'],
                    'summary': self.summarize_class(cls),
                    'methods': cls.get('method_names', [])
                }
                for cls in parsed_data.get('classes', [])
            ],
            'functions': [
                {
                    'name': func['name'],
                    'summary': self.summarize_function(func),
                    'parameters': func.get('parameters', []),
                    'returns': func.get('returns')
                }
                for func in parsed_data.get('functions', [])
                if not func.get('parent_class')  # Only standalone functions
            ]
        }