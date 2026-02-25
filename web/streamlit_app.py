"""
Streamlit Web Dashboard for Codebase Archaeologist
Interactive web interface for code analysis — v2 (enhanced UI)
"""

import streamlit as st
import sys
import json
import math
import time as _time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import CodebaseArchaeologist
from src.utils.logger import logger
from src.utils.helpers import load_config, get_default_config
from src.ai_engine.code_summarizer import CodeSummarizer
from src.ai_engine.model_manager import ModelManager
from src.ai_engine.prompt_templates import PromptTemplates

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

# ─── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Codebase Archaeologist",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session-state defaults ─────────────────────────────────────
for _key, _default in {
    "analysis_results": None,
    "analysis_history": [],
    "dark_mode": False,
    "selected_file_idx": None,
    "smell_filter": "All",
    "active_tab": 0,
}.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default

# ─── Theme-aware CSS ────────────────────────────────────────────
_ACCENT = "#6C63FF"
_ACCENT2 = "#00C9A7"

st.markdown(f"""
<style>
/* ── global resets / helpers ── */
.block-container {{ padding-top: 1.5rem; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg,#1a1a2e 0%,#16213e 100%); }}
section[data-testid="stSidebar"] * {{ color: #e0e0e0 !important; }}
section[data-testid="stSidebar"] .stSlider label, section[data-testid="stSidebar"] .stRadio label {{ color: #ccc !important; }}

/* ── hero header ── */
.hero {{
    background: linear-gradient(135deg, #6C63FF 0%, #00C9A7 100%);
    border-radius: 1rem;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    color: #fff;
}}
.hero h1 {{ margin:0; font-size:2.4rem; font-weight:800; }}
.hero p  {{ margin:.4rem 0 0; opacity:.88; font-size:1.05rem; }}

/* ── score ring ── */
.score-ring {{
    width: 120px; height: 120px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem; font-weight: 800; color: #fff;
    margin: 0 auto;
    box-shadow: 0 4px 24px rgba(0,0,0,.25);
}}

/* ── glass card ── */
.glass {{
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: .75rem;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    transition: transform .2s, box-shadow .2s;
}}
.glass:hover {{ transform: translateY(-2px); box-shadow: 0 8px 32px rgba(108,99,255,.18); }}
.glass h4 {{ margin-top:0; }}

/* ── severity badges ── */
.badge {{
    display:inline-block; padding: .15rem .55rem; border-radius:999px;
    font-size:.78rem; font-weight:600; margin-right:.35rem;
}}
.badge-critical {{ background:#e74c3c; color:#fff; }}
.badge-warning  {{ background:#f39c12; color:#fff; }}
.badge-info     {{ background:#3498db; color:#fff; }}
.badge-ok       {{ background:#27ae60; color:#fff; }}

/* ── step indicator ── */
.step-row {{ display:flex; gap:.5rem; align-items:center; margin:.35rem 0; }}
.step-dot {{
    width:22px; height:22px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:.75rem; color:#fff; flex-shrink:0;
}}
.step-done  {{ background:#27ae60; }}
.step-run   {{ background:{_ACCENT}; animation: pulse 1s infinite; }}
.step-wait  {{ background:#555; }}
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.45}} }}

/* ── feature card (welcome) ── */
.feat-card {{
    background: linear-gradient(135deg, rgba(108,99,255,.12) 0%, rgba(0,201,167,.08) 100%);
    border: 1px solid rgba(108,99,255,.22);
    border-radius: 1rem;
    padding: 1.8rem 1.5rem;
    text-align: center;
    transition: transform .25s;
    height: 100%;
}}
.feat-card:hover {{ transform: translateY(-4px); }}
.feat-icon {{ font-size: 2.8rem; margin-bottom:.5rem; }}
.feat-title {{ font-weight:700; font-size:1.15rem; margin-bottom:.45rem; }}

/* ── timeline ── */
.timeline {{ border-left: 3px solid {_ACCENT}; padding-left: 1.2rem; margin: 1rem 0; }}
.timeline-item {{ margin-bottom: .75rem; position: relative; }}
.timeline-item::before {{
    content: ''; position: absolute; left: -1.55rem; top: .35rem;
    width: 10px; height: 10px; border-radius: 50%; background: {_ACCENT};
}}

/* ── misc ── */
.kpi {{ text-align:center; }}
.kpi .value {{ font-size:2rem; font-weight:800; color:{_ACCENT}; }}
.kpi .label {{ font-size:.85rem; color:#999; }}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────
def _health_score(summary: dict) -> tuple:
    """Return (score 0-100, letter grade, colour)."""
    mi = summary.get("average_maintainability", 0)
    cx = summary.get("average_complexity", 0)
    sm = summary.get("total_code_smells", 0)
    funcs = max(summary.get("total_functions", 1), 1)

    # Weighted formula
    mi_norm = min(mi / 40, 1.0) * 100        # 40 = ideal MI
    cx_norm = max(1 - cx / 25, 0) * 100       # lower is better
    sm_norm = max(1 - sm / (funcs * 2), 0) * 100

    score = int(mi_norm * 0.45 + cx_norm * 0.35 + sm_norm * 0.20)
    score = max(0, min(score, 100))

    if score >= 80:
        return score, "A", "#27ae60"
    if score >= 60:
        return score, "B", "#2ecc71"
    if score >= 40:
        return score, "C", "#f39c12"
    if score >= 20:
        return score, "D", "#e67e22"
    return score, "F", "#e74c3c"


def _severity_badge(level: str) -> str:
    cls = {"critical": "badge-critical", "warning": "badge-warning",
           "info": "badge-info"}.get(level, "badge-ok")
    return f'<span class="badge {cls}">{level.upper()}</span>'


def _render_step(label: str, status: str = "wait"):
    """Render a single analysis step (done / run / wait)."""
    icon_map = {"done": "✓", "run": "⟳", "wait": "·"}
    css = f"step-{status}"
    return f'<div class="step-row"><div class="step-dot {css}">{icon_map.get(status,"·")}</div><span>{label}</span></div>'


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────
def main():
    """Main application"""

    # ── Hero header ──
    st.markdown("""
    <div class="hero">
        <h1>🏛️ Codebase Archaeologist</h1>
        <p>AI-Powered Legacy Code Analysis &amp; Documentation System</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("## ⚙️ Analysis Setup")

        analysis_type = st.radio(
            "Source type",
            ["GitHub Repository", "Local Directory"],
            horizontal=True,
        )

        if analysis_type == "Local Directory":
            path = st.text_input(
                "📁 Local path",
                placeholder="C:\\projects\\my-app",
                help="Absolute path to your local codebase",
            )
        else:
            path = st.text_input(
                "🐙 GitHub URL",
                placeholder="https://github.com/user/repo.git",
                help="Public or private GitHub repository URL",
            )

        with st.expander("🔧 Advanced options", expanded=False):
            max_complexity = st.slider("Complexity threshold", 5, 25, 10,
                                       help="Flag functions above this value")
            max_function_length = st.slider("Max function length (lines)", 20, 150, 50)
            st.caption("Thresholds for code-smell detection.")

        analyze_button = st.button("🚀  Analyze", type="primary", use_container_width=True)

        # ── History ──
        if st.session_state["analysis_history"]:
            st.markdown("---")
            st.markdown("### 🕑 History")
            for i, entry in enumerate(reversed(st.session_state["analysis_history"][-5:])):
                if st.button(f"📂 {entry['label']}", key=f"hist_{i}", use_container_width=True):
                    st.session_state["analysis_results"] = entry["results"]
                    st.rerun()

        st.markdown("---")
        st.caption("v2.0 · Built with Streamlit + Plotly")

    # ── Route ──
    if analyze_button:
        if not path:
            st.error("⚠️ Please enter a valid path or URL")
            return
        _run_analysis(path, analysis_type)
    elif st.session_state["analysis_results"]:
        display_results(st.session_state["analysis_results"])
    else:
        display_welcome()


# ─────────────────────────────────────────────────────────────────
# ANALYSIS RUNNER  (step-by-step progress)
# ─────────────────────────────────────────────────────────────────
def _run_analysis(path: str, analysis_type: str):
    """Run analysis with animated step indicator."""

    steps = [
        "Initializing engine",
        "Cloning / loading files",
        "Parsing AST & metrics",
        "Extracting dependencies",
        "Detecting code smells",
        "Generating AI summaries",
        "Compiling results",
    ]
    progress_bar = st.progress(0, text="Starting analysis…")
    step_placeholder = st.empty()

    def _show_steps(current_idx: int):
        html = ""
        for i, s in enumerate(steps):
            if i < current_idx:
                html += _render_step(s, "done")
            elif i == current_idx:
                html += _render_step(s, "run")
            else:
                html += _render_step(s, "wait")
        step_placeholder.markdown(html, unsafe_allow_html=True)

    try:
        # Step 0 – init
        _show_steps(0)
        progress_bar.progress(5, text="Initializing…")
        archaeologist = CodebaseArchaeologist(save_to_disk=False)

        # Step 1 – load
        _show_steps(1)
        progress_bar.progress(15, text="Loading codebase…")

        # Step 2 – analyse (bulk)
        _show_steps(2)
        progress_bar.progress(30, text="Parsing & analysing…")

        if analysis_type == "Local Directory":
            results = archaeologist.analyze_local(path)
        else:
            results = archaeologist.analyze_github(path)

        # Steps 3-6 – fast (already done inside analyze_*)
        for idx in range(3, len(steps)):
            _show_steps(idx)
            progress_bar.progress(30 + idx * 10, text=f"{steps[idx]}…")
            _time.sleep(0.25)  # brief visual pause

        progress_bar.progress(100, text="Done!")
        _show_steps(len(steps))  # all done

        if not results:
            st.error("❌ Analysis failed. Check the path and try again.")
            return

        # Persist
        st.session_state["analysis_results"] = results
        label = Path(path).name if "/" not in path and "\\" not in path else path.rstrip("/").split("/")[-1].split("\\")[-1]
        st.session_state["analysis_history"].append({
            "label": label or "analysis",
            "results": results,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        })

        st.toast("✅ Analysis complete!", icon="🎉")
        _time.sleep(0.5)
        st.rerun()

    except RuntimeError as e:
        progress_bar.empty()
        step_placeholder.empty()
        error_msg = str(e)
        st.error(f"❌ {error_msg}")
        if "access denied" in error_msg.lower() or "authentication" in error_msg.lower():
            st.warning("💡 **Tip:** For private repos use SSH format `git@github.com:user/repo.git` and ensure credentials are configured.")
        elif "not found" in error_msg.lower():
            st.warning("💡 Double-check the URL / path exists and you have access.")
        logger.error(f"Dashboard error: {e}")
    except Exception as e:
        progress_bar.empty()
        step_placeholder.empty()
        st.error(f"❌ {e}")
        logger.error(f"Dashboard error: {e}")


# ─────────────────────────────────────────────────────────────────
# WELCOME SCREEN
# ─────────────────────────────────────────────────────────────────
def display_welcome():
    """Visually rich landing page."""

    st.markdown("#### 👈 Enter a path or GitHub URL in the sidebar to begin")
    st.write("")

    cols = st.columns(3)
    cards = [
        ("🔍", "Static Analysis", "AST parsing, function & class extraction, import mapping, and cyclomatic complexity metrics."),
        ("🧠", "AI Insights", "Automatic function summaries, class descriptions, and purpose inference powered by transformers."),
        ("📊", "Quality Metrics", "Complexity scoring, code-smell detection, dependency graphing, and maintainability index."),
    ]
    for col, (icon, title, desc) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class="feat-card">
                <div class="feat-icon">{icon}</div>
                <div class="feat-title">{title}</div>
                <div style="font-size:.92rem;color:#aaa;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    with st.expander("📚 Quick-start guide", expanded=False):
        st.markdown("""
**GitHub repo (easiest)**
1. Paste a public repo URL, e.g. `https://github.com/pallets/flask.git`
2. Click **Analyze** — the repo is cloned automatically.

**Local directory**
1. Switch to *Local Directory* in the sidebar.
2. Enter the absolute path, e.g. `C:\\projects\\my-app`
3. Click **Analyze**.

Results include interactive charts, dependency graphs, code-smell cards, and downloadable reports.
        """)

def display_results(results: dict):
    """Display analysis results with an interactive tabbed layout."""

    summary = results.get("summary", {})
    metadata = results.get("metadata", {})
    files = results.get("files", [])

    # ── Health-score banner ──
    score, grade, colour = _health_score(summary)
    bcol1, bcol2 = st.columns([1, 4])
    with bcol1:
        st.markdown(
            f'<div class="score-ring" style="background:{colour};">{grade}</div>'
            f'<p style="text-align:center;margin-top:.4rem;font-size:.85rem;">Health <b>{score}/100</b></p>',
            unsafe_allow_html=True,
        )
    with bcol2:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Files", metadata.get("total_files", 0))
        c2.metric("Functions", summary.get("total_functions", 0))
        c3.metric("Classes", summary.get("total_classes", 0))
        c4.metric("Lines", f"{summary.get('total_lines_of_code', 0):,}")
        c5.metric("Time", f"{metadata.get('analysis_time_seconds', 0):.1f}s")

    st.write("")

    # ── Tab bar ──
    tabs = st.tabs([
        "📊 Overview",
        "📈 Visualizations",
        "📁 File Explorer",
        "🔗 Dependencies",
        "🐛 Code Smells",
        "💾 Export",
        "� AI Lab",
    ])

    with tabs[0]:
        _tab_overview(summary, metadata, files)
    with tabs[1]:
        _tab_visualizations(results)
    with tabs[2]:
        _tab_files(files)
    with tabs[3]:
        _tab_dependencies(results.get("dependencies", {}))
    with tabs[4]:
        _tab_code_smells(files)
    with tabs[5]:
        _tab_export(results)
    with tabs[6]:
        _tab_ai_playground()


# ─────────────────────────────────────────────────────────────────
# TAB 0 — Overview
# ─────────────────────────────────────────────────────────────────
def _tab_overview(summary: dict, metadata: dict, files: list):
    st.subheader("📊 Repository Overview")

    # Quality KPIs with radar chart
    col_left, col_right = st.columns([3, 2])

    with col_left:
        qc1, qc2, qc3 = st.columns(3)
        cx = summary.get("average_complexity", 0)
        mi = summary.get("average_maintainability", 0)
        sm = summary.get("total_code_smells", 0)
        rank = "A" if mi >= 20 else "B" if mi >= 10 else "C"

        qc1.metric("Avg Complexity", f"{cx:.2f}",
                    delta="Good" if cx <= 5 else ("High" if cx > 10 else "Moderate"),
                    delta_color="normal" if cx <= 10 else "inverse")
        qc2.metric("Maintainability", f"{mi:.1f} ({rank})",
                    delta="Good" if mi >= 20 else ("Poor" if mi < 10 else "Moderate"))
        qc3.metric("Code Smells", sm,
                    delta="Few" if sm < 10 else "Many",
                    delta_color="normal" if sm < 10 else "inverse")

    with col_right:
        if HAS_PLOTLY:
            cats = ["Maintainability", "Low Complexity", "Documentation", "Few Smells", "Modularity"]
            vals = [
                min(mi / 40, 1) * 100,
                max(1 - cx / 25, 0) * 100,
                max(1 - sm / max(summary.get("total_functions", 1), 1), 0) * 100,
                max(1 - sm / 30, 0) * 100,
                min(summary.get("total_classes", 0) / max(summary.get("total_functions", 1), 1) * 100, 100),
            ]
            fig = go.Figure(go.Scatterpolar(r=vals + [vals[0]], theta=cats + [cats[0]],
                                            fill="toself", fillcolor="rgba(108,99,255,.18)",
                                            line_color="#6C63FF"))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                              showlegend=False, margin=dict(l=40, r=40, t=30, b=30), height=260)
            st.plotly_chart(fig, key="radar_overview", width="stretch")

    st.markdown("---")

    # Most-complex files as interactive cards
    st.subheader("⚠️ Hotspot Files")
    complex_files = summary.get("most_complex_files", [])
    if complex_files:
        cols = st.columns(min(len(complex_files), 5))
        for col, finfo in zip(cols, complex_files):
            cx_val = finfo["complexity"]
            badge = "badge-critical" if cx_val > 10 else ("badge-warning" if cx_val > 5 else "badge-ok")
            with col:
                st.markdown(f"""
                <div class="glass">
                    <h4 style="margin-bottom:.3rem;">{Path(finfo['file']).name}</h4>
                    <span class="badge {badge}">complexity {cx_val:.1f}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.success("No hotspot files – all complexity is under control.")


# ─────────────────────────────────────────────────────────────────
# TAB 1 — Visualizations
# ─────────────────────────────────────────────────────────────────
def _tab_visualizations(results: dict):
    if not HAS_PLOTLY or not HAS_PANDAS:
        st.warning("Install **plotly** and **pandas** for interactive charts.")
        return

    files = results.get("files", [])
    summary = results.get("summary", {})
    deps = results.get("dependencies", {})

    viz = st.radio("Chart", [
        "Complexity Heatmap",
        "Metrics Gauges",
        "File Treemap",
        "Lines vs Complexity Scatter",
        "Dependency Network",
    ], horizontal=True)

    if viz == "Complexity Heatmap":
        _viz_complexity_heatmap(files)
    elif viz == "Metrics Gauges":
        _viz_gauges(summary)
    elif viz == "File Treemap":
        _viz_treemap(files)
    elif viz == "Lines vs Complexity Scatter":
        _viz_scatter(files)
    elif viz == "Dependency Network":
        _viz_dependency_network(deps)


def _collect_func_df(files):
    rows = []
    for f in files[:50]:
        fname = Path(f.get("filepath", "?")).name
        for func in f.get("complexity", {}).get("cyclomatic_complexity", {}).get("functions", []):
            rows.append({
                "File": fname,
                "Function": func.get("name", "?"),
                "Complexity": func.get("complexity", 0),
                "Lines": func.get("lines", 0),
            })
    return pd.DataFrame(rows) if rows else None


def _viz_complexity_heatmap(files):
    df = _collect_func_df(files)
    if df is None or df.empty:
        st.info("No function data.")
        return

    # Interactive: let user pick min complexity to highlight
    threshold = st.slider("Highlight above complexity", 1, 25, 10, key="cx_thresh")
    df["Above"] = df["Complexity"] >= threshold

    fig = px.scatter(df, x="File", y="Function", size="Complexity", color="Complexity",
                     color_continuous_scale=["#27ae60", "#f1c40f", "#e74c3c"],
                     hover_data=["Lines"], title="Function Complexity Heatmap")
    fig.update_layout(xaxis_tickangle=-45, height=520)
    st.plotly_chart(fig, key="heatmap", width="stretch")

    # Distribution
    st.markdown("##### Distribution")
    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.histogram(df, x="Complexity", nbins=20, color_discrete_sequence=["#6C63FF"],
                            title="Complexity Distribution")
        fig2.add_vline(x=threshold, line_dash="dash", line_color="red",
                       annotation_text=f"threshold ({threshold})")
        st.plotly_chart(fig2, key="hist_cx", width="stretch")
    with col2:
        top = df.nlargest(10, "Complexity")
        fig3 = px.bar(top, x="Complexity", y="Function", orientation="h",
                      color="Complexity", color_continuous_scale=["#27ae60", "#f1c40f", "#e74c3c"],
                      title="Top 10 Complex Functions")
        fig3.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig3, key="bar_cx", width="stretch")


def _viz_gauges(summary):
    mi = summary.get("average_maintainability", 0)
    cx = summary.get("average_complexity", 0)

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=mi,
            title={"text": "Maintainability Index"},
            delta={"reference": 20, "increasing": {"color": "green"}},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#6C63FF"},
                   "steps": [{"range": [0, 10], "color": "#e74c3c"},
                             {"range": [10, 20], "color": "#f39c12"},
                             {"range": [20, 100], "color": "#27ae60"}]}))
        fig.update_layout(height=300)
        st.plotly_chart(fig, key="gauge_mi", width="stretch")

    with col2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=cx,
            title={"text": "Average Complexity"},
            delta={"reference": 10, "decreasing": {"color": "green"}},
            gauge={"axis": {"range": [0, 30]}, "bar": {"color": "#6C63FF"},
                   "steps": [{"range": [0, 5], "color": "#27ae60"},
                             {"range": [5, 10], "color": "#f39c12"},
                             {"range": [10, 30], "color": "#e74c3c"}]}))
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, key="gauge_cx", width="stretch")

    # Stat bars
    stats = {"Functions": summary.get("total_functions", 0),
             "Classes": summary.get("total_classes", 0),
             "Code Smells": summary.get("total_code_smells", 0),
             "Lines (÷100)": summary.get("total_lines_of_code", 0) / 100}
    fig3 = px.bar(x=list(stats.keys()), y=list(stats.values()), color=list(stats.keys()),
                  title="Codebase Statistics")
    st.plotly_chart(fig3, key="stats_bar", width="stretch")


def _collect_file_df(files):
    rows = []
    for f in files:
        fi = f.get("file_info", {})
        ci = f.get("complexity", {}).get("cyclomatic_complexity", {})
        rows.append({
            "File": Path(f.get("filepath", "?")).name,
            "Lines": fi.get("lines", 0),
            "Complexity": ci.get("average", 0),
            "Functions": len(f.get("functions", [])),
            "Classes": len(f.get("classes", [])),
            "Code Smells": f.get("code_smells", {}).get("total_smell_count", 0),
        })
    return pd.DataFrame(rows) if rows else None


def _viz_treemap(files):
    df = _collect_file_df(files)
    if df is None or df.empty:
        st.info("No file data.")
        return
    fig = px.treemap(df, path=["File"], values="Lines", color="Complexity",
                     color_continuous_scale=["#27ae60", "#f1c40f", "#e74c3c"],
                     title="File Size (coloured by complexity)")
    fig.update_layout(height=500)
    st.plotly_chart(fig, key="treemap", width="stretch")


def _viz_scatter(files):
    df = _collect_file_df(files)
    if df is None or df.empty:
        st.info("No file data.")
        return
    fig = px.scatter(df, x="Lines", y="Complexity", size="Functions",
                     color="Code Smells", hover_name="File",
                     color_continuous_scale=["#27ae60", "#f1c40f", "#e74c3c"],
                     title="Lines vs Complexity (bubble = functions)")
    st.plotly_chart(fig, key="scatter_lc", width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        top_l = df.nlargest(10, "Lines")
        fig2 = px.bar(top_l, x="Lines", y="File", orientation="h", color="Lines",
                      color_continuous_scale="Blues", title="Largest Files")
        fig2.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig2, key="bar_lines", width="stretch")
    with col2:
        top_s = df.nlargest(10, "Code Smells")
        fig3 = px.bar(top_s, x="Code Smells", y="File", orientation="h", color="Code Smells",
                      color_continuous_scale="Reds", title="Most Code Smells")
        fig3.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig3, key="bar_smells", width="stretch")


def _viz_dependency_network(dependencies):
    if not dependencies:
        st.info("No dependency data.")
        return
    graph_data = dependencies.get("graph_data", {})
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])
    if not nodes:
        st.info("No dependency graph data.")
        return

    import networkx as nx
    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n)
    for e in edges:
        G.add_edge(e["source"], e["target"])

    max_nodes = st.slider("Max visible nodes", 5, min(len(nodes), 80), min(len(nodes), 40), key="dep_max")
    if len(G.nodes()) > max_nodes:
        degrees = dict(G.degree())
        keep = [n for n, _ in sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:max_nodes]]
        G = G.subgraph(keep)

    if not G.nodes():
        st.info("No dependencies to show.")
        return

    pos = nx.spring_layout(G, k=2, iterations=50)
    ex, ey = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        ex += [x0, x1, None]; ey += [y0, y1, None]

    edge_trace = go.Scatter(x=ex, y=ey, mode="lines", line=dict(width=.6, color="#888"), hoverinfo="none")
    nx_vals = [pos[n][0] for n in G.nodes()]
    ny_vals = [pos[n][1] for n in G.nodes()]
    labels = [Path(n).name for n in G.nodes()]
    degs = [G.degree(n) for n in G.nodes()]

    node_trace = go.Scatter(
        x=nx_vals, y=ny_vals, mode="markers+text", text=labels, textposition="top center",
        textfont=dict(size=9), hoverinfo="text",
        marker=dict(showscale=True, colorscale="YlOrRd", size=[10 + d * 3 for d in degs],
                    color=degs, colorbar=dict(title="Connections", thickness=15)))

    fig = go.Figure([edge_trace, node_trace])
    fig.update_layout(title="Dependency Network", showlegend=False, hovermode="closest",
                      xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                      yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), height=600)
    st.plotly_chart(fig, key="dep_net", width="stretch")

    analysis = dependencies.get("analysis", {})
    mc1, mc2 = st.columns(2)
    mc1.metric("Nodes", len(nodes))
    mc1.metric("Edges", len(edges))
    circ = analysis.get("has_circular_dependencies", False)
    if circ:
        mc2.error("⚠️ Circular dependencies detected!")
    else:
        mc2.success("✅ No circular dependencies")


# ─────────────────────────────────────────────────────────────────
# TAB 2 — File Explorer
# ─────────────────────────────────────────────────────────────────
def _tab_files(files: list):
    if not files:
        st.warning("No files analysed.")
        return

    st.subheader("📁 Interactive File Explorer")

    # Toolbar row
    tc1, tc2, tc3 = st.columns([3, 1, 1])
    with tc1:
        search = st.text_input("🔍 Filter files", placeholder="Type to search…", key="f_search")
    with tc2:
        sort_by = st.selectbox("Sort", ["Complexity", "Lines", "Code Smells", "Name"], key="f_sort")
    with tc3:
        limit = st.number_input("Show", min_value=5, max_value=200, value=20, step=5, key="f_limit")

    filtered = files
    if search:
        filtered = [f for f in files if search.lower() in f["filepath"].lower()]

    key_map = {
        "Complexity": lambda x: x.get("complexity", {}).get("cyclomatic_complexity", {}).get("average", 0),
        "Lines": lambda x: x.get("file_info", {}).get("lines", 0),
        "Code Smells": lambda x: x.get("code_smells", {}).get("total_smell_count", 0),
        "Name": lambda x: x["filepath"],
    }
    reverse = sort_by != "Name"
    filtered = sorted(filtered, key=key_map[sort_by], reverse=reverse)

    st.caption(f"Showing {min(len(filtered), limit)} of {len(files)} files")

    for fd in filtered[:limit]:
        fi = fd.get("file_info", {})
        cc = fd.get("complexity", {}).get("cyclomatic_complexity", {})
        smell_n = fd.get("code_smells", {}).get("total_smell_count", 0)
        cx_avg = cc.get("average", 0)

        # Build badges string
        badges = ""
        if cx_avg > 10:
            badges += '<span class="badge badge-critical">complex</span>'
        elif cx_avg > 5:
            badges += '<span class="badge badge-warning">moderate</span>'
        if smell_n > 0:
            badges += f'<span class="badge badge-info">{smell_n} smell{"s" if smell_n != 1 else ""}</span>'

        label = f"📄 {Path(fd['filepath']).name}  —  {fi.get('lines', 0)} lines  |  cx {cx_avg:.1f}"
        with st.expander(label):
            st.markdown(badges, unsafe_allow_html=True)
            _render_file_detail(fd)


def _render_file_detail(fd: dict):
    fi = fd.get("file_info", {})
    cc = fd.get("complexity", {}).get("cyclomatic_complexity", {})
    doc = fd.get("documentation", {})
    smells = fd.get("code_smells", {})

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lines", fi.get("lines", 0))
    c2.metric("Functions", len(fd.get("functions", [])))
    c3.metric("Classes", len(fd.get("classes", [])))
    c4.metric("Max CX", cc.get("max", 0))

    if doc.get("file_summary"):
        st.info(f"🧠 **AI Summary:** {doc['file_summary']}")

    # Functions table
    funcs = fd.get("functions", [])
    if funcs:
        with st.expander(f"🔧 Functions ({len(funcs)})", expanded=False):
            for fn in funcs:
                name = fn.get("name", "?")
                params = ", ".join(fn.get("params", []))
                st.markdown(f"- `{name}({params})`")

    # Classes table
    classes = fd.get("classes", [])
    if classes:
        with st.expander(f"🏗️ Classes ({len(classes)})", expanded=False):
            for cls in classes:
                st.markdown(f"- **{cls.get('name', '?')}** — {len(cls.get('methods', []))} methods")

    # Smells detail
    smell_count = smells.get("total_smell_count", 0)
    if smell_count:
        with st.expander(f"🐛 Code Smells ({smell_count})", expanded=False):
            for cat, items in smells.get("smells", {}).items():
                if items:
                    st.markdown(f"**{cat.replace('_', ' ').title()}**")
                    for it in items:
                        st.markdown(f"  - `{it.get('name', '?')}`")


# ─────────────────────────────────────────────────────────────────
# TAB 3 — Dependencies
# ─────────────────────────────────────────────────────────────────
def _tab_dependencies(dependencies: dict):
    st.subheader("🔗 Dependency Analysis")
    if not dependencies:
        st.warning("No dependency data available.")
        return

    analysis = dependencies.get("analysis", {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### 📌 Most Depended-Upon")
        most_dep = analysis.get("most_depended_upon", [])
        if most_dep:
            for item in most_dep:
                name = Path(item["file"]).name
                cnt = item["dependents"]
                pct = min(cnt / max(len(dependencies.get("graph_data", {}).get("nodes", [1])), 1) * 100, 100)
                st.markdown(f"""
                <div class="glass" style="padding:.7rem 1rem;">
                    <strong>{name}</strong>
                    <div style="background:#333;border-radius:4px;height:8px;margin-top:.3rem;">
                        <div style="width:{pct:.0f}%;background:#6C63FF;height:100%;border-radius:4px;"></div>
                    </div>
                    <small>{cnt} dependent(s)</small>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No dependencies found.")

    with col2:
        # Circular deps
        if analysis.get("has_circular_dependencies"):
            st.error("⚠️ Circular Dependencies Detected!")
            for i, cycle in enumerate(analysis.get("circular_dependencies", []), 1):
                chain = " → ".join(Path(f).name for f in cycle)
                st.markdown(f"{i}. `{chain}`")
        else:
            st.success("✅ No circular dependencies")

        # Isolated
        isolated = analysis.get("isolated_files", [])
        if isolated:
            with st.expander(f"🏝️ Isolated files ({len(isolated)})"):
                for fp in isolated[:15]:
                    st.write(f"- {Path(fp).name}")


# ─────────────────────────────────────────────────────────────────
# TAB 4 — Code Smells  (interactive filter)
# ─────────────────────────────────────────────────────────────────
def _tab_code_smells(files: list):
    st.subheader("🐛 Code Quality Issues")

    # Aggregate
    cats = {
        "long_functions": {"icon": "📏", "label": "Long Functions", "sev": "warning"},
        "missing_docstrings": {"icon": "📝", "label": "Missing Docstrings", "sev": "info"},
        "dead_code": {"icon": "☠️", "label": "Dead Code", "sev": "warning"},
        "too_many_parameters": {"icon": "🔢", "label": "Too Many Parameters", "sev": "critical"},
    }
    collected: dict[str, list] = {k: [] for k in cats}

    for fd in files:
        smells = fd.get("code_smells", {}).get("smells", {})
        for key in collected:
            for item in smells.get(key, []):
                item["_file"] = Path(fd["filepath"]).name
                collected[key].append(item)

    total = sum(len(v) for v in collected.values())
    counts = {k: len(v) for k, v in collected.items()}

    # Filter bar
    options = ["All"] + [cats[k]["label"] for k in cats if counts[k]]
    chosen = st.radio("Filter", options, horizontal=True, key="smell_radio")

    st.caption(f"{total} issue(s) found across {len(files)} file(s)")

    # Render cards
    for key, meta in cats.items():
        if chosen != "All" and chosen != meta["label"]:
            continue
        items = collected[key]
        if not items:
            continue

        sev = meta["sev"]
        st.markdown(f"#### {meta['icon']} {meta['label']}  {_severity_badge(sev)}", unsafe_allow_html=True)

        # Show as a mini-table inside glass cards (3 per row)
        for i in range(0, len(items), 3):
            cols = st.columns(3)
            for col, item in zip(cols, items[i: i + 3]):
                name = item.get("name", "?")
                detail = ""
                if "lines" in item:
                    detail = f"{item['lines']} lines"
                elif "parameter_count" in item:
                    detail = f"{item['parameter_count']} params"
                elif "type" in item:
                    detail = item["type"]
                col.markdown(f"""
                <div class="glass">
                    <strong style="color:#e0e0e0;">{name}</strong><br>
                    <small>{item.get('_file', '')}</small><br>
                    <span class="badge badge-{sev}">{detail or sev}</span>
                </div>
                """, unsafe_allow_html=True)

    if total == 0:
        st.success("🎉 No code smells detected — nice work!")


# ─────────────────────────────────────────────────────────────────
# TAB 5 — Export
# ─────────────────────────────────────────────────────────────────
def _tab_export(results: dict):
    st.subheader("💾 Export Results")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="glass" style="text-align:center;">
            <h4>📄 JSON</h4>
            <p style="font-size:.85rem;color:#aaa;">Raw analysis data</p>
        </div>""", unsafe_allow_html=True)
        json_str = json.dumps(results, indent=2, default=str)
        st.download_button("⬇️  Download JSON", json_str,
                           file_name="analysis_results.json", mime="application/json",
                           use_container_width=True)

    with col2:
        st.markdown("""
        <div class="glass" style="text-align:center;">
            <h4>📊 Summary</h4>
            <p style="font-size:.85rem;color:#aaa;">Plain-text report</p>
        </div>""", unsafe_allow_html=True)
        st.download_button("⬇️  Download Summary", _generate_summary_text(results),
                           file_name="analysis_summary.txt", mime="text/plain",
                           use_container_width=True)

    with col3:
        st.markdown("""
        <div class="glass" style="text-align:center;">
            <h4>🌐 HTML</h4>
            <p style="font-size:.85rem;color:#aaa;">Styled report</p>
        </div>""", unsafe_allow_html=True)
        try:
            from src.reporting.html_generator import HTMLGenerator
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                html_gen = HTMLGenerator(tmpdir)
                html_path = html_gen.generate_report(results, "report.html")
                if html_path:
                    with open(html_path, "r", encoding="utf-8") as f:
                        html_content = f.read()
                    st.download_button("⬇️  Download HTML", html_content,
                                       file_name="analysis_report.html", mime="text/html",
                                       use_container_width=True)
        except Exception as e:
            st.error(f"Could not generate HTML: {e}")

    st.markdown("---")
    st.markdown("""
    <div class="glass" style="text-align:center;">
        ✨ <strong>In-Memory Mode</strong> — nothing is saved to disk unless you download above.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# TAB 6 — AI Lab
# ─────────────────────────────────────────────────────────────────
def _tab_ai_playground():
    """Interactive AI lab — paste code & see the AI engine in action."""

    st.subheader("� AI Lab")
    st.markdown(
        '<p style="opacity:.7;">Experiment with every part of the AI engine live — '
        'paste code, tweak inputs, and watch results update instantly.</p>',
        unsafe_allow_html=True,
    )

    # ── Initialise AI objects (cached) ──
    @st.cache_resource
    def _get_ai_objects():
        try:
            cfg = load_config()
        except Exception:
            cfg = get_default_config()
        summarizer = CodeSummarizer(cfg)
        manager = ModelManager(cfg)
        return summarizer, manager

    summarizer, model_mgr = _get_ai_objects()

    # ── Four interactive sections via horizontal radio ──
    section = st.radio(
        "Pick a tool",
        ["✍️ Paste & Summarize", "🔎 Name Pattern Lookup",
         "📐 Similarity Calculator", "📝 Prompt Preview"],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # ────────────────────────── Paste & Summarize ──────────────────────────
    if section == "✍️ Paste & Summarize":
        st.markdown("#### ✍️ Paste & Summarize")
        st.caption("Paste a Python function or class and get an instant natural-language summary.")

        _default_code = '''def calculate_discount(price, discount_percent):
    """Calculate the discounted price."""
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)'''

        code_input = st.text_area("Paste your code here", value=_default_code, height=220,
                                   key="ai_code_input")

        col_a, col_b = st.columns(2)
        with col_a:
            entity_type = st.selectbox("What is this?", ["Function", "Class"], key="ai_entity_type")
        with col_b:
            entity_name = st.text_input("Name (optional — auto-detected if blank)",
                                         key="ai_entity_name")

        if st.button("🚀 Summarize", use_container_width=True, key="ai_summarize_btn"):
            if not code_input.strip():
                st.warning("Please paste some code first.")
            else:
                with st.spinner("Analysing…"):
                    _time.sleep(0.3)  # tiny visual delay so the spinner is noticeable
                    # Try to auto-detect name from first line
                    auto_name = entity_name.strip()
                    if not auto_name:
                        import re as _re
                        m = _re.search(r'(?:def|class)\s+(\w+)', code_input)
                        auto_name = m.group(1) if m else "unknown"

                    if entity_type == "Function":
                        # Build a minimal func_data dict the summarizer expects
                        params = []
                        pm = __import__('re').search(r'def\s+\w+\s*\(([^)]*)\)', code_input)
                        if pm:
                            params = [p.strip().split(':')[0].split('=')[0].strip()
                                      for p in pm.group(1).split(',') if p.strip()]
                        # Detect docstring
                        doc = None
                        dm = __import__('re').search(r'"""(.*?)"""', code_input, __import__('re').DOTALL)
                        if dm:
                            doc = dm.group(1).strip()
                        func_data = {
                            'name': auto_name,
                            'parameters': params,
                            'returns': None,
                            'docstring': doc,
                            'calls': [],
                            'is_async': 'async ' in code_input[:30],
                        }
                        summary_text = summarizer.summarize_function(func_data, code_input)
                    else:
                        # Class mode
                        methods = __import__('re').findall(r'def\s+(\w+)\s*\(', code_input)
                        doc = None
                        dm = __import__('re').search(r'class\s+\w+.*?:\s*"""(.*?)"""',
                                                     code_input, __import__('re').DOTALL)
                        if dm:
                            doc = dm.group(1).strip()
                        class_data = {
                            'name': auto_name,
                            'bases': [],
                            'method_names': methods,
                            'docstring': doc,
                        }
                        summary_text = summarizer.summarize_class(class_data)

                st.success("Done!")
                st.markdown(f"""
                <div class="glass" style="padding:1.2rem;">
                    <h4 style="margin:0 0 .5rem;">📄 Summary</h4>
                    <p style="font-size:1.05rem;line-height:1.6;">{summary_text}</p>
                </div>
                """, unsafe_allow_html=True)

                # Also show the inferred purpose separately
                purpose = summarizer._infer_purpose_from_name(auto_name)
                if purpose:
                    st.info(f"🔎 Name pattern **'{auto_name}'** → *{purpose}*")
                else:
                    st.info(f"🔎 No built-in name pattern matched for **'{auto_name}'**.")

    # ────────────────────────── Name Pattern Lookup ──────────────────────────
    elif section == "🔎 Name Pattern Lookup":
        st.markdown("#### 🔎 Name Pattern Lookup")
        st.caption(
            "The AI engine uses 16 prefix/keyword patterns to infer what a function or class does. "
            "Type a name to see which pattern matches."
        )

        _pattern_table = {
            "get / fetch": "retrieves data",
            "set / update": "updates data",
            "create / make": "creates new data or objects",
            "delete / remove": "removes data",
            "validate / check": "validates data or conditions",
            "calculate / compute": "performs calculations",
            "parse / process": "processes data",
            "save / write": "saves or writes data",
            "load / read": "loads or reads data",
            "handle / handler": "handles events or requests",
            "manager": "manages resources or operations",
            "controller": "controls application logic",
            "helper / util": "provides utility functions",
        }

        test_name = st.text_input("Enter a function or class name", value="getUser",
                                    key="ai_name_input")

        if test_name.strip():
            result = summarizer._infer_purpose_from_name(test_name.strip())
            if result:
                st.markdown(f"""
                <div class="glass" style="padding:1rem;">
                    <span style="font-size:1.4rem;">✅</span>
                    <strong>{test_name}</strong> → <em>{result}</em>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="glass" style="padding:1rem;border-left:3px solid #f39c12;">
                    <span style="font-size:1.4rem;">⚠️</span>
                    No pattern matched for <strong>{test_name}</strong>.
                    Try prefixes like <code>get</code>, <code>create</code>, <code>validate</code>, etc.
                </div>
                """, unsafe_allow_html=True)

        st.markdown("##### All 16 patterns")
        if HAS_PANDAS:
            df_patterns = pd.DataFrame([
                {"Prefix / Keyword": k, "Inferred Purpose": v}
                for k, v in _pattern_table.items()
            ])
            st.dataframe(df_patterns, use_container_width=True, hide_index=True)
        else:
            for k, v in _pattern_table.items():
                st.write(f"**{k}** → {v}")

    # ────────────────────────── Similarity Calculator ──────────────────────────
    elif section == "📐 Similarity Calculator":
        st.markdown("#### 📐 Code Similarity Calculator")
        st.caption(
            "Compare two code snippets using Jaccard token similarity "
            "(or CodeBERT cosine similarity when the model is loaded)."
        )

        col1, col2 = st.columns(2)
        with col1:
            snippet_a = st.text_area("Snippet A", height=180, key="sim_a",
                                      value="def add(a, b):\n    return a + b")
        with col2:
            snippet_b = st.text_area("Snippet B", height=180, key="sim_b",
                                      value="def sum_values(x, y):\n    return x + y")

        if st.button("📐 Calculate Similarity", use_container_width=True, key="sim_btn"):
            if not snippet_a.strip() or not snippet_b.strip():
                st.warning("Please paste code in both boxes.")
            else:
                with st.spinner("Comparing…"):
                    _time.sleep(0.2)
                    score = model_mgr.calculate_similarity(snippet_a, snippet_b)

                pct = int(score * 100)
                # Colour gradient
                if pct >= 75:
                    bar_color = "#2ecc71"
                    label = "High"
                elif pct >= 40:
                    bar_color = "#f39c12"
                    label = "Moderate"
                else:
                    bar_color = "#e74c3c"
                    label = "Low"

                st.markdown(f"""
                <div class="glass" style="padding:1.2rem;text-align:center;">
                    <h2 style="margin:0;">{pct}%</h2>
                    <div style="background:#e0e0e0;border-radius:8px;height:18px;margin:.6rem 0;">
                        <div style="width:{pct}%;background:{bar_color};height:100%;
                                    border-radius:8px;transition:width .5s;"></div>
                    </div>
                    <span style="font-size:.95rem;color:{bar_color};font-weight:600;">{label} similarity</span>
                    <p style="opacity:.6;font-size:.8rem;margin-top:.4rem;">
                        Method: {'CodeBERT cosine' if model_mgr.model else 'Jaccard token'} similarity
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Show Jaccard detail
                tokens_a = set(snippet_a.split())
                tokens_b = set(snippet_b.split())
                shared = tokens_a & tokens_b
                if shared:
                    st.caption(f"Shared tokens ({len(shared)}): `{'`, `'.join(sorted(shared))}`")

    # ────────────────────────── Prompt Preview ──────────────────────────
    elif section == "📝 Prompt Preview":
        st.markdown("#### 📝 LLM Prompt Preview")
        st.caption(
            "Select one of the 10 built-in prompt templates and see the formatted prompt "
            "that would be sent to an LLM (GPT, Claude, etc.)."
        )

        template_names = [
            "Function Summary",
            "Class Summary",
            "File Summary",
            "Code Smell Explanation",
            "Refactoring Suggestion",
            "Dependency Analysis",
            "Code Quality Assessment",
            "Documentation Generation",
            "Bug Detection",
            "Test Generation",
        ]

        chosen = st.selectbox("Template", template_names, key="prompt_tmpl")

        # Sample data for each template
        sample_code = 'def calculate_discount(price, pct):\n    return price * (1 - pct / 100)'

        prompt_text = ""
        if chosen == "Function Summary":
            prompt_text = PromptTemplates.function_summary_prompt(
                sample_code, "calculate_discount", ["price", "pct"])
        elif chosen == "Class Summary":
            prompt_text = PromptTemplates.class_summary_prompt(
                "class OrderProcessor:\n    def process(self): ...",
                "OrderProcessor", ["process"])
        elif chosen == "File Summary":
            prompt_text = PromptTemplates.file_summary_prompt(
                sample_code, "pricing.py",
                ["calculate_discount"], [])
        elif chosen == "Code Smell Explanation":
            prompt_text = PromptTemplates.code_smell_explanation_prompt(
                "Long Function", sample_code, "pricing.py:1")
        elif chosen == "Refactoring Suggestion":
            prompt_text = PromptTemplates.refactoring_suggestion_prompt(sample_code, 15)
        elif chosen == "Dependency Analysis":
            prompt_text = PromptTemplates.dependency_analysis_prompt(
                ["os", "json", "pathlib"], ["app.py", "cli.py"])
        elif chosen == "Code Quality Assessment":
            prompt_text = PromptTemplates.code_quality_prompt({
                'complexity': 6.2, 'maintainability': 72.5,
                'loc': 340, 'functions': 18, 'classes': 3, 'smells': 4})
        elif chosen == "Documentation Generation":
            prompt_text = PromptTemplates.documentation_generation_prompt(sample_code, "")
        elif chosen == "Bug Detection":
            prompt_text = PromptTemplates.bug_detection_prompt(sample_code, "pricing module")
        elif chosen == "Test Generation":
            prompt_text = PromptTemplates.test_generation_prompt(sample_code, "calculate_discount")

        st.code(prompt_text, language="text")

        st.markdown(f"""
        <div class="glass" style="padding:.8rem;font-size:.85rem;">
            📏 <strong>Prompt length:</strong> {len(prompt_text)} chars &nbsp;|&nbsp;
            ~{len(prompt_text.split())} tokens (approx)
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────
def _generate_summary_text(results: dict) -> str:
    summary = results["summary"]
    metadata = results["metadata"]
    return f"""
CODEBASE ARCHAEOLOGIST — ANALYSIS SUMMARY
{'='*60}

Source:    {metadata.get('source', 'N/A')}
Analysed: {metadata.get('analyzed_at', 'N/A')}
Duration: {metadata.get('analysis_time_seconds', 0)}s

STATISTICS
{'-'*60}
Total Files:     {metadata.get('total_files', 0)}
Total Functions: {summary.get('total_functions', 0)}
Total Classes:   {summary.get('total_classes', 0)}
Lines of Code:   {summary.get('total_lines_of_code', 0):,}

QUALITY METRICS
{'-'*60}
Avg Complexity:      {summary.get('average_complexity', 0):.2f}
Maintainability:     {summary.get('average_maintainability', 0):.2f}
Code Smells:         {summary.get('total_code_smells', 0)}

{'='*60}
Generated by Codebase Archaeologist v2.0
"""


if __name__ == "__main__":
    main()