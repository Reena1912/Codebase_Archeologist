"""
Dependency Extractor Module
Extract and analyze file dependencies
"""

from typing import Dict, List, Set
from collections import defaultdict
import networkx as nx
from src.utils.logger import logger

class DependencyExtractor:
    """Extract and analyze code dependencies"""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
        self.file_dependencies = defaultdict(set)
    
    def extract_dependencies(self, all_parsed_data: List[Dict]) -> Dict:
        """
        Extract dependencies from all parsed files
        
        Args:
            all_parsed_data: List of parsed file data
            
        Returns:
            Dictionary containing dependency information
        """
        logger.info("Extracting dependencies...")
        
        # Build file mapping
        file_map = {data['filepath']: data for data in all_parsed_data}
        
        # Extract imports and build dependency graph
        for file_data in all_parsed_data:
            filepath = file_data['filepath']
            imports = file_data.get('imports', [])
            
            # Add node for this file
            self.dependency_graph.add_node(filepath)
            
            # Process imports
            for import_data in imports:
                dependencies = self._resolve_import(import_data, file_map)
                for dep in dependencies:
                    self.file_dependencies[filepath].add(dep)
                    self.dependency_graph.add_edge(filepath, dep)
        
        # Analyze dependencies
        analysis = self._analyze_dependencies()
        
        # Convert sets to lists for JSON serialization
        file_deps_serializable = {k: list(v) for k, v in self.file_dependencies.items()}
        
        return {
            'total_files': len(all_parsed_data),
            'dependency_graph': self.dependency_graph,
            'file_dependencies': file_deps_serializable,
            'analysis': analysis
        }
    
    def _resolve_import(self, import_data: Dict, file_map: Dict) -> List[str]:
        """
        Resolve import to actual file dependencies
        
        Args:
            import_data: Import information
            file_map: Mapping of filepaths to parsed data
            
        Returns:
            List of resolved file dependencies
        """
        dependencies = []
        
        if import_data['type'] == 'import':
            # Handle: import module
            modules = import_data.get('modules', [])
            for module in modules:
                # Try to find corresponding file
                module_path = module.replace('.', '/')
                for filepath in file_map.keys():
                    if module_path in filepath:
                        dependencies.append(filepath)
        
        elif import_data['type'] == 'from_import':
            # Handle: from module import name
            module = import_data.get('module', '')
            if module:
                module_path = module.replace('.', '/')
                for filepath in file_map.keys():
                    if module_path in filepath:
                        dependencies.append(filepath)
        
        return dependencies
    
    def _analyze_dependencies(self) -> Dict:
        """Analyze dependency graph for insights"""
        
        # Most depended upon files (incoming edges)
        in_degrees = dict(self.dependency_graph.in_degree())
        most_depended = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Files with most dependencies (outgoing edges)
        out_degrees = dict(self.dependency_graph.out_degree())
        most_dependencies = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Detect circular dependencies
        circular = []
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            circular = cycles[:5]  # Limit to first 5
        except:
            pass
        
        # Isolated files (no dependencies)
        isolated = [node for node in self.dependency_graph.nodes() 
                   if self.dependency_graph.degree(node) == 0]
        
        return {
            'most_depended_upon': [
                {'file': file, 'dependents': count} 
                for file, count in most_depended if count > 0
            ],
            'most_dependencies': [
                {'file': file, 'dependencies': count} 
                for file, count in most_dependencies if count > 0
            ],
            'circular_dependencies': circular,
            'isolated_files': isolated,
            'has_circular_dependencies': len(circular) > 0
        }
    
    def get_dependency_matrix(self) -> List[List[int]]:
        """
        Generate dependency matrix for visualization
        
        Returns:
            Adjacency matrix
        """
        return nx.to_numpy_array(self.dependency_graph)
    
    def export_graph_data(self) -> Dict:
        """
        Export graph data in format suitable for visualization
        
        Returns:
            Dictionary with nodes and edges
        """
        nodes = [
            {
                'id': node,
                'label': node.split('/')[-1],  # Just filename
                'in_degree': self.dependency_graph.in_degree(node),
                'out_degree': self.dependency_graph.out_degree(node)
            }
            for node in self.dependency_graph.nodes()
        ]
        
        edges = [
            {
                'source': source,
                'target': target
            }
            for source, target in self.dependency_graph.edges()
        ]
        
        return {
            'nodes': nodes,
            'edges': edges
        }