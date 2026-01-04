"""
Markdown Report Generator
Creates comprehensive markdown documentation
"""

from pathlib import Path
from typing import Dict, List
from datetime import datetime
from src.utils.logger import logger

class MarkdownGenerator:
    """Generate Markdown reports"""
    
    def __init__(self, output_dir: str = "./outputs/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, results: Dict, filename: str = "analysis_report.md") -> str:
        """
        Generate comprehensive markdown report
        
        Args:
            results: Complete analysis results
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        try:
            report_lines = []
            
            # Header
            report_lines.extend(self._generate_header(results['metadata']))
            
            # Executive Summary
            report_lines.extend(self._generate_summary(results['summary']))
            
            # File Analysis
            report_lines.extend(self._generate_file_analysis(results['files']))
            
            # Dependency Analysis
            if 'dependencies' in results:
                report_lines.extend(self._generate_dependency_analysis(results['dependencies']))
            
            # Code Smells
            report_lines.extend(self._generate_smell_report(results['files']))
            
            # Recommendations
            report_lines.extend(self._generate_recommendations(results))
            
            # Write to file
            output_path = self.output_dir / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            logger.info(f"Markdown report saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating markdown report: {e}")
            return None
    
    def _generate_header(self, metadata: Dict) -> List[str]:
        """Generate report header"""
        lines = [
            "# 🏛️ Codebase Archaeologist - Analysis Report",
            "",
            f"**Generated:** {metadata.get('analyzed_at', 'N/A')}  ",
            f"**Source:** `{metadata.get('source', 'N/A')}`  ",
            f"**Total Files Analyzed:** {metadata.get('total_files', 0)}  ",
            f"**Analysis Time:** {metadata.get('analysis_time_seconds', 0)}s  ",
            "",
            "---",
            ""
        ]
        return lines
    
    def _generate_summary(self, summary: Dict) -> List[str]:
        """Generate executive summary"""
        lines = [
            "## 📊 Executive Summary",
            "",
            "### Overview Statistics",
            "",
            f"- **Total Functions:** {summary.get('total_functions', 0)}",
            f"- **Total Classes:** {summary.get('total_classes', 0)}",
            f"- **Total Lines of Code:** {summary.get('total_lines_of_code', 0):,}",
            f"- **Code Smells Detected:** {summary.get('total_code_smells', 0)}",
            "",
            "### Quality Metrics",
            "",
            f"- **Average Cyclomatic Complexity:** {summary.get('average_complexity', 0):.2f}",
            f"- **Average Maintainability Index:** {summary.get('average_maintainability', 0):.2f}",
            "",
            self._get_quality_assessment(summary),
            "",
            "---",
            ""
        ]
        return lines
    
    def _get_quality_assessment(self, summary: Dict) -> str:
        """Generate quality assessment"""
        mi = summary.get('average_maintainability', 0)
        complexity = summary.get('average_complexity', 0)
        
        assessment = "### Quality Assessment\n\n"
        
        # Maintainability
        if mi >= 20:
            assessment += "✅ **Maintainability: GOOD** (Score: A)\n"
        elif mi >= 10:
            assessment += "⚠️ **Maintainability: MODERATE** (Score: B)\n"
        else:
            assessment += "❌ **Maintainability: POOR** (Score: C)\n"
        
        # Complexity
        if complexity <= 5:
            assessment += "✅ **Complexity: LOW** (Easy to maintain)\n"
        elif complexity <= 10:
            assessment += "⚠️ **Complexity: MODERATE** (Consider refactoring)\n"
        else:
            assessment += "❌ **Complexity: HIGH** (Needs refactoring)\n"
        
        return assessment
    
    def _generate_file_analysis(self, files: List[Dict]) -> List[str]:
        """Generate detailed file analysis"""
        lines = [
            "## 📁 Detailed File Analysis",
            "",
        ]
        
        # Sort files by complexity
        sorted_files = sorted(
            files,
            key=lambda x: x.get('complexity', {}).get('cyclomatic_complexity', {}).get('average', 0),
            reverse=True
        )
        
        for file_data in sorted_files[:10]:  # Top 10 files
            lines.extend(self._generate_file_section(file_data))
        
        return lines
    
    def _generate_file_section(self, file_data: Dict) -> List[str]:
        """Generate section for individual file"""
        filepath = file_data.get('filepath', 'unknown')
        filename = Path(filepath).name
        
        file_info = file_data.get('file_info', {})
        complexity = file_data.get('complexity', {})
        smells = file_data.get('code_smells', {})
        doc = file_data.get('documentation', {})
        
        lines = [
            f"### 📄 {filename}",
            "",
            f"**Path:** `{file_info.get('relative_path', filepath)}`  ",
            f"**Lines:** {file_info.get('lines', 0)}  ",
            f"**Functions:** {len(file_data.get('functions', []))}  ",
            f"**Classes:** {len(file_data.get('classes', []))}  ",
            "",
        ]
        
        # Summary
        if doc.get('file_summary'):
            lines.extend([
                "**Summary:**",
                f"> {doc['file_summary']}",
                ""
            ])
        
        # Complexity
        cc = complexity.get('cyclomatic_complexity', {})
        mi = complexity.get('maintainability_index', {})
        
        lines.extend([
            "**Quality Metrics:**",
            f"- Average Complexity: {cc.get('average', 0):.2f}",
            f"- Max Complexity: {cc.get('max', 0)}",
            f"- Maintainability: {mi.get('score', 0):.2f} ({mi.get('rank', 'N/A')})",
            ""
        ])
        
        # High complexity functions
        high_complexity = cc.get('high_complexity_functions', [])
        if high_complexity:
            lines.extend([
                "**⚠️ High Complexity Functions:**",
                ""
            ])
            for func in high_complexity[:5]:
                lines.append(f"- `{func['name']}()` - Complexity: {func['complexity']} (Line {func['line']})")
            lines.append("")
        
        # Code smells
        smell_count = smells.get('total_smell_count', 0)
        if smell_count > 0:
            lines.extend([
                f"**🔍 Code Smells Detected: {smell_count}**",
                ""
            ])
            
            # Long functions
            long_funcs = smells.get('smells', {}).get('long_functions', [])
            if long_funcs:
                lines.append(f"- Long Functions: {len(long_funcs)}")
            
            # Missing docstrings
            no_docs = smells.get('smells', {}).get('missing_docstrings', [])
            if no_docs:
                lines.append(f"- Missing Docstrings: {len(no_docs)}")
            
            # Dead code
            dead = smells.get('smells', {}).get('dead_code', [])
            if dead:
                lines.append(f"- Potentially Dead Code: {len(dead)}")
            
            lines.append("")
        
        lines.extend([
            "---",
            ""
        ])
        
        return lines
    
    def _generate_dependency_analysis(self, dependencies: Dict) -> List[str]:
        """Generate dependency analysis section"""
        analysis = dependencies.get('analysis', {})
        
        lines = [
            "## 🔗 Dependency Analysis",
            "",
            f"**Total Files:** {dependencies.get('total_files', 0)}  ",
            ""
        ]
        
        # Most depended upon
        most_depended = analysis.get('most_depended_upon', [])
        if most_depended:
            lines.extend([
                "### Most Depended Upon Files",
                "",
                "These files are used by many other files:",
                ""
            ])
            for item in most_depended[:5]:
                filename = Path(item['file']).name
                lines.append(f"- **{filename}** - {item['dependents']} dependents")
            lines.append("")
        
        # Files with most dependencies
        most_deps = analysis.get('most_dependencies', [])
        if most_deps:
            lines.extend([
                "### Files With Most Dependencies",
                "",
                "These files import many other files:",
                ""
            ])
            for item in most_deps[:5]:
                filename = Path(item['file']).name
                lines.append(f"- **{filename}** - {item['dependencies']} imports")
            lines.append("")
        
        # Circular dependencies
        if analysis.get('has_circular_dependencies'):
            circular = analysis.get('circular_dependencies', [])
            lines.extend([
                "### ⚠️ Circular Dependencies Detected",
                "",
                f"Found {len(circular)} circular dependency cycle(s):",
                ""
            ])
            for i, cycle in enumerate(circular[:3], 1):
                cycle_str = " → ".join([Path(f).name for f in cycle])
                lines.append(f"{i}. {cycle_str}")
            lines.append("")
        
        # Isolated files
        isolated = analysis.get('isolated_files', [])
        if isolated:
            lines.extend([
                "### Isolated Files",
                "",
                f"These {len(isolated)} file(s) have no dependencies:",
                ""
            ])
            for filepath in isolated[:5]:
                lines.append(f"- `{Path(filepath).name}`")
            lines.append("")
        
        lines.extend([
            "---",
            ""
        ])
        
        return lines
    
    def _generate_smell_report(self, files: List[Dict]) -> List[str]:
        """Generate comprehensive code smell report"""
        lines = [
            "## 🔍 Code Quality Issues",
            ""
        ]
        
        # Aggregate all smells
        all_long_funcs = []
        all_missing_docs = []
        all_dead_code = []
        all_magic_numbers = []
        
        for file_data in files:
            smells = file_data.get('code_smells', {}).get('smells', {})
            filepath = file_data.get('filepath', '')
            
            for func in smells.get('long_functions', []):
                func['file'] = filepath
                all_long_funcs.append(func)
            
            for item in smells.get('missing_docstrings', []):
                item['file'] = filepath
                all_missing_docs.append(item)
            
            for item in smells.get('dead_code', []):
                item['file'] = filepath
                all_dead_code.append(item)
            
            for item in smells.get('magic_numbers', []):
                item['file'] = filepath
                all_magic_numbers.append(item)
        
        # Long functions
        if all_long_funcs:
            lines.extend([
                "### 📏 Long Functions",
                "",
                f"Found {len(all_long_funcs)} function(s) exceeding recommended length:",
                ""
            ])
            for func in sorted(all_long_funcs, key=lambda x: x['lines'], reverse=True)[:10]:
                lines.append(f"- `{func['name']}()` in `{Path(func['file']).name}` - {func['lines']} lines (Line {func['line_start']})")
            lines.append("")
        
        # Missing docstrings
        if all_missing_docs:
            lines.extend([
                "### 📝 Missing Docstrings",
                "",
                f"Found {len(all_missing_docs)} function(s)/class(es) without docstrings:",
                ""
            ])
            for item in all_missing_docs[:10]:
                lines.append(f"- `{item['name']}` ({item['type']}) in `{Path(item['file']).name}` (Line {item['line']})")
            lines.append("")
        
        # Dead code
        if all_dead_code:
            lines.extend([
                "### ☠️ Potentially Dead Code",
                "",
                f"Found {len(all_dead_code)} potentially unused function(s):",
                ""
            ])
            for item in all_dead_code[:10]:
                lines.append(f"- `{item['name']}()` in `{Path(item['file']).name}` (Line {item['line']})")
            lines.append("")
        
        lines.extend([
            "---",
            ""
        ])
        
        return lines
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate actionable recommendations"""
        summary = results['summary']
        
        lines = [
            "## 💡 Recommendations",
            ""
        ]
        
        recommendations = []
        
        # Check complexity
        if summary.get('average_complexity', 0) > 10:
            recommendations.append(
                "**High Complexity:** Consider refactoring complex functions. "
                "Break down large functions into smaller, more manageable pieces."
            )
        
        # Check maintainability
        if summary.get('average_maintainability', 0) < 20:
            recommendations.append(
                "**Low Maintainability:** Add comments and documentation. "
                "Simplify complex logic and improve code readability."
            )
        
        # Check code smells
        if summary.get('total_code_smells', 0) > 20:
            recommendations.append(
                "**Many Code Smells:** Address code quality issues systematically. "
                "Start with high-priority smells like long functions and missing docstrings."
            )
        
        # Check circular dependencies
        dep_analysis = results.get('dependencies', {}).get('analysis', {})
        if dep_analysis.get('has_circular_dependencies'):
            recommendations.append(
                "**Circular Dependencies:** Refactor to remove circular imports. "
                "Consider dependency inversion or extracting shared functionality."
            )
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"{i}. {rec}")
                lines.append("")
        else:
            lines.extend([
                "✅ **Great job!** Your codebase shows good quality metrics.",
                ""
            ])
        
        lines.extend([
            "---",
            "",
            "## 📚 Next Steps",
            "",
            "1. Review high-complexity functions and refactor",
            "2. Add missing docstrings to improve documentation",
            "3. Address identified code smells systematically",
            "4. Run analysis regularly to track improvements",
            "",
            "---",
            "",
            f"*Report generated by Codebase Archaeologist v1.0*"
        ])
        
        return lines