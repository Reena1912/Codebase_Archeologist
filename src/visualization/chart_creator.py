"""
Chart Creator Module
Creates various charts and visualizations using Plotly and Matplotlib
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

# Try to import plotting libraries
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from src.utils.logger import logger

class ChartCreator:
    """Create various charts and visualizations"""
    
    def __init__(self, output_dir: str = "./outputs/visualizations"):
        """
        Initialize chart creator
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Color palette
        self.colors = {
            'primary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'secondary': '#6c757d',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
        
        self.complexity_colors = ['#27ae60', '#f1c40f', '#e67e22', '#e74c3c']
    
    def create_complexity_heatmap(self, files: List[Dict], 
                                  filename: str = "complexity_heatmap.html") -> Optional[str]:
        """
        Create interactive complexity heatmap
        
        Args:
            files: List of file analysis data
            filename: Output filename
            
        Returns:
            Path to generated file or None
        """
        if not HAS_PLOTLY:
            logger.warning("Plotly not installed, skipping heatmap")
            return None
        
        try:
            # Prepare data
            data = []
            for f in files[:30]:  # Limit files
                filepath = f.get('filepath', 'unknown')
                file_name = Path(filepath).name
                
                complexity = f.get('complexity', {})
                functions = complexity.get('cyclomatic_complexity', {}).get('functions', [])
                
                for func in functions:
                    data.append({
                        'File': file_name,
                        'Function': func.get('name', 'unknown'),
                        'Complexity': func.get('complexity', 0)
                    })
            
            if not data:
                logger.warning("No function data for heatmap")
                return None
            
            # Create heatmap using scatter plot
            import pandas as pd
            df = pd.DataFrame(data)
            
            fig = px.scatter(
                df, 
                x='File', 
                y='Function', 
                size='Complexity',
                color='Complexity',
                color_continuous_scale=['green', 'yellow', 'orange', 'red'],
                title='Function Complexity Heatmap',
                hover_data=['Complexity']
            )
            
            fig.update_layout(
                xaxis_tickangle=-45,
                height=600,
                width=1000
            )
            
            # Save
            output_path = self.output_dir / filename
            fig.write_html(str(output_path))
            
            logger.info(f"Complexity heatmap saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating heatmap: {e}")
            return None
    
    def create_metrics_dashboard(self, summary: Dict, 
                                 filename: str = "metrics_dashboard.html") -> Optional[str]:
        """
        Create interactive metrics dashboard
        
        Args:
            summary: Summary statistics
            filename: Output filename
            
        Returns:
            Path to generated file or None
        """
        if not HAS_PLOTLY:
            logger.warning("Plotly not installed, skipping dashboard")
            return None
        
        try:
            # Create subplot figure
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=(
                    'Code Statistics',
                    'Quality Metrics',
                    'Complexity Distribution',
                    'Code Smells'
                ),
                specs=[
                    [{"type": "bar"}, {"type": "indicator"}],
                    [{"type": "pie"}, {"type": "bar"}]
                ]
            )
            
            # 1. Code Statistics Bar Chart
            stats_labels = ['Functions', 'Classes', 'Lines (÷100)']
            stats_values = [
                summary.get('total_functions', 0),
                summary.get('total_classes', 0),
                summary.get('total_lines_of_code', 0) / 100
            ]
            
            fig.add_trace(
                go.Bar(x=stats_labels, y=stats_values, marker_color=self.colors['primary']),
                row=1, col=1
            )
            
            # 2. Quality Gauge
            mi = summary.get('average_maintainability', 0)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=mi,
                    title={'text': "Maintainability Index"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': self.colors['primary']},
                        'steps': [
                            {'range': [0, 10], 'color': self.colors['danger']},
                            {'range': [10, 20], 'color': self.colors['warning']},
                            {'range': [20, 100], 'color': self.colors['success']}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': mi
                        }
                    }
                ),
                row=1, col=2
            )
            
            # 3. Complexity Distribution Pie
            complexity = summary.get('average_complexity', 0)
            remaining = max(0, 20 - complexity)
            
            fig.add_trace(
                go.Pie(
                    labels=['Complexity', 'Remaining'],
                    values=[complexity, remaining],
                    marker_colors=[
                        self.colors['warning'] if complexity > 5 else self.colors['success'],
                        self.colors['light']
                    ],
                    hole=0.4
                ),
                row=2, col=1
            )
            
            # 4. Code Smells Bar
            smells = summary.get('total_code_smells', 0)
            smell_categories = ['Long Functions', 'Missing Docs', 'Dead Code', 'Other']
            # Distribute smells (simplified)
            smell_values = [smells // 4] * 3 + [smells - (smells // 4) * 3]
            
            fig.add_trace(
                go.Bar(
                    x=smell_categories,
                    y=smell_values,
                    marker_color=[
                        self.colors['danger'],
                        self.colors['warning'],
                        self.colors['info'],
                        self.colors['secondary']
                    ]
                ),
                row=2, col=2
            )
            
            # Update layout
            fig.update_layout(
                title_text="Codebase Metrics Dashboard",
                height=700,
                showlegend=False
            )
            
            # Save
            output_path = self.output_dir / filename
            fig.write_html(str(output_path))
            
            logger.info(f"Metrics dashboard saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return None
    
    def create_dependency_network(self, dependencies: Dict,
                                  filename: str = "dependency_network.html") -> Optional[str]:
        """
        Create interactive dependency network visualization
        
        Args:
            dependencies: Dependency analysis data
            filename: Output filename
            
        Returns:
            Path to generated file or None
        """
        if not HAS_PLOTLY:
            logger.warning("Plotly not installed, skipping network")
            return None
        
        try:
            file_deps = dependencies.get('file_dependencies', {})
            
            if not file_deps:
                logger.warning("No dependency data for network")
                return None
            
            # Build node and edge lists
            nodes = set()
            edges = []
            
            for source, targets in file_deps.items():
                source_name = Path(source).name
                nodes.add(source_name)
                
                for target in targets:
                    target_name = Path(target).name
                    nodes.add(target_name)
                    edges.append((source_name, target_name))
            
            nodes = list(nodes)
            
            # Create positions using simple circular layout
            import math
            n = len(nodes)
            positions = {}
            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / n
                positions[node] = (math.cos(angle), math.sin(angle))
            
            # Create edge traces
            edge_x = []
            edge_y = []
            for source, target in edges:
                x0, y0 = positions[source]
                x1, y1 = positions[target]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Create node trace
            node_x = [positions[node][0] for node in nodes]
            node_y = [positions[node][1] for node in nodes]
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=nodes,
                textposition="top center",
                marker=dict(
                    size=20,
                    color=self.colors['primary'],
                    line_width=2
                )
            )
            
            # Create figure
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='File Dependency Network',
                    showlegend=False,
                    hovermode='closest',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=700
                )
            )
            
            # Save
            output_path = self.output_dir / filename
            fig.write_html(str(output_path))
            
            logger.info(f"Dependency network saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating network: {e}")
            return None
    
    def create_treemap(self, files: List[Dict], 
                       filename: str = "codebase_treemap.html") -> Optional[str]:
        """
        Create treemap visualization of codebase structure
        
        Args:
            files: List of file analysis data
            filename: Output filename
            
        Returns:
            Path to generated file or None
        """
        if not HAS_PLOTLY:
            logger.warning("Plotly not installed, skipping treemap")
            return None
        
        try:
            # Prepare data
            labels = []
            parents = []
            values = []
            colors = []
            
            # Root
            labels.append("Codebase")
            parents.append("")
            values.append(0)
            colors.append(self.colors['primary'])
            
            # Add files
            for f in files:
                filepath = f.get('filepath', 'unknown')
                file_name = Path(filepath).name
                lines = f.get('file_info', {}).get('lines', 1)
                complexity = f.get('complexity', {}).get('cyclomatic_complexity', {}).get('average', 0)
                
                labels.append(file_name)
                parents.append("Codebase")
                values.append(lines)
                
                # Color by complexity
                if complexity <= 5:
                    colors.append(self.colors['success'])
                elif complexity <= 10:
                    colors.append(self.colors['warning'])
                else:
                    colors.append(self.colors['danger'])
            
            # Create treemap
            fig = go.Figure(go.Treemap(
                labels=labels,
                parents=parents,
                values=values,
                marker_colors=colors,
                textinfo="label+value",
                hovertemplate='<b>%{label}</b><br>Lines: %{value}<extra></extra>'
            ))
            
            fig.update_layout(
                title='Codebase Structure (size = lines, color = complexity)',
                height=600
            )
            
            # Save
            output_path = self.output_dir / filename
            fig.write_html(str(output_path))
            
            logger.info(f"Treemap saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating treemap: {e}")
            return None
    
    def create_timeline_chart(self, metrics_history: List[Dict],
                             filename: str = "metrics_timeline.html") -> Optional[str]:
        """
        Create timeline chart of metrics over time
        
        Args:
            metrics_history: List of historical metrics with timestamps
            filename: Output filename
            
        Returns:
            Path to generated file or None
        """
        if not HAS_PLOTLY:
            logger.warning("Plotly not installed, skipping timeline")
            return None
        
        try:
            if not metrics_history:
                logger.warning("No historical data for timeline")
                return None
            
            dates = [m.get('date', '') for m in metrics_history]
            complexity = [m.get('complexity', 0) for m in metrics_history]
            maintainability = [m.get('maintainability', 0) for m in metrics_history]
            smells = [m.get('smells', 0) for m in metrics_history]
            
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                subplot_titles=('Complexity', 'Maintainability', 'Code Smells')
            )
            
            fig.add_trace(
                go.Scatter(x=dates, y=complexity, mode='lines+markers',
                          name='Complexity', line_color=self.colors['warning']),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=dates, y=maintainability, mode='lines+markers',
                          name='Maintainability', line_color=self.colors['success']),
                row=2, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=dates, y=smells, mode='lines+markers',
                          name='Code Smells', line_color=self.colors['danger']),
                row=3, col=1
            )
            
            fig.update_layout(
                title='Metrics Over Time',
                height=700
            )
            
            output_path = self.output_dir / filename
            fig.write_html(str(output_path))
            
            logger.info(f"Timeline chart saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error creating timeline: {e}")
            return None
    
    def create_all_visualizations(self, results: Dict) -> Dict[str, str]:
        """
        Create all available visualizations
        
        Args:
            results: Complete analysis results
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        outputs = {}
        
        files = results.get('files', [])
        summary = results.get('summary', {})
        dependencies = results.get('dependencies', {})
        
        # Create each visualization
        path = self.create_complexity_heatmap(files)
        if path:
            outputs['heatmap'] = path
        
        path = self.create_metrics_dashboard(summary)
        if path:
            outputs['dashboard'] = path
        
        path = self.create_dependency_network(dependencies)
        if path:
            outputs['network'] = path
        
        path = self.create_treemap(files)
        if path:
            outputs['treemap'] = path
        
        logger.info(f"Created {len(outputs)} visualizations")
        return outputs


# Example usage
if __name__ == "__main__":
    # Test with sample data
    sample_summary = {
        'total_functions': 50,
        'total_classes': 10,
        'total_lines_of_code': 2000,
        'average_complexity': 6.5,
        'average_maintainability': 18.5,
        'total_code_smells': 12
    }
    
    creator = ChartCreator()
    creator.create_metrics_dashboard(sample_summary)
