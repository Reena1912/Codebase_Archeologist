"""
Streamlit Web Dashboard for Codebase Archaeologist
Interactive web interface for code analysis
"""

import streamlit as st
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import CodebaseArchaeologist
from src.utils.logger import logger

# Page config
st.set_page_config(
    page_title="Codebase Archaeologist",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #155724;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #856404;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Header
    st.markdown('<p class="main-header">🏛️ Codebase Archaeologist</p>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Legacy Code Analysis & Documentation System**")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        analysis_type = st.radio(
            "Analysis Source:",
            ["Local Directory", "GitHub Repository"]
        )
        
        if analysis_type == "Local Directory":
            path = st.text_input(
                "Enter local path:",
                placeholder="/path/to/your/codebase",
                help="Absolute path to your local codebase"
            )
        else:
            path = st.text_input(
                "Enter GitHub URL:",
                placeholder="https://github.com/username/repo.git",
                help="GitHub repository URL"
            )
        
        st.markdown("---")
        
        st.subheader("Analysis Options")
        
        max_complexity = st.slider(
            "Max Complexity Threshold:",
            min_value=5,
            max_value=20,
            value=10,
            help="Flag functions with complexity above this value"
        )
        
        max_function_length = st.slider(
            "Max Function Length:",
            min_value=30,
            max_value=100,
            value=50,
            help="Flag functions longer than this"
        )
        
        analyze_button = st.button("🚀 Analyze Codebase", type="primary", use_container_width=True)
    
    # Main content
    if analyze_button:
        if not path:
            st.error("⚠️ Please enter a valid path or URL")
            return
        
        # Initialize archaeologist
        try:
            with st.spinner("🔧 Initializing analysis engine..."):
                archaeologist = CodebaseArchaeologist()
            
            # Run analysis
            with st.spinner(f"📊 Analyzing codebase at: {path}"):
                if analysis_type == "Local Directory":
                    results = archaeologist.analyze_local(path)
                else:
                    results = archaeologist.analyze_github(path)
            
            if not results:
                st.error("❌ Analysis failed. Check the path and try again.")
                return
            
            # Display results
            display_results(results)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            logger.error(f"Dashboard error: {e}")
    
    else:
        # Welcome screen
        display_welcome()

def display_welcome():
    """Display welcome screen"""
    st.info("👈 Configure analysis options in the sidebar and click **Analyze Codebase** to start")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔍 Static Analysis")
        st.write("Parse code structure using AST")
        st.write("- Extract functions & classes")
        st.write("- Analyze imports")
        st.write("- Calculate metrics")
    
    with col2:
        st.markdown("### 🧠 AI Insights")
        st.write("Generate explanations")
        st.write("- Function summaries")
        st.write("- Class descriptions")
        st.write("- Purpose inference")
    
    with col3:
        st.markdown("### 📊 Quality Metrics")
        st.write("Detect code issues")
        st.write("- Complexity analysis")
        st.write("- Code smells")
        st.write("- Dependencies")
    
    st.markdown("---")
    
    st.markdown("### 📚 Quick Start")
    st.code("""
# Analyze local directory
1. Select "Local Directory"
2. Enter path: /path/to/your/project
3. Click "Analyze Codebase"

# Analyze GitHub repository
1. Select "GitHub Repository"
2. Enter URL: https://github.com/user/repo.git
3. Click "Analyze Codebase"
    """)

def display_results(results: dict):
    """Display analysis results"""
    
    summary = results.get('summary', {})
    metadata = results.get('metadata', {})
    
    # Success message
    st.success(f"✅ Analysis completed in {metadata.get('analysis_time_seconds', 0):.2f}s")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview", "📁 Files", "🔗 Dependencies", "🔍 Code Smells", "💾 Export"
    ])
    
    # Tab 1: Overview
    with tab1:
        display_overview(summary, metadata)
    
    # Tab 2: Files
    with tab2:
        display_files(results.get('files', []))
    
    # Tab 3: Dependencies
    with tab3:
        display_dependencies(results.get('dependencies', {}))
    
    # Tab 4: Code Smells
    with tab4:
        display_code_smells(results.get('files', []))
    
    # Tab 5: Export
    with tab5:
        display_export(results)

