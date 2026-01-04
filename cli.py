#!/usr/bin/env python3
"""
Command Line Interface for Codebase Archaeologist
Enhanced CLI with rich formatting
"""

import argparse
import sys
from pathlib import Path
from main import CodebaseArchaeologist
from src.utils.logger import logger, setup_logger

def print_banner():
    """Print ASCII banner"""
    banner = """
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🏛️  CODEBASE ARCHAEOLOGIST  🏛️                        ║
║                                                            ║
║     AI-Powered Legacy Code Analysis System                 ║
║     Version 1.0.0                                          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_summary_table(summary: dict):
    """Print formatted summary table"""
    print("\n" + "="*70)
    print(" "*25 + "ANALYSIS SUMMARY")
    print("="*70)
    
    print(f"\n📊 Code Statistics:")
    print(f"   ├─ Total Functions:    {summary.get('total_functions', 0):>8}")
    print(f"   ├─ Total Classes:      {summary.get('total_classes', 0):>8}")
    print(f"   └─ Lines of Code:      {summary.get('total_lines_of_code', 0):>8,}")
    
    print(f"\n📈 Quality Metrics:")
    complexity = summary.get('average_complexity', 0)
    complexity_status = "✅ Good" if complexity <= 5 else "⚠️  Moderate" if complexity <= 10 else "❌ High"
    print(f"   ├─ Avg Complexity:     {complexity:>8.2f}  {complexity_status}")
    
    mi = summary.get('average_maintainability', 0)
    mi_rank = "A" if mi >= 20 else "B" if mi >= 10 else "C"
    mi_status = "✅ Good" if mi >= 20 else "⚠️  Moderate" if mi >= 10 else "❌ Poor"
    print(f"   ├─ Maintainability:    {mi:>8.2f}  ({mi_rank}) {mi_status}")
    
    smells = summary.get('total_code_smells', 0)
    smell_status = "✅ Few" if smells < 10 else "⚠️  Many" if smells < 30 else "❌ Critical"
    print(f"   └─ Code Smells:        {smells:>8}  {smell_status}")
    
    # Most complex files
    complex_files = summary.get('most_complex_files', [])
    if complex_files:
        print(f"\n⚠️  Most Complex Files:")
        for i, file_info in enumerate(complex_files[:5], 1):
            filename = Path(file_info['file']).name
            complexity = file_info['complexity']
            status = "🟢" if complexity <= 5 else "🟡" if complexity <= 10 else "🔴"
            print(f"   {i}. {status} {filename:<40} M={complexity:.1f}")
    
    print("\n" + "="*70 + "\n")

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="🏛️  Codebase Archaeologist - AI-Powered Code Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze local directory
  %(prog)s /path/to/your/project
  
  # Analyze GitHub repository
  %(prog)s https://github.com/username/repo.git
  
  # Use custom configuration
  %(prog)s /path/to/project --config custom_config.yaml
  
  # Specify output directory
  %(prog)s /path/to/project --output ./my_results
  
  # Quiet mode (minimal output)
  %(prog)s /path/to/project --quiet
  
  # Verbose mode (detailed logging)
  %(prog)s /path/to/project --verbose

For more information, visit: https://github.com/yourusername/codebase-archaeologist
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'path',
        help='Path to local codebase or GitHub repository URL'
    )
    
    # Optional arguments
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output directory for reports (overrides config)'
    )
    
    parser.add_argument(
        '--no-visualize',
        action='store_true',
        help='Skip generating visualization graphs'
    )
    
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Skip generating markdown report'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'markdown', 'html', 'all'],
        default='all',
        help='Output format: json, markdown, html, or all (default: all)'
    )
    
    parser.add_argument(
        '--open-html',
        action='store_true',
        help='Open HTML report in browser after generation'
    )
    
    # Logging options
    logging_group = parser.add_mutually_exclusive_group()
    logging_group.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Minimal output (errors only)'
    )
    
    logging_group.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output (debug level)'
    )
    
    # Info options
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Show banner (unless quiet mode)
    if not args.quiet:
        print_banner()
    
    # Setup logging
    if args.quiet:
        log_level = 'ERROR'
    elif args.verbose:
        log_level = 'DEBUG'
    else:
        log_level = 'INFO'
    
    setup_logger(level=log_level, log_file='archaeologist.log')
    
    try:
        # Initialize archaeologist
        logger.info("Initializing Codebase Archaeologist...")
        archaeologist = CodebaseArchaeologist(args.config)
        
        # Override output directory if specified
        if args.output:
            archaeologist.output_dir = Path(args.output)
            archaeologist.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine source type
        is_github = args.path.startswith('http')
        
        # Run analysis
        if is_github:
            logger.info(f"Analyzing GitHub repository: {args.path}")
            results = archaeologist.analyze_github(args.path)
        else:
            logger.info(f"Analyzing local codebase: {args.path}")
            results = archaeologist.analyze_local(args.path)
        
        if not results:
            logger.error("Analysis failed. Please check the path and try again.")
            sys.exit(1)
        
        # Print summary (unless quiet)
        if not args.quiet:
            print_summary_table(results['summary'])
        
        # Generate additional outputs
        html_report_path = None
        
        # Generate Markdown report
        if not args.no_report and args.format in ['markdown', 'all']:
            from src.reporting.markdown_generator import MarkdownGenerator
            generator = MarkdownGenerator(str(archaeologist.output_dir / "reports"))
            report_path = generator.generate_report(results)
            if report_path:
                logger.info(f"📄 Markdown report: {report_path}")
        
        # Generate HTML report
        if not args.no_report and args.format in ['html', 'all']:
            from src.reporting.html_generator import HTMLGenerator
            html_gen = HTMLGenerator(str(archaeologist.output_dir / "reports"))
            html_report_path = html_gen.generate_report(results)
            if html_report_path:
                logger.info(f"🌐 HTML report: {html_report_path}")
        
        if not args.no_visualize:
            from src.visualization.graph_generator import GraphGenerator
            viz_gen = GraphGenerator(str(archaeologist.output_dir / "graphs"))
            
            # Generate dependency graph
            if 'dependencies' in results and results['dependencies'].get('dependency_graph'):
                graph_path = viz_gen.generate_dependency_graph(
                    results['dependencies']['dependency_graph']
                )
                if graph_path:
                    logger.info(f"📊 Dependency graph: {graph_path}")
            
            # Generate complexity chart
            chart_path = viz_gen.generate_complexity_chart(results['files'])
            if chart_path:
                logger.info(f"📊 Complexity chart: {chart_path}")
            
            # Generate metrics summary
            summary_path = viz_gen.generate_metrics_summary(results['summary'])
            if summary_path:
                logger.info(f"📊 Metrics summary: {summary_path}")
        
        # Success message
        if not args.quiet:
            print("✅ Analysis complete!")
            print(f"\n📂 Results saved to: {archaeologist.output_dir}")
            if args.format in ['json', 'all']:
                print(f"   ├─ JSON:        {archaeologist.output_dir}/reports/analysis_results.json")
            if not args.no_report and args.format in ['markdown', 'all']:
                print(f"   ├─ Markdown:    {archaeologist.output_dir}/reports/analysis_report.md")
            if not args.no_report and args.format in ['html', 'all']:
                print(f"   ├─ HTML:        {archaeologist.output_dir}/reports/analysis_report.html")
            if not args.no_visualize:
                print(f"   └─ Graphs:      {archaeologist.output_dir}/graphs/")
            print()
        
        # Open HTML report in browser if requested
        if args.open_html and html_report_path:
            import webbrowser
            webbrowser.open(f'file://{Path(html_report_path).absolute()}')
            logger.info("🌐 Opened HTML report in browser")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        return 130
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.verbose)
        return 1

if __name__ == "__main__":
    sys.exit(main())