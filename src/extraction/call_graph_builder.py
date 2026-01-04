"""
Call Graph Builder Module
Builds function call graphs for code analysis
"""

import ast
from typing import Dict, List, Set, Tuple
import networkx as nx
from collections import defaultdict
from src.utils.logger import logger

class CallGraphBuilder:
    """Build function call graphs"""
    
    def __init__(self):
        """Initialize call graph builder"""
        self.call_graph = nx.DiGraph()
        self.function_calls = defaultdict(set)
        self.function_definitions = {}
    
    def build_call_graph(self, parsed_files: List[Dict]) -> Dict:
        """
        Build call graph from parsed files
        
        Args:
            parsed_files: List of parsed file data
            
        Returns:
            Dictionary containing call graph information
        """
        logger.info("Building function call graph...")
        
        # First pass: collect all function definitions
        for file_data in parsed_files:
            self._collect_functions(file_data)
        
        # Second pass: build call relationships
        for file_data in parsed_files:
            self._build_calls(file_data)
        
        # Analyze the graph
        analysis = self._analyze_call_graph()
        
        return {
            'call_graph': self.call_graph,
            'function_calls': dict(self.function_calls),
            'function_definitions': self.function_definitions,
            'analysis': analysis
        }
    
    def _collect_functions(self, file_data: Dict):
        """
        Collect all function definitions
        
        Args:
            file_data: Parsed file data
        """
        filepath = file_data.get('filepath', 'unknown')
        
        for func in file_data.get('functions', []):
            func_name = func['name']
            
            # Create unique identifier
            if func.get('parent_class'):
                func_id = f"{filepath}::{func['parent_class']}.{func_name}"
            else:
                func_id = f"{filepath}::{func_name}"
            
            self.function_definitions[func_id] = {
                'name': func_name,
                'file': filepath,
                'class': func.get('parent_class'),
                'line': func.get('line_start'),
                'complexity': func.get('complexity', 0)
            }
            
            # Add node to graph
            self.call_graph.add_node(func_id, **self.function_definitions[func_id])
    
    def _build_calls(self, file_data: Dict):
        """
        Build call relationships
        
        Args:
            file_data: Parsed file data
        """
        filepath = file_data.get('filepath', 'unknown')
        
        for func in file_data.get('functions', []):
            # Get caller ID
            if func.get('parent_class'):
                caller_id = f"{filepath}::{func['parent_class']}.{func['name']}"
            else:
                caller_id = f"{filepath}::{func['name']}"
            
            # Get all calls made by this function
            calls = func.get('calls', [])
            
            for call in calls:
                # Try to resolve the call
                callee_ids = self._resolve_call(call, filepath, file_data)
                
                for callee_id in callee_ids:
                    # Add edge
                    if self.call_graph.has_node(callee_id):
                        self.call_graph.add_edge(caller_id, callee_id)
                        self.function_calls[caller_id].add(callee_id)
    
    def _resolve_call(self, call_name: str, current_file: str, 
                     file_data: Dict) -> List[str]:
        """
        Resolve a function call to its definition
        
        Args:
            call_name: Name of the called function
            current_file: Current file path
            file_data: Current file data
            
        Returns:
            List of possible function IDs
        """
        possible_ids = []
        
        # Handle method calls (e.g., "obj.method")
        if '.' in call_name:
            # For now, just try the method name
            method_name = call_name.split('.')[-1]
            call_name = method_name
        
        # Try local file first
        local_id = f"{current_file}::{call_name}"
        if local_id in self.function_definitions:
            possible_ids.append(local_id)
        
        # Try with class context
        for func in file_data.get('functions', []):
            if func.get('parent_class'):
                class_id = f"{current_file}::{func['parent_class']}.{call_name}"
                if class_id in self.function_definitions:
                    possible_ids.append(class_id)
        
        # If not found locally, search all files (expensive)
        if not possible_ids:
            for func_id in self.function_definitions:
                if func_id.endswith(f"::{call_name}") or func_id.endswith(f".{call_name}"):
                    possible_ids.append(func_id)
        
        return possible_ids
    
    def _analyze_call_graph(self) -> Dict:
        """
        Analyze the call graph for insights
        
        Returns:
            Dictionary with analysis results
        """
        if len(self.call_graph.nodes()) == 0:
            return {
                'total_functions': 0,
                'total_calls': 0,
                'most_called': [],
                'most_calls': [],
                'recursive_functions': [],
                'dead_end_functions': []
            }
        
        # Most called functions (high in-degree)
        in_degrees = dict(self.call_graph.in_degree())
        most_called = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Functions that call the most (high out-degree)
        out_degrees = dict(self.call_graph.out_degree())
        most_calls = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Detect recursive functions (self-loops)
        recursive = []
        for node in self.call_graph.nodes():
            if self.call_graph.has_edge(node, node):
                recursive.append(node)
        
        # Detect mutual recursion (simple cycles)
        try:
            cycles = list(nx.simple_cycles(self.call_graph))
            recursive.extend([c for cycle in cycles for c in cycle if len(cycle) <= 5])
        except:
            pass
        
        recursive = list(set(recursive))  # Remove duplicates
        
        # Dead-end functions (no outgoing calls, leaf nodes)
        dead_ends = [node for node in self.call_graph.nodes() 
                    if self.call_graph.out_degree(node) == 0]
        
        return {
            'total_functions': len(self.call_graph.nodes()),
            'total_calls': len(self.call_graph.edges()),
            'most_called': [
                {
                    'function': func_id,
                    'calls': count,
                    'name': self.function_definitions.get(func_id, {}).get('name', 'unknown')
                }
                for func_id, count in most_called if count > 0
            ][:5],
            'most_calls': [
                {
                    'function': func_id,
                    'calls': count,
                    'name': self.function_definitions.get(func_id, {}).get('name', 'unknown')
                }
                for func_id, count in most_calls if count > 0
            ][:5],
            'recursive_functions': [
                {
                    'function': func_id,
                    'name': self.function_definitions.get(func_id, {}).get('name', 'unknown')
                }
                for func_id in recursive[:10]
            ],
            'dead_end_functions': len(dead_ends),
            'average_calls_per_function': (
                len(self.call_graph.edges()) / len(self.call_graph.nodes())
                if len(self.call_graph.nodes()) > 0 else 0
            )
        }
    
    def get_call_chain(self, function_id: str, max_depth: int = 5) -> List[List[str]]:
        """
        Get call chains starting from a function
        
        Args:
            function_id: Starting function ID
            max_depth: Maximum chain depth
            
        Returns:
            List of call chains
        """
        if not self.call_graph.has_node(function_id):
            return []
        
        chains = []
        
        def dfs(node: str, chain: List[str], depth: int):
            if depth >= max_depth:
                chains.append(chain)
                return
            
            successors = list(self.call_graph.successors(node))
            
            if not successors:
                chains.append(chain)
                return
            
            for successor in successors:
                if successor not in chain:  # Avoid cycles
                    dfs(successor, chain + [successor], depth + 1)
        
        dfs(function_id, [function_id], 0)
        
        return chains[:10]  # Limit to 10 chains
    
    def export_dot(self, output_path: str):
        """
        Export call graph to DOT format
        
        Args:
            output_path: Path to output file
        """
        try:
            from networkx.drawing.nx_pydot import write_dot
            write_dot(self.call_graph, output_path)
            logger.info(f"Call graph exported to: {output_path}")
        except Exception as e:
            logger.error(f"Error exporting call graph: {e}")

# Example usage
if __name__ == "__main__":
    # Example parsed data
    sample_data = [
        {
            'filepath': 'test.py',
            'functions': [
                {
                    'name': 'main',
                    'calls': ['process_data', 'save_results'],
                    'line_start': 10
                },
                {
                    'name': 'process_data',
                    'calls': ['load_data', 'transform'],
                    'line_start': 20
                },
                {
                    'name': 'load_data',
                    'calls': [],
                    'line_start': 30
                }
            ]
        }
    ]
    
    builder = CallGraphBuilder()
    result = builder.build_call_graph(sample_data)
    
    print("Call Graph Analysis:")
    print(f"Total Functions: {result['analysis']['total_functions']}")
    print(f"Total Calls: {result['analysis']['total_calls']}")
    print(f"\nMost Called Functions:")
    for func in result['analysis']['most_called']:
        print(f"  - {func['name']}: {func['calls']} calls")