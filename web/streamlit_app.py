"""
Streamlit Web Dashboard for Codebase Archaeologist
Interactive web interface for code analysis
"""

import streamlit as st
import sys
import json
from pathlib import Path
import io

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import CodebaseArchaeologist
from src.utils.logger import logger

# Try to import visualization libraries
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

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
                # Use save_to_disk=False to keep everything in memory
                archaeologist = CodebaseArchaeologist(save_to_disk=False)
            
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
            
        except RuntimeError as e:
            # Handle specific errors with detailed messages
            error_msg = str(e)
            st.error(f"❌ {error_msg}")
            
            # Show additional help for common issues
            if "access denied" in error_msg.lower() or "authentication" in error_msg.lower():
                st.warning("""
                **💡 Tips for private repositories:**
                1. Make sure you have Git installed and configured
                2. For private repos, use SSH URL format: `git@github.com:username/repo.git`
                3. Ensure your SSH keys are set up: `ssh -T git@github.com`
                4. Or configure Git credentials: `git config --global credential.helper store`
                """)
            elif "not found" in error_msg.lower():
                st.warning("""
                **💡 Repository not found - please check:**
                1. The URL is correct and complete
                2. The repository exists on GitHub
                3. You have access if it's a private repository
                """)
            logger.error(f"Dashboard error: {e}")
            
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
    
    # Tabs - Added Visualizations tab
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Overview", "📈 Visualizations", "📁 Files", "🔗 Dependencies", "🔍 Code Smells", "💾 Export"
    ])
    
    # Tab 1: Overview
    with tab1:
        display_overview(summary, metadata)
    
    # Tab 2: Visualizations (in-memory charts)
    with tab2:
        display_visualizations(results)
    
    # Tab 3: Files
    with tab3:
        display_files(results.get('files', []))
    
    # Tab 4: Dependencies
    with tab4:
        display_dependencies(results.get('dependencies', {}))
    
    # Tab 5: Code Smells
    with tab5:
        display_code_smells(results.get('files', []))
    
    # Tab 6: Export
    with tab6:
        display_export(results)


def display_visualizations(results: dict):
    """Display interactive visualizations (in-memory, no file saving)"""
    
    st.header("📈 Interactive Visualizations")
    
    if not HAS_PLOTLY:
        st.warning("📦 Plotly is not installed. Install it with: `pip install plotly`")
        return
    
    if not HAS_PANDAS:
        st.warning("📦 Pandas is not installed. Install it with: `pip install pandas`")
        return
    
    files = results.get('files', [])
    summary = results.get('summary', {})
    dependencies = results.get('dependencies', {})
    
    # Sub-tabs for different visualizations
    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
        "📊 Complexity Charts", "📈 Metrics Dashboard", "🔗 Dependency Graph", "📁 File Analysis"
    ])
    
    with viz_tab1:
        display_complexity_charts(files)
    
    with viz_tab2:
        display_metrics_dashboard(summary)
    
    with viz_tab3:
        display_dependency_visualization(dependencies)
    
    with viz_tab4:
        display_file_analysis_charts(files)


def display_complexity_charts(files: list):
    """Display complexity-related charts"""
    
    st.subheader("🎯 Function Complexity Analysis")
    
    # Collect function data
    func_data = []
    for f in files[:30]:  # Limit for performance
        filepath = f.get('filepath', 'unknown')
        file_name = Path(filepath).name
        complexity_info = f.get('complexity', {})
        functions = complexity_info.get('cyclomatic_complexity', {}).get('functions', [])
        
        for func in functions:
            func_data.append({
                'File': file_name,
                'Function': func.get('name', 'unknown'),
                'Complexity': func.get('complexity', 0),
                'Lines': func.get('lines', 0)
            })
    
    if not func_data:
        st.info("No function data available for visualization")
        return
    
    df = pd.DataFrame(func_data)
    
    # Complexity scatter plot
    fig = px.scatter(
        df,
        x='File',
        y='Function',
        size='Complexity',
        color='Complexity',
        color_continuous_scale=['green', 'yellow', 'orange', 'red'],
        title='Function Complexity Heatmap',
        hover_data=['Complexity', 'Lines']
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Complexity distribution histogram
    st.subheader("📊 Complexity Distribution")
    fig2 = px.histogram(
        df,
        x='Complexity',
        nbins=20,
        title='Distribution of Function Complexity',
        color_discrete_sequence=['#3498db']
    )
    fig2.add_vline(x=10, line_dash="dash", line_color="red", 
                   annotation_text="High complexity threshold")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Top complex functions bar chart
    st.subheader("⚠️ Most Complex Functions")
    top_complex = df.nlargest(10, 'Complexity')
    fig3 = px.bar(
        top_complex,
        x='Complexity',
        y='Function',
        orientation='h',
        color='Complexity',
        color_continuous_scale=['green', 'yellow', 'orange', 'red'],
        title='Top 10 Most Complex Functions'
    )
    fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig3, use_container_width=True)


