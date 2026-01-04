"""
Codebase Archaeologist - Main Orchestrator
Coordinates all modules to analyze codebase
"""

import json
import time
from pathlib import Path
from typing import Dict, List
from tqdm import tqdm

from src.utils.logger import setup_logger, logger
from src.utils.helpers import load_config, create_output_dir
from src.ingestion.code_loader import CodeLoader
from src.analysis.ast_parser import ASTParser
from src.analysis.complexity_analyzer import ComplexityAnalyzer
from src.extraction.dependency_extractor import DependencyExtractor
from src.extraction.code_smell_detector import CodeSmellDetector
from src.ai_engine.code_summarizer import CodeSummarizer

class CodebaseArchaeologist:
    """
    Main orchestrator for codebase analysis
    
    This class coordinates all analysis modules to:
    1. Load and parse codebase
    2. Analyze code quality and complexity
    3. Extract dependencies
    4. Detect code smells
    5. Generate AI explanations
    6. Create visualizations and reports
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize archaeologist with configuration"""
        self.config = load_config(config_path)
        
        # Setup logging
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        log_file = self.config.get('logging', {}).get('file', 'archaeologist.log')
        setup_logger(level=log_level, log_file=log_file)
        
        # Initialize modules
        self.loader = CodeLoader(self.config)
        self.parser = ASTParser()
        self.complexity_analyzer = ComplexityAnalyzer(self.config)
        self.dependency_extractor = DependencyExtractor()
        self.smell_detector = CodeSmellDetector(self.config)
        self.summarizer = CodeSummarizer(self.config)
        
        # Create output directory
        self.output_dir = create_output_dir(self.config['output']['base_dir'])
        
        logger.info("🏛️  Codebase Archaeologist initialized")
    
    def analyze_local(self, path: str) -> Dict:
        """
        Analyze local codebase
        
        Args:
            path: Path to local codebase
            
        Returns:
            Complete analysis results
        """
        logger.info(f"📂 Starting analysis of: {path}")
        start_time = time.time()
        
        # Step 1: Load codebase
        codebase_data = self.loader.load_from_local(path)
        files = self.loader.filter_by_language(codebase_data['files'], 'python')
        
        if not files:
            logger.warning("No Python files found!")
            return {}
        
        # Step 2: Parse and analyze files
        logger.info("📊 Parsing and analyzing files...")
        all_parsed = []
        
        for file_data in tqdm(files, desc="Analyzing files"):
            parsed = self._analyze_file(file_data)
            all_parsed.append(parsed)
        
        # Step 3: Extract dependencies
        logger.info("🔗 Extracting dependencies...")
        dependency_data = self.dependency_extractor.extract_dependencies(all_parsed)
        
        # Step 4: Detect duplicates
        logger.info("🔍 Detecting code smells and duplicates...")
        duplicates = self.smell_detector.detect_duplicates(all_parsed)
        
        # Step 5: Analyze repository-level metrics
        logger.info("📈 Calculating repository metrics...")
        repo_complexity = self.complexity_analyzer.analyze_repository(all_parsed)
        
        # Step 6: Compile results
        results = {
            'metadata': {
                'source': path,
                'analyzed_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_files': len(files),
                'analysis_time_seconds': round(time.time() - start_time, 2)
            },
            'files': all_parsed,
            'dependencies': dependency_data,
            'duplicates': duplicates,
            'repository_metrics': repo_complexity,
            'summary': self._generate_summary(all_parsed, dependency_data, repo_complexity)
        }
        
        # Step 7: Save results
        self._save_results(results)
        
        logger.info(f"✅ Analysis complete in {results['metadata']['analysis_time_seconds']}s")
        logger.info(f"📄 Results saved to: {self.output_dir}")
        
        return results
    
    def analyze_github(self, repo_url: str) -> Dict:
        """
        Analyze GitHub repository
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Complete analysis results
        """
        logger.info(f"🐙 Analyzing GitHub repository: {repo_url}")
        
        # Load from GitHub
        codebase_data = self.loader.load_from_github(repo_url)
        
        # Continue with normal analysis
        return self.analyze_local(codebase_data['source'])
    
    def _analyze_file(self, file_data: Dict) -> Dict:
        """
        Analyze a single file
        
        Args:
            file_data: File information with content
            
        Returns:
            Complete analysis of the file
        """
        filepath = file_data['path']
        content = file_data['content']
        
        # Parse AST
        parsed = self.parser.parse_file(filepath, content)
        
        # Analyze complexity
        complexity = self.complexity_analyzer.analyze_file(filepath, content)
        
        # Detect code smells
        smells = self.smell_detector.detect_smells(parsed, content)
        
        # Generate AI summaries
        documentation = self.summarizer.generate_documentation(parsed)
        
        # Combine all data
        return {
            **parsed,
            'file_info': {
                'name': file_data['name'],
                'relative_path': file_data['relative_path'],
                'lines': file_data['lines'],
                'size': file_data['size']
            },
            'complexity': complexity,
            'code_smells': smells,
            'documentation': documentation
        }
    
    def _generate_summary(self, all_parsed: List[Dict], 
                         dependency_data: Dict, 
                         repo_complexity: Dict) -> Dict:
        """Generate high-level repository summary"""
        
        total_functions = sum(len(f['functions']) for f in all_parsed)
        total_classes = sum(len(f['classes']) for f in all_parsed)
        total_lines = sum(f['file_info']['lines'] for f in all_parsed)
        
        # Code smell statistics
        total_smells = sum(f['code_smells']['total_smell_count'] for f in all_parsed)
        
        # Most complex files
        complex_files = sorted(
            [(f['filepath'], f['complexity']['cyclomatic_complexity']['average']) 
             for f in all_parsed],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_functions': total_functions,
            'total_classes': total_classes,
            'total_lines_of_code': total_lines,
            'total_code_smells': total_smells,
            'average_complexity': repo_complexity['average_complexity'],
            'average_maintainability': repo_complexity['average_maintainability'],
            'most_complex_files': [
                {'file': f, 'complexity': c} for f, c in complex_files
            ],
            'dependency_analysis': {
                'has_circular_dependencies': dependency_data['analysis']['has_circular_dependencies'],
                'isolated_files': len(dependency_data['analysis']['isolated_files'])
            }
        }
    
    def _save_results(self, results: Dict):
        """Save analysis results to JSON file"""
        reports_dir = self.output_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        output_file = reports_dir / "analysis_results.json"
        
        # Convert non-serializable objects
        serializable_results = self._make_serializable(results)
        
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"Results saved to: {output_file}")
    
    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            return str(obj)
        else:
            return obj

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Codebase Archaeologist - AI-powered code analysis')
    parser.add_argument('path', help='Path to codebase or GitHub URL')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--output', default='./outputs', help='Output directory')
    
    args = parser.parse_args()
    
    # Initialize archaeologist
    archaeologist = CodebaseArchaeologist(args.config)
    
    # Determine source type and analyze
    if args.path.startswith('http'):
        results = archaeologist.analyze_github(args.path)
    else:
        results = archaeologist.analyze_local(args.path)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 ANALYSIS SUMMARY")
    print("="*60)
    summary = results['summary']
    print(f"Total Files: {results['metadata']['total_files']}")
    print(f"Total Functions: {summary['total_functions']}")
    print(f"Total Classes: {summary['total_classes']}")
    print(f"Total Lines: {summary['total_lines_of_code']}")
    print(f"Code Smells: {summary['total_code_smells']}")
    print(f"Avg Complexity: {summary['average_complexity']}")
    print(f"Maintainability: {summary['average_maintainability']}")
    print("="*60)

if __name__ == "__main__":
    main()