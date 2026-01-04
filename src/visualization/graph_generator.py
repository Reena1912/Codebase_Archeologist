"""
Graph Generator Module
Creates visual dependency graphs and charts
"""

import os
import math
from pathlib import Path
from typing import Dict, List, Optional
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from src.utils.logger import logger

class GraphGenerator:
    """Generate visual graphs and charts"""
    
    def __init__(self, output_dir: str = "./outputs/graphs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_dependency_graph(self, graph: nx.DiGraph, 
                                  filename: str = "dependency_graph.png") -> str:
        """
        Generate visual dependency graph
        
        Args:
            graph: NetworkX directed graph
            filename: Output filename
            
        Returns:
            Path to generated image
        """
        try:
            if len(graph.nodes()) == 0:
                logger.warning("Empty graph, skipping visualization")
                return None
            
            # Limit nodes for readability
            if len(graph.nodes()) > 50:
                logger.info(f"Graph has {len(graph.nodes())} nodes, showing top 50 by degree")
                # Get top 50 nodes by degree
                degrees = dict(graph.degree())
                top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:50]
                nodes_to_show = [node for node, degree in top_nodes]
                graph = graph.subgraph(nodes_to_show)
            
            # Create figure
            plt.figure(figsize=(16, 12))
            
            # Use spring layout for better visualization
            pos = nx.spring_layout(graph, k=2, iterations=50)
            
            # Calculate node sizes based on degree
            degrees = dict(graph.degree())
            node_sizes = [300 + (degrees[node] * 100) for node in graph.nodes()]
            
            # Color nodes by in-degree
            in_degrees = dict(graph.in_degree())
            node_colors = [in_degrees[node] for node in graph.nodes()]
            
            # Draw graph
            nx.draw_networkx_nodes(
                graph, pos,
                node_size=node_sizes,
                node_color=node_colors,
                cmap='YlOrRd',
                alpha=0.8
            )
            
            nx.draw_networkx_edges(
                graph, pos,
                edge_color='gray',
                arrows=True,
                arrowsize=10,
                alpha=0.5,
                width=1.5
            )
            
            # Add labels (just filenames)
            labels = {node: Path(node).name for node in graph.nodes()}
            nx.draw_networkx_labels(
                graph, pos,
                labels,
                font_size=8,
                font_weight='bold'
            )
            
            plt.title("File Dependency Graph", fontsize=16, fontweight='bold')
            plt.axis('off')
            plt.tight_layout()
            
            # Save
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Dependency graph saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating dependency graph: {e}")
            return None
    
    def generate_complexity_chart(self, file_data: List[Dict], 
                                  filename: str = "complexity_chart.png") -> str:
        """
        Generate complexity bar chart
        
        Args:
            file_data: List of file analysis data
            filename: Output filename
            
        Returns:
            Path to generated image
        """
        try:
            # Extract data
            files = []
            complexities = []
            
            for data in file_data[:20]:  # Top 20 files
                filepath = data.get('filepath', 'unknown')
                filename_only = Path(filepath).name
                
                complexity = data.get('complexity', {})
                avg_complexity = complexity.get('cyclomatic_complexity', {}).get('average', 0)
                
                if avg_complexity > 0:
                    files.append(filename_only)
                    complexities.append(avg_complexity)
            
            if not files:
                logger.warning("No complexity data to visualize")
                return None
            
            # Create chart
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Color bars by complexity level
            colors = ['green' if c <= 5 else 'yellow' if c <= 10 else 'red' 
                     for c in complexities]
            
            bars = ax.barh(files, complexities, color=colors, alpha=0.7)
            
            # Add value labels
            for i, (bar, value) in enumerate(zip(bars, complexities)):
                ax.text(value + 0.2, i, f'{value:.1f}', 
                       va='center', fontsize=9)
            
            ax.set_xlabel('Average Cyclomatic Complexity', fontsize=12)
            ax.set_title('File Complexity Analysis', fontsize=14, fontweight='bold')
            ax.axvline(x=10, color='red', linestyle='--', label='High Complexity (>10)')
            ax.legend()
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            
            # Save
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Complexity chart saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating complexity chart: {e}")
            return None
    
    def generate_smell_distribution(self, all_smells: Dict,
                                    filename: str = "smell_distribution.png") -> str:
        """
        Generate code smell distribution pie chart
        
        Args:
            all_smells: Dictionary of smell types and counts
            filename: Output filename
            
        Returns:
            Path to generated image
        """
        try:
            if not all_smells or sum(all_smells.values()) == 0:
                logger.warning("No code smell data to visualize")
                return None
            
            # Create chart
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Sort by count
            sorted_smells = dict(sorted(all_smells.items(), 
                                       key=lambda x: x[1], 
                                       reverse=True))
            
            labels = list(sorted_smells.keys())
            sizes = list(sorted_smells.values())
            
            # Colors
            colors = plt.cm.Set3(range(len(labels)))
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                sizes, 
                labels=labels,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 10}
            )
            
            # Enhance text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            ax.set_title('Code Smell Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # Save
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Smell distribution chart saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating smell distribution: {e}")
            return None
    
    def generate_metrics_summary(self, summary: Dict,
                                filename: str = "metrics_summary.png") -> str:
        """
        Generate overall metrics summary visualization
        
        Args:
            summary: Summary statistics
            filename: Output filename
            
        Returns:
            Path to generated image
        """
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('Repository Metrics Summary', fontsize=16, fontweight='bold')
            
            # 1. Basic stats
            stats = {
                'Functions': summary.get('total_functions', 0),
                'Classes': summary.get('total_classes', 0),
                'Lines': summary.get('total_lines_of_code', 0),
                'Smells': summary.get('total_code_smells', 0)
            }
            
            ax1.bar(stats.keys(), stats.values(), color=['blue', 'green', 'orange', 'red'])
            ax1.set_title('Code Statistics')
            ax1.set_ylabel('Count')
            for i, (k, v) in enumerate(stats.items()):
                ax1.text(i, v + max(stats.values())*0.02, str(v), 
                        ha='center', fontweight='bold')
            
            # 2. Complexity gauge
            avg_complexity = summary.get('average_complexity', 0)
            max_val = 20
            
            # Create semi-circle gauge
            theta = (avg_complexity / max_val) * 180
            colors_gauge = ['green', 'yellow', 'orange', 'red']
            sections = [5, 10, 15, 20]
            
            ax2.set_xlim(-1.2, 1.2)
            ax2.set_ylim(0, 1.2)
            ax2.set_aspect('equal')
            
            # Draw gauge sections
            for i, (section, color) in enumerate(zip(sections, colors_gauge)):
                start = (i * 45)
                extent = 45
                wedge = plt.Circle((0, 0), 1, color=color, alpha=0.3)
                ax2.add_patch(plt.matplotlib.patches.Wedge(
                    (0, 0), 1, start, start + extent, 
                    color=color, alpha=0.5, width=0.3
                ))
            
            # Draw needle
            angle_rad = (theta * 3.14159) / 180
            ax2.plot([0, 0.8*math.cos(angle_rad)], 
                    [0, 0.8*math.sin(angle_rad)],
                    'k-', linewidth=3)
            ax2.plot(0, 0, 'ko', markersize=10)
            
            ax2.text(0, -0.3, f'{avg_complexity:.1f}', 
                    ha='center', fontsize=16, fontweight='bold')
            ax2.set_title('Average Complexity')
            ax2.axis('off')
            
            # 3. Maintainability score
            mi_score = summary.get('average_maintainability', 0)
            
            # Bar with gradient
            if mi_score >= 20:
                color = 'green'
                rank = 'A'
            elif mi_score >= 10:
                color = 'yellow'
                rank = 'B'
            else:
                color = 'red'
                rank = 'C'
            
            ax3.barh(['Maintainability'], [mi_score], color=color, alpha=0.7)
            ax3.set_xlim(0, 100)
            ax3.set_title('Maintainability Index')
            ax3.text(mi_score + 3, 0, f'{mi_score:.1f} ({rank})', 
                    va='center', fontsize=12, fontweight='bold')
            ax3.axvline(x=20, color='green', linestyle='--', alpha=0.5)
            ax3.axvline(x=10, color='orange', linestyle='--', alpha=0.5)
            
            # 4. Top complex files
            complex_files = summary.get('most_complex_files', [])[:5]
            
            if complex_files:
                files = [Path(f['file']).name for f in complex_files]
                complexities = [f['complexity'] for f in complex_files]
                
                ax4.barh(files, complexities, color='coral', alpha=0.7)
                ax4.set_title('Most Complex Files (Top 5)')
                ax4.set_xlabel('Complexity')
                
                for i, v in enumerate(complexities):
                    ax4.text(v + 0.1, i, f'{v:.1f}', va='center', fontsize=9)
            else:
                ax4.text(0.5, 0.5, 'No data', ha='center', va='center',
                        transform=ax4.transAxes)
                ax4.set_title('Most Complex Files')
            
            plt.tight_layout()
            
            # Save
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Metrics summary saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating metrics summary: {e}")
            return None