def display_metrics_dashboard(summary: dict):
    """Display metrics dashboard with gauges and charts"""
    
    st.subheader("📈 Quality Metrics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Maintainability gauge
        mi = summary.get('average_maintainability', 0)
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=mi,
            title={'text': "Maintainability Index"},
            delta={'reference': 20, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 10], 'color': "#e74c3c"},
                    {'range': [10, 20], 'color': "#f39c12"},
                    {'range': [20, 100], 'color': "#27ae60"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': mi
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Complexity gauge
        complexity = summary.get('average_complexity', 0)
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=complexity,
            title={'text': "Average Complexity"},
            delta={'reference': 10, 'decreasing': {'color': "green"}},
            gauge={
                'axis': {'range': [0, 30]},
                'bar': {'color': "#3498db"},
                'steps': [
                    {'range': [0, 5], 'color': "#27ae60"},
                    {'range': [5, 10], 'color': "#f39c12"},
                    {'range': [10, 30], 'color': "#e74c3c"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': complexity
                }
            }
        ))
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Code statistics bar chart
    st.subheader("📊 Code Statistics")
    stats_data = {
        'Metric': ['Functions', 'Classes', 'Code Smells', 'Lines (÷100)'],
        'Value': [
            summary.get('total_functions', 0),
            summary.get('total_classes', 0),
            summary.get('total_code_smells', 0),
            summary.get('total_lines_of_code', 0) / 100
        ]
    }
    fig3 = px.bar(
        stats_data,
        x='Metric',
        y='Value',
        color='Metric',
        title='Codebase Statistics'
    )
    st.plotly_chart(fig3, use_container_width=True)


def display_dependency_visualization(dependencies: dict):
    """Display dependency network visualization"""
    
    st.subheader("🔗 Dependency Network")
    
    if not dependencies:
        st.info("No dependency data available")
        return
    
    graph_data = dependencies.get('graph_data', {})
    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('edges', [])
    
    if not nodes:
        st.info("No dependency graph data available")
        return
    
    # Create network visualization using Plotly
    import networkx as nx
    
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node)
    for edge in edges:
        G.add_edge(edge['source'], edge['target'])
    
    # Limit nodes for readability
    if len(G.nodes()) > 40:
        st.warning(f"Graph has {len(G.nodes())} nodes, showing top 40 by connections")
        degrees = dict(G.degree())
        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:40]
        nodes_to_show = [node for node, _ in top_nodes]
        G = G.subgraph(nodes_to_show)
    
    if len(G.nodes()) == 0:
        st.info("No dependencies to visualize")
        return
    
    # Get positions using spring layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Create edge traces
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node traces
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    node_text = [Path(node).name for node in G.nodes()]
    node_degrees = [G.degree(node) for node in G.nodes()]
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=node_text,
        textposition='top center',
        textfont=dict(size=8),
        marker=dict(
            showscale=True,
            colorscale='YlOrRd',
            size=[10 + d * 3 for d in node_degrees],
            color=node_degrees,
            colorbar=dict(
                title='Connections',
                thickness=15
            )
        )
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title='File Dependency Network',
                       showlegend=False,
                       hovermode='closest',
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=600
                   ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Dependency statistics
    analysis = dependencies.get('analysis', {})
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Nodes", len(nodes))
        st.metric("Total Edges", len(edges))
    
    with col2:
        circular = analysis.get('has_circular_dependencies', False)
        if circular:
            st.error("⚠️ Circular dependencies detected!")
        else:
            st.success("✅ No circular dependencies")


def display_file_analysis_charts(files: list):
    """Display file-level analysis charts"""
    
    st.subheader("📁 File Analysis Charts")
    
    if not files:
        st.info("No file data available")
        return
    
    # Collect file data
    file_data = []
    for f in files:
        filepath = f.get('filepath', 'unknown')
        file_info = f.get('file_info', {})
        complexity_info = f.get('complexity', {})
        smells = f.get('code_smells', {})
        
        file_data.append({
            'File': Path(filepath).name,
            'Lines': file_info.get('lines', 0),
            'Complexity': complexity_info.get('cyclomatic_complexity', {}).get('average', 0),
            'Functions': len(f.get('functions', [])),
            'Classes': len(f.get('classes', [])),
            'Code Smells': smells.get('total_smell_count', 0)
        })
    
    df = pd.DataFrame(file_data)
    
    # File size treemap
    st.subheader("📊 File Size Distribution")
    fig = px.treemap(
        df,
        path=['File'],
        values='Lines',
        color='Complexity',
        color_continuous_scale=['green', 'yellow', 'orange', 'red'],
        title='File Size by Lines of Code (colored by complexity)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Scatter plot: Lines vs Complexity
    st.subheader("📈 Lines vs Complexity")
    fig2 = px.scatter(
        df,
        x='Lines',
        y='Complexity',
        size='Functions',
        color='Code Smells',
        hover_name='File',
        color_continuous_scale=['green', 'yellow', 'red'],
        title='File Complexity vs Size (bubble size = functions)'
    )
    st.plotly_chart(fig2, use_container_width=True)
    
    # Top files by various metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📏 Largest Files")
        top_lines = df.nlargest(10, 'Lines')
        fig3 = px.bar(
            top_lines,
            x='Lines',
            y='File',
            orientation='h',
            title='Top 10 Largest Files',
            color='Lines',
            color_continuous_scale='Blues'
        )
        fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.subheader("🔍 Most Code Smells")
        top_smells = df.nlargest(10, 'Code Smells')
        fig4 = px.bar(
            top_smells,
            x='Code Smells',
            y='File',
            orientation='h',
            title='Top 10 Files with Most Code Smells',
            color='Code Smells',
            color_continuous_scale='Reds'
        )
        fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig4, use_container_width=True)


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
    
    # Info about in-memory operation
    st.success("""
    ✨ **In-Memory Analysis Mode**
    
    All analysis results and visualizations are generated in-memory. 
    Nothing is saved to your disk unless you download the reports above.
    When you close this dashboard, all data will be cleared.
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