"""
HTML Report Generator Module
Generates interactive HTML reports for code analysis
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader
import json
from src.utils.logger import logger

class HTMLGenerator:
    """Generate interactive HTML reports"""
    
    def __init__(self, output_dir: str = "./outputs/reports"):
        """
        Initialize HTML generator
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load templates
        template_dir = Path(__file__).parent
        self.template_path = template_dir / "template.html"
    
    def generate_report(self, results: Dict, filename: str = "analysis_report.html") -> str:
        """
        Generate comprehensive HTML report
        
        Args:
            results: Complete analysis results
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        try:
            # Prepare data for template
            template_data = self._prepare_template_data(results)
            
            # Read and render template
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = Template(f.read())
            
            html_content = template.render(**template_data)
            
            # Write to file
            output_path = self.output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return None
    
    def _prepare_template_data(self, results: Dict) -> Dict:
        """Prepare data for HTML template"""
        metadata = results.get('metadata', {})
        summary = results.get('summary', {})
        files = results.get('files', [])
        dependencies = results.get('dependencies', {})
        
        # Calculate quality grade
        mi = summary.get('average_maintainability', 0)
        complexity = summary.get('average_complexity', 0)
        
        if mi >= 20 and complexity <= 5:
            quality_grade = 'A'
            quality_color = '#28a745'
            quality_text = 'Excellent'
        elif mi >= 15 and complexity <= 10:
            quality_grade = 'B'
            quality_color = '#17a2b8'
            quality_text = 'Good'
        elif mi >= 10 and complexity <= 15:
            quality_grade = 'C'
            quality_color = '#ffc107'
            quality_text = 'Fair'
        else:
            quality_grade = 'D'
            quality_color = '#dc3545'
            quality_text = 'Needs Improvement'
        
        # Prepare file data
        file_data = []
        for f in files[:50]:  # Limit to 50 files
            file_data.append({
                'name': Path(f.get('filepath', '')).name,
                'path': f.get('file_info', {}).get('relative_path', ''),
                'lines': f.get('file_info', {}).get('lines', 0),
                'functions': len(f.get('functions', [])),
                'classes': len(f.get('classes', [])),
                'complexity': f.get('complexity', {}).get('cyclomatic_complexity', {}).get('average', 0),
                'maintainability': f.get('complexity', {}).get('maintainability_index', {}).get('score', 0),
                'smells': f.get('code_smells', {}).get('total_smell_count', 0),
                'summary': f.get('documentation', {}).get('file_summary', '')
            })
        
        # Sort by complexity
        file_data.sort(key=lambda x: x['complexity'], reverse=True)
        
        # Prepare code smells summary
        smell_counts = {
            'long_functions': 0,
            'missing_docstrings': 0,
            'dead_code': 0,
            'magic_numbers': 0,
            'too_many_parameters': 0
        }
        
        for f in files:
            smells = f.get('code_smells', {}).get('smells', {})
            for key in smell_counts:
                smell_counts[key] += len(smells.get(key, []))
        
        return {
            'title': 'Codebase Archaeologist Report',
            'generated_at': metadata.get('analyzed_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'source': metadata.get('source', 'Unknown'),
            'analysis_time': metadata.get('analysis_time_seconds', 0),
            'total_files': metadata.get('total_files', 0),
            'total_functions': summary.get('total_functions', 0),
            'total_classes': summary.get('total_classes', 0),
            'total_lines': summary.get('total_lines_of_code', 0),
            'avg_complexity': summary.get('average_complexity', 0),
            'avg_maintainability': summary.get('average_maintainability', 0),
            'total_smells': summary.get('total_code_smells', 0),
            'quality_grade': quality_grade,
            'quality_color': quality_color,
            'quality_text': quality_text,
            'files': file_data,
            'smell_counts': smell_counts,
            'most_complex': summary.get('most_complex_files', [])[:5],
            'has_circular_deps': dependencies.get('analysis', {}).get('has_circular_dependencies', False),
            'circular_deps': dependencies.get('analysis', {}).get('circular_dependencies', [])[:3],
            'most_depended': dependencies.get('analysis', {}).get('most_depended_upon', [])[:5],
            'json_data': json.dumps(results, default=str, indent=2)
        }
    
    def generate_mini_report(self, results: Dict, filename: str = "summary.html") -> str:
        """
        Generate a compact summary HTML report
        
        Args:
            results: Analysis results
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        summary = results.get('summary', {})
        metadata = results.get('metadata', {})
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Summary</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin: 20px 0; }}
        .metric {{ text-align: center; padding: 20px; background: #ecf0f1; border-radius: 8px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #2c3e50; }}
        .metric-label {{ color: #7f8c8d; margin-top: 5px; }}
        .status-good {{ color: #27ae60; }}
        .status-warn {{ color: #f39c12; }}
        .status-bad {{ color: #e74c3c; }}
        footer {{ margin-top: 30px; text-align: center; color: #95a5a6; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️ Codebase Archaeologist</h1>
        <p><strong>Source:</strong> {metadata.get('source', 'N/A')}</p>
        <p><strong>Analyzed:</strong> {metadata.get('analyzed_at', 'N/A')}</p>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{metadata.get('total_files', 0)}</div>
                <div class="metric-label">Files</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.get('total_functions', 0)}</div>
                <div class="metric-label">Functions</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.get('total_classes', 0)}</div>
                <div class="metric-label">Classes</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.get('total_lines_of_code', 0):,}</div>
                <div class="metric-label">Lines of Code</div>
            </div>
        </div>
        
        <h2>Quality Metrics</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-value {'status-good' if summary.get('average_complexity', 0) <= 5 else 'status-warn' if summary.get('average_complexity', 0) <= 10 else 'status-bad'}">
                    {summary.get('average_complexity', 0):.1f}
                </div>
                <div class="metric-label">Avg Complexity</div>
            </div>
            <div class="metric">
                <div class="metric-value {'status-good' if summary.get('average_maintainability', 0) >= 20 else 'status-warn' if summary.get('average_maintainability', 0) >= 10 else 'status-bad'}">
                    {summary.get('average_maintainability', 0):.1f}
                </div>
                <div class="metric-label">Maintainability</div>
            </div>
            <div class="metric">
                <div class="metric-value {'status-good' if summary.get('total_code_smells', 0) < 10 else 'status-warn' if summary.get('total_code_smells', 0) < 30 else 'status-bad'}">
                    {summary.get('total_code_smells', 0)}
                </div>
                <div class="metric-label">Code Smells</div>
            </div>
        </div>
        
        <footer>
            Generated by Codebase Archaeologist v1.0
        </footer>
    </div>
</body>
</html>
"""
        
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"Mini report saved to: {output_path}")
        return str(output_path)


# Example usage
if __name__ == "__main__":
    # Test with sample data
    sample_results = {
        'metadata': {
            'source': '/test/path',
            'analyzed_at': '2024-01-01 12:00:00',
            'total_files': 10,
            'analysis_time_seconds': 5.2
        },
        'summary': {
            'total_functions': 50,
            'total_classes': 10,
            'total_lines_of_code': 2000,
            'average_complexity': 6.5,
            'average_maintainability': 18.5,
            'total_code_smells': 12,
            'most_complex_files': []
        },
        'files': [],
        'dependencies': {'analysis': {}}
    }
    
    generator = HTMLGenerator()
    generator.generate_mini_report(sample_results)