def display_overview(summary: dict, metadata: dict):
    """Display overview tab"""
    
    st.header("📊 Repository Overview")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Files", metadata.get('total_files', 0))
    with col2:
        st.metric("Total Functions", summary.get('total_functions', 0))
    with col3:
        st.metric("Total Classes", summary.get('total_classes', 0))
    with col4:
        st.metric("Lines of Code", f"{summary.get('total_lines_of_code', 0):,}")
    
    st.markdown("---")
    
    # Quality metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        complexity = summary.get('average_complexity', 0)
        delta_color = "normal" if complexity <= 10 else "inverse"
        st.metric(
            "Avg Complexity",
            f"{complexity:.2f}",
            delta="Good" if complexity <= 5 else "High" if complexity > 10 else "Moderate",
            delta_color=delta_color
        )
    
    with col2:
        mi = summary.get('average_maintainability', 0)
        rank = "A" if mi >= 20 else "B" if mi >= 10 else "C"
        st.metric(
            "Maintainability",
            f"{mi:.1f} ({rank})",
            delta="Good" if mi >= 20 else "Poor" if mi < 10 else "Moderate"
        )
    
    with col3:
        smells = summary.get('total_code_smells', 0)
        st.metric(
            "Code Smells",
            smells,
            delta="Few issues" if smells < 10 else "Many issues"
        )
    
    st.markdown("---")
    
    # Most complex files
    st.subheader("⚠️ Most Complex Files")
    complex_files = summary.get('most_complex_files', [])
    
    if complex_files:
        for i, file_info in enumerate(complex_files, 1):
            filename = Path(file_info['file']).name
            complexity = file_info['complexity']
            
            color = "🟢" if complexity <= 5 else "🟡" if complexity <= 10 else "🔴"
            st.write(f"{i}. {color} **{filename}** - Complexity: {complexity:.2f}")
    else:
        st.info("No complex files detected")

def display_files(files: list):
    """Display files tab"""
    
    st.header("📁 File Analysis")
    
    if not files:
        st.warning("No files analyzed")
        return
    
    # Search/filter
    search = st.text_input("🔍 Search files:", placeholder="Enter filename...")
    
    # Filter files
    filtered_files = files
    if search:
        filtered_files = [f for f in files if search.lower() in f['filepath'].lower()]
    
    st.write(f"Showing {len(filtered_files)} of {len(files)} files")
    
    # Sort options
    sort_by = st.selectbox(
        "Sort by:",
        ["Complexity", "Lines", "Code Smells", "Name"]
    )
    
    if sort_by == "Complexity":
        filtered_files = sorted(
            filtered_files,
            key=lambda x: x.get('complexity', {}).get('cyclomatic_complexity', {}).get('average', 0),
            reverse=True
        )
    elif sort_by == "Lines":
        filtered_files = sorted(
            filtered_files,
            key=lambda x: x.get('file_info', {}).get('lines', 0),
            reverse=True
        )
    elif sort_by == "Code Smells":
        filtered_files = sorted(
            filtered_files,
            key=lambda x: x.get('code_smells', {}).get('total_smell_count', 0),
            reverse=True
        )
    else:
        filtered_files = sorted(filtered_files, key=lambda x: x['filepath'])
    
    # Display files
    for file_data in filtered_files[:20]:  # Limit to 20
        with st.expander(f"📄 {Path(file_data['filepath']).name}"):
            display_file_details(file_data)

def display_file_details(file_data: dict):
    """Display details for a single file"""
    
    file_info = file_data.get('file_info', {})
    complexity = file_data.get('complexity', {})
    smells = file_data.get('code_smells', {})
    doc = file_data.get('documentation', {})
    
    # Basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Lines", file_info.get('lines', 0))
    with col2:
        st.metric("Functions", len(file_data.get('functions', [])))
    with col3:
        st.metric("Classes", len(file_data.get('classes', [])))
    
    # Summary
    if doc.get('file_summary'):
        st.info(f"**Summary:** {doc['file_summary']}")
    
    # Complexity
    cc = complexity.get('cyclomatic_complexity', {})
    st.write(f"**Avg Complexity:** {cc.get('average', 0):.2f}")
    st.write(f"**Max Complexity:** {cc.get('max', 0)}")
    
    # Code smells
    smell_count = smells.get('total_smell_count', 0)
    if smell_count > 0:
        st.warning(f"⚠️ {smell_count} code smell(s) detected")

def display_dependencies(dependencies: dict):
    """Display dependencies tab"""
    
    st.header("🔗 Dependency Analysis")
    
    if not dependencies:
        st.warning("No dependency data available")
        return
    
    analysis = dependencies.get('analysis', {})
    
    # Most depended upon
    st.subheader("📌 Most Depended Upon Files")
    most_depended = analysis.get('most_depended_upon', [])
    
    if most_depended:
        for item in most_depended:
            filename = Path(item['file']).name
            count = item['dependents']
            st.write(f"- **{filename}** ({count} dependents)")
    else:
        st.info("No dependencies found")
    
    st.markdown("---")
    
    # Circular dependencies
    if analysis.get('has_circular_dependencies'):
        st.error("⚠️ Circular Dependencies Detected!")
        circular = analysis.get('circular_dependencies', [])
        for i, cycle in enumerate(circular, 1):
            cycle_str = " → ".join([Path(f).name for f in cycle])
            st.write(f"{i}. {cycle_str}")
    
    # Isolated files
    isolated = analysis.get('isolated_files', [])
    if isolated:
        st.subheader("🏝️ Isolated Files")
        st.write(f"Found {len(isolated)} file(s) with no dependencies:")
        for filepath in isolated[:10]:
            st.write(f"- {Path(filepath).name}")

