"""
Prompt Templates for AI Code Analysis
Templates for generating prompts for LLMs (GPT, Claude, etc.)
"""

from typing import Dict, List

class PromptTemplates:
    """Collection of prompt templates for code analysis"""
    
    @staticmethod
    def function_summary_prompt(function_code: str, function_name: str, 
                                parameters: List[str]) -> str:
        """
        Generate prompt for function summarization
        
        Args:
            function_code: The complete function code
            function_name: Name of the function
            parameters: List of parameter names
            
        Returns:
            Formatted prompt string
        """
        params_str = ", ".join(parameters) if parameters else "no parameters"
        
        prompt = f"""Analyze this Python function and provide a concise summary:

Function Name: {function_name}
Parameters: {params_str}

Code:
```python
{function_code}
```

Provide a one-sentence summary that explains:
1. What the function does
2. What it returns (if applicable)
3. Any important side effects

Summary:"""
        
        return prompt
    
    @staticmethod
    def class_summary_prompt(class_code: str, class_name: str, 
                            methods: List[str]) -> str:
        """
        Generate prompt for class summarization
        
        Args:
            class_code: The complete class code
            class_name: Name of the class
            methods: List of method names
            
        Returns:
            Formatted prompt string
        """
        methods_str = ", ".join(methods) if methods else "no methods"
        
        prompt = f"""Analyze this Python class and provide a concise summary:

Class Name: {class_name}
Methods: {methods_str}

Code:
```python
{class_code}
```

Provide a one-sentence summary that explains:
1. The purpose of this class
2. What it represents or manages
3. Key responsibilities

Summary:"""
        
        return prompt
    
    @staticmethod
    def file_summary_prompt(file_content: str, filename: str,
                           functions: List[str], classes: List[str]) -> str:
        """
        Generate prompt for file summarization
        
        Args:
            file_content: Complete file content
            filename: Name of the file
            functions: List of function names
            classes: List of class names
            
        Returns:
            Formatted prompt string
        """
        funcs_str = ", ".join(functions[:5]) if functions else "none"
        classes_str = ", ".join(classes[:5]) if classes else "none"
        
        prompt = f"""Analyze this Python file and provide a concise summary:

Filename: {filename}
Functions: {funcs_str}
Classes: {classes_str}

Preview:
```python
{file_content[:500]}...
```

Provide a one-sentence summary that explains:
1. The main purpose of this file
2. What functionality it provides
3. How it fits into a larger system

Summary:"""
        
        return prompt
    
    @staticmethod
    def code_smell_explanation_prompt(smell_type: str, code_snippet: str,
                                      location: str) -> str:
        """
        Generate prompt for code smell explanation
        
        Args:
            smell_type: Type of code smell (e.g., "Long Function")
            code_snippet: The problematic code
            location: File and line number
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Explain this code smell and suggest improvements:

Code Smell Type: {smell_type}
Location: {location}

Code:
```python
{code_snippet}
```

Provide:
1. Why this is considered a code smell
2. Potential problems it could cause
3. A specific refactoring suggestion

Explanation:"""
        
        return prompt
    
    @staticmethod
    def refactoring_suggestion_prompt(code: str, complexity: int) -> str:
        """
        Generate prompt for refactoring suggestions
        
        Args:
            code: Code to refactor
            complexity: Cyclomatic complexity score
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""This function has high cyclomatic complexity ({complexity}). 
Suggest how to refactor it:

```python
{code}
```

Provide:
1. Main issues causing high complexity
2. Step-by-step refactoring approach
3. Expected complexity after refactoring

Suggestions:"""
        
        return prompt
    
    @staticmethod
    def dependency_analysis_prompt(file_imports: List[str],
                                  dependent_files: List[str]) -> str:
        """
        Generate prompt for dependency analysis
        
        Args:
            file_imports: List of imports in the file
            dependent_files: Files that depend on this file
            
        Returns:
            Formatted prompt string
        """
        imports_str = "\n".join(f"- {imp}" for imp in file_imports[:10])
        dependents_str = "\n".join(f"- {dep}" for dep in dependent_files[:5])
        
        prompt = f"""Analyze these file dependencies:

This file imports:
{imports_str}

Files that depend on this file:
{dependents_str}

Provide:
1. Assessment of coupling (tight/loose)
2. Potential circular dependency risks
3. Suggestions for improving modularity

Analysis:"""
        
        return prompt
    
    @staticmethod
    def code_quality_prompt(metrics: Dict) -> str:
        """
        Generate prompt for overall code quality assessment
        
        Args:
            metrics: Dictionary of code metrics
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Assess the overall code quality based on these metrics:

Cyclomatic Complexity: {metrics.get('complexity', 0):.2f}
Maintainability Index: {metrics.get('maintainability', 0):.2f}
Lines of Code: {metrics.get('loc', 0)}
Functions: {metrics.get('functions', 0)}
Classes: {metrics.get('classes', 0)}
Code Smells: {metrics.get('smells', 0)}

Provide:
1. Overall quality rating (Excellent/Good/Fair/Poor)
2. Top 3 areas for improvement
3. Priority recommendations

Assessment:"""
        
        return prompt
    
    @staticmethod
    def documentation_generation_prompt(code: str, existing_docs: str) -> str:
        """
        Generate prompt for documentation generation
        
        Args:
            code: Code to document
            existing_docs: Any existing documentation
            
        Returns:
            Formatted prompt string
        """
        existing = f"Existing: {existing_docs}" if existing_docs else "No existing documentation"
        
        prompt = f"""Generate comprehensive documentation for this code:

{existing}

Code:
```python
{code}
```

Generate:
1. Docstring in Google style format
2. Parameter descriptions with types
3. Return value description
4. Example usage

Documentation:"""
        
        return prompt
    
    @staticmethod
    def bug_detection_prompt(code: str, context: str) -> str:
        """
        Generate prompt for potential bug detection
        
        Args:
            code: Code to analyze
            context: Context about the code
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze this code for potential bugs:

Context: {context}

Code:
```python
{code}
```

Identify:
1. Potential runtime errors
2. Logic errors
3. Edge cases not handled
4. Security concerns

Findings:"""
        
        return prompt
    
    @staticmethod
    def test_generation_prompt(function_code: str, function_name: str) -> str:
        """
        Generate prompt for test case generation
        
        Args:
            function_code: Function to test
            function_name: Name of the function
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Generate unit test cases for this function:

Function: {function_name}

Code:
```python
{function_code}
```

Generate pytest test cases covering:
1. Normal cases
2. Edge cases
3. Error cases
4. Boundary conditions

Tests:"""
        
        return prompt

# Example usage
if __name__ == "__main__":
    templates = PromptTemplates()
    
    # Example function
    sample_code = """
def calculate_discount(price, discount_percent):
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)
"""
    
    # Generate summary prompt
    prompt = templates.function_summary_prompt(
        sample_code,
        "calculate_discount",
        ["price", "discount_percent"]
    )
    
    print("Generated Prompt:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)