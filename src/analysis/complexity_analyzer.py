"""
Complexity Analyzer Module
Calculate code complexity metrics using Radon
"""

from typing import Dict, List
from radon.complexity import cc_visit
from radon.metrics import mi_visit, h_visit
from radon.raw import analyze
from src.utils.logger import logger

class ComplexityAnalyzer:
    """Analyze code complexity and quality metrics"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_complexity = config['quality'].get('max_complexity', 10)
        self.max_function_length = config['quality'].get('max_function_length', 50)
    
    def analyze_file(self, filepath: str, content: str) -> Dict:
        """
        Analyze complexity metrics for a file
        
        Args:
            filepath: Path to file
            content: File content
            
        Returns:
            Dictionary containing complexity metrics
        """
        try:
            # Cyclomatic complexity
            complexity_results = cc_visit(content)
            
            # Maintainability index
            mi_score = mi_visit(content, multi=True)
            
            # Halstead metrics - handle both old and new API
            halstead = h_visit(content)
            halstead_data = {}
            try:
                # Try new API (returns list of tuples)
                if isinstance(halstead, list) and len(halstead) > 0:
                    h_item = halstead[0]
                    if hasattr(h_item, 'total'):
                        # Even newer API
                        h = h_item.total
                        halstead_data = {
                            'volume': getattr(h, 'volume', 0) if h else 0,
                            'difficulty': getattr(h, 'difficulty', 0) if h else 0,
                            'effort': getattr(h, 'effort', 0) if h else 0
                        }
                    else:
                        halstead_data = {
                            'volume': getattr(h_item, 'volume', 0),
                            'difficulty': getattr(h_item, 'difficulty', 0),
                            'effort': getattr(h_item, 'effort', 0)
                        }
                elif hasattr(halstead, 'volume'):
                    # Old API
                    halstead_data = {
                        'volume': halstead.volume,
                        'difficulty': halstead.difficulty,
                        'effort': halstead.effort
                    }
                else:
                    halstead_data = {'volume': 0, 'difficulty': 0, 'effort': 0}
            except (TypeError, AttributeError):
                halstead_data = {'volume': 0, 'difficulty': 0, 'effort': 0}
            
            # Raw metrics (LOC, SLOC, etc.)
            raw_metrics = analyze(content)
            
            # Process complexity results
            functions_complexity = []
            high_complexity = []
            
            for result in complexity_results:
                func_data = {
                    'name': result.name,
                    'complexity': result.complexity,
                    'line': result.lineno,
                    'classname': getattr(result, 'classname', None)  # Handle Class objects
                }
                functions_complexity.append(func_data)
                
                # Flag high complexity
                if result.complexity > self.max_complexity:
                    high_complexity.append(func_data)
            
            return {
                'filepath': filepath,
                'cyclomatic_complexity': {
                    'average': self._calculate_average_complexity(complexity_results),
                    'max': max([r.complexity for r in complexity_results]) if complexity_results else 0,
                    'functions': functions_complexity,
                    'high_complexity_count': len(high_complexity),
                    'high_complexity_functions': high_complexity
                },
                'maintainability_index': {
                    'score': mi_score,
                    'rank': self._get_mi_rank(mi_score)
                },
                'halstead': halstead_data,
                'raw_metrics': {
                    'loc': raw_metrics.loc,
                    'sloc': raw_metrics.sloc,
                    'comments': raw_metrics.comments,
                    'multi': raw_metrics.multi,
                    'blank': raw_metrics.blank
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing complexity for {filepath}: {e}")
            return self._empty_result(filepath)
    
    def _calculate_average_complexity(self, results: List) -> float:
        """Calculate average cyclomatic complexity"""
        if not results:
            return 0.0
        total = sum(r.complexity for r in results)
        return round(total / len(results), 2)
    
    def _get_mi_rank(self, mi_score: float) -> str:
        """
        Get maintainability index rank
        A: 20-100 (good)
        B: 10-19 (moderate)
        C: 0-9 (poor)
        """
        if mi_score >= 20:
            return 'A (Good)'
        elif mi_score >= 10:
            return 'B (Moderate)'
        else:
            return 'C (Poor)'
    
    def analyze_repository(self, parsed_files: List[Dict]) -> Dict:
        """
        Analyze complexity for entire repository
        
        Args:
            parsed_files: List of parsed file data
            
        Returns:
            Aggregated complexity metrics
        """
        total_complexity = []
        total_mi = []
        high_complexity_files = []
        
        for file_data in parsed_files:
            complexity = file_data.get('complexity', {})
            
            if complexity:
                # Collect complexity scores
                avg_complexity = complexity.get('cyclomatic_complexity', {}).get('average', 0)
                if avg_complexity > 0:
                    total_complexity.append(avg_complexity)
                
                # Collect MI scores
                mi_score = complexity.get('maintainability_index', {}).get('score', 0)
                if mi_score > 0:
                    total_mi.append(mi_score)
                
                # Flag high complexity files
                high_count = complexity.get('cyclomatic_complexity', {}).get('high_complexity_count', 0)
                if high_count > 0:
                    high_complexity_files.append({
                        'file': file_data.get('filepath'),
                        'count': high_count,
                        'functions': complexity.get('cyclomatic_complexity', {}).get('high_complexity_functions', [])
                    })
        
        return {
            'average_complexity': round(sum(total_complexity) / len(total_complexity), 2) if total_complexity else 0,
            'average_maintainability': round(sum(total_mi) / len(total_mi), 2) if total_mi else 0,
            'total_high_complexity_files': len(high_complexity_files),
            'high_complexity_files': high_complexity_files
        }
    
    def _empty_result(self, filepath: str) -> Dict:
        """Return empty result for failed analysis"""
        return {
            'filepath': filepath,
            'cyclomatic_complexity': {
                'average': 0,
                'max': 0,
                'functions': []
            },
            'maintainability_index': {
                'score': 0,
                'rank': 'Unknown'
            },
            'halstead': {},
            'raw_metrics': {}
        }