def display_code_smells(files: list):
    """Display code smells tab"""
    
    st.header("🔍 Code Quality Issues")
    
    # Aggregate smells
    all_smells = {
        'long_functions': [],
        'missing_docstrings': [],
        'dead_code': [],
        'too_many_parameters': []
    }
    
    for file_data in files:
        smells = file_data.get('code_smells', {}).get('smells', {})
        filepath = file_data['filepath']
        
        for key in all_smells.keys():
            items = smells.get(key, [])
            for item in items:
                item['file'] = filepath
                all_smells[key].append(item)
    
    # Display each type
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📏 Long Functions")
        long_funcs = all_smells['long_functions']
        if long_funcs:
            st.write(f"Found {len(long_funcs)} long function(s):")
            for func in sorted(long_funcs, key=lambda x: x['lines'], reverse=True)[:10]:
                st.write(f"- `{func['name']}()` - {func['lines']} lines")
        else:
            st.success("✅ No long functions")
        
        st.markdown("---")
        
        st.subheader("☠️ Dead Code")
        dead = all_smells['dead_code']
        if dead:
            st.write(f"Found {len(dead)} potentially unused function(s):")
            for item in dead[:10]:
                st.write(f"- `{item['name']}()`")
        else:
            st.success("✅ No dead code detected")
    
    with col2:
        st.subheader("📝 Missing Docstrings")
        no_docs = all_smells['missing_docstrings']
        if no_docs:
            st.write(f"Found {len(no_docs)} item(s) without docstrings:")
            for item in no_docs[:10]:
                st.write(f"- `{item['name']}` ({item['type']})")
        else:
            st.success("✅ All documented")
        
        st.markdown("---")
        
        st.subheader("🔢 Too Many Parameters")
        many_params = all_smells['too_many_parameters']
        if many_params:
            st.write(f"Found {len(many_params)} function(s) with many parameters:")
            for func in many_params[:10]:
                st.write(f"- `{func['name']}()` - {func['parameter_count']} params")
        else:
            st.success("✅ Parameter counts are good")

def display_export(results: dict):
    """Display export tab"""
    
    st.header("💾 Export Results")
    
    st.write("Download analysis results in various formats:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON export
        st.subheader("📄 JSON Format")
        json_str = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="⬇️ Download JSON",
            data=json_str,
            file_name="analysis_results.json",
            mime="application/json"
        )
    
    with col2:
        # Summary export
        st.subheader("📊 Summary Report")
        summary_text = generate_summary_text(results)
        st.download_button(
            label="⬇️ Download Summary",
            data=summary_text,
            file_name="analysis_summary.txt",
            mime="text/plain"
        )
    
    with col3:
        # HTML export
        st.subheader("🌐 HTML Report")
        try:
            from src.reporting.html_generator import HTMLGenerator
            import tempfile
            
            with tempfile.TemporaryDirectory() as tmpdir:
                html_gen = HTMLGenerator(tmpdir)
                html_path = html_gen.generate_report(results, "report.html")
                
                if html_path:
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    st.download_button(
                        label="⬇️ Download HTML",
                        data=html_content,
                        file_name="analysis_report.html",
                        mime="text/html"
                    )
        except Exception as e:
            st.error(f"Could not generate HTML: {e}")
    
    st.markdown("---")
    
    # Show file locations
    st.info("""
    **Full reports saved to:**
    - JSON: `outputs/reports/analysis_results.json`
    - Markdown: `outputs/reports/analysis_report.md`
    - HTML: `outputs/reports/analysis_report.html`
    - Graphs: `outputs/graphs/`
    """)

def generate_summary_text(results: dict) -> str:
    """Generate plain text summary"""
    summary = results['summary']
    metadata = results['metadata']
    
    text = f"""
CODEBASE ARCHAEOLOGIST - ANALYSIS SUMMARY
{'='*60}

Source: {metadata.get('source', 'N/A')}
Analyzed: {metadata.get('analyzed_at', 'N/A')}
Duration: {metadata.get('analysis_time_seconds', 0)}s

STATISTICS
{'-'*60}
Total Files: {metadata.get('total_files', 0)}
Total Functions: {summary.get('total_functions', 0)}
Total Classes: {summary.get('total_classes', 0)}
Lines of Code: {summary.get('total_lines_of_code', 0):,}

QUALITY METRICS
{'-'*60}
Average Complexity: {summary.get('average_complexity', 0):.2f}
Maintainability Index: {summary.get('average_maintainability', 0):.2f}
Code Smells: {summary.get('total_code_smells', 0)}

{'='*60}
Generated by Codebase Archaeologist v1.0
    """
    
    return text

if __name__ == "__main__":
    main()