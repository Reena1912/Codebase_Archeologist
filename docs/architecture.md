# CODEBASE ARCHAEOLOGIST — Project Report

## AI-Powered Legacy Code Analysis & Documentation System

---

## TABLE OF CONTENTS

1. [Introduction](#1-introduction)
2. [Rationale Behind the Study](#2-rationale-behind-the-study)
3. [Objectives](#3-objectives)
4. [System Architecture](#4-system-architecture)
5. [Module-Level Design](#5-module-level-design)
6. [Technology Stack](#6-technology-stack)
7. [Implementation Details](#7-implementation-details)
8. [AI-Powered Documentation Generation (Deep Dive)](#8-ai-powered-documentation-generation-deep-dive)
   - [8.7 Interactive AI Lab](#87-interactive-ai-lab-live-demo-feature)
   - [8.8 AI Decision-Tree Flowchart](#88-ai-decision-tree-how-summaries-are-generated)
   - [8.9 Before & After Real-World Examples](#89-before--after-real-world-examples)
   - [8.10 Similarity Engine](#810-similarity-engine-how-code-comparison-works)
   - [8.11 Prompt Templates Quick Reference](#811-all-10-prompt-templates--quick-reference-card)
   - [8.12 AI Configuration & Tuning Guide](#812-ai-engine-configuration--tuning-guide)
9. [Data Flow & Processing Pipeline](#9-data-flow--processing-pipeline)
10. [Output Artifacts](#10-output-artifacts)
11. [Testing Strategy](#11-testing-strategy)
12. [Screenshots / Sample Outputs](#12-screenshots--sample-outputs)
13. [Total Workflow Process (Step-by-Step)](#13-total-workflow-process-step-by-step)
14. [Limitations & Future Scope](#14-limitations--future-scope)
15. [Conclusion](#15-conclusion)
16. [References](#16-references)

---

## 1. INTRODUCTION

Software maintenance consumes approximately 60–80% of the total software development lifecycle cost. One of the most significant challenges in this phase is understanding **"legacy code"**—older codebases written by developers who may no longer be with the organization. In the modern software industry, documentation is often outdated, missing, or disconnected from the actual code logic ("Code Rot"). New developers spend weeks or months purely on "onboarding"—reading thousands of lines of code to build a mental model of the system.

The **"Codebase Archaeologist"** project addresses this critical inefficiency. It is an AI-powered system designed to **"excavate"** an unfamiliar codebase. By combining **Static Analysis (Abstract Syntax Trees)** with **Large Language Models (LLMs)** and **Knowledge Graphs**, the system automatically generates human-readable explanations, visualizes complex dependencies, and produces up-to-date documentation.

This tool moves beyond simple code commenting, acting as an **intelligent agent** that explains _how_ the system works and _why_ specific logic exists.

---

## 2. RATIONALE BEHIND THE STUDY

### 2.1 Mitigating "Knowledge Loss"

When senior developers leave an organization, their tacit knowledge of the system architecture leaves with them. This project automates the preservation of this knowledge by extracting logic directly from the source code.

### 2.2 Combating Documentation Drift

Comments and external documentation often become outdated as code evolves. By analyzing the current syntax tree and logic, this system generates documentation that is always synchronized with the code's actual behavior.

### 2.3 Reducing Cognitive Load

Reading raw code is mentally taxing. This system translates complex algorithmic logic into natural language summaries (e.g., _"This function validates the user token and updates the session database"_), allowing developers to skim-read codebases.

### 2.4 Visualizing Invisible Dependencies

Spaghetti code (tangled dependencies) is a primary cause of bugs during refactoring. By generating Knowledge Graphs, the system visualizes how files and modules interact, revealing risks that text editors cannot show.

### 2.5 Standardization of Code Audits

Manual code reviews vary in quality between reviewers. An AI-driven approach ensures a standardized, objective report on code complexity, structure, and quality for every project analyzed.

---

## 3. OBJECTIVES

1. **To implement an AI-Based Explanation Engine** using Transformer models (e.g., CodeT5 or CodeBERT) to generate natural language summaries for complex functions and classes.

2. **To construct a Dependency Knowledge Graph** that visually maps relationships between files, identifying critical paths and "God Classes" within the system.

3. **To automate the generation of a Comprehensive Audit Report** (Markdown/HTML) that combines metrics, text explanations, and visual graphs into a single "User Manual" for the legacy codebase.

---

## 4. SYSTEM ARCHITECTURE

### 4.1 High-Level Architecture

The system follows a **modular pipeline architecture** with seven distinct stages:

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                            │
│         ┌──────────────┐          ┌──────────────────┐             │
│         │   CLI (cli.py)│          │ Streamlit Web App │            │
│         └──────┬───────┘          └────────┬─────────┘             │
│                └──────────┬───────────────┘                        │
│                           ▼                                        │
│              ┌────────────────────────┐                             │
│              │  Main Orchestrator     │                             │
│              │      (main.py)         │                             │
│              └───────────┬────────────┘                             │
│                          ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   PROCESSING PIPELINE                        │   │
│  │                                                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │Ingestion │→ │Analysis  │→ │Extraction│→ │AI Engine │    │   │
│  │  │          │  │          │  │          │  │          │    │   │
│  │  │• Loader  │  │• AST     │  │• Deps    │  │• Summary │    │   │
│  │  │• Filter  │  │• Complex │  │• Smells  │  │• Models  │    │   │
│  │  │• GitHub  │  │• Metrics │  │• Calls   │  │• Prompts │    │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │   │
│  │                                                              │   │
│  └──────────────────────┬──────────────────────────────────────┘   │
│                          ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    OUTPUT LAYER                               │   │
│  │  ┌───────────────┐  ┌───────────────┐  ┌────────────────┐   │   │
│  │  │ Visualization │  │   Reporting   │  │  JSON Export    │   │   │
│  │  │ • Charts      │  │ • HTML        │  │  (Raw Data)     │   │   │
│  │  │ • Graphs      │  │ • Markdown    │  │                 │   │   │
│  │  └───────────────┘  └───────────────┘  └────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Design Patterns Used

| Pattern                   | Where Used                                    | Purpose                                     |
| ------------------------- | --------------------------------------------- | ------------------------------------------- |
| **Orchestrator / Facade** | `main.py` — `CodebaseArchaeologist`           | Single entry point coordinating all modules |
| **Strategy**              | `CodeSummarizer` — rule-based vs. model-based | Allows swapping summarization strategies    |
| **Pipeline**              | Analysis flow in `analyze_local()`            | Sequential processing stages                |
| **Template Method**       | `MarkdownGenerator`, `HTMLGenerator`          | Common report structure, different formats  |
| **Singleton**             | `logger` (via `setup_logger`)                 | Global logging instance                     |
| **Factory**               | `ModelManager.load_model()`                   | Model instantiation based on config         |

---

## 5. MODULE-LEVEL DESIGN

### 5.1 Ingestion Layer (`src/ingestion/`)

| File             | Class        | Responsibility                                                                                                                                                                                                       |
| ---------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `code_loader.py` | `CodeLoader` | Loads codebase from local directories or GitHub repos (shallow clone via subprocess). Normalizes GitHub URLs (handles HTTPS, SSH, with/without `.git`). Robust Windows-compatible cleanup of `.git` read-only files. |
| `file_filter.py` | `FileFilter` | Validates files against supported languages (Python, JS, Java, C++, Go, Rust, Ruby, PHP), excluded directories/extensions, and file size limits. Maps file extensions → language names.                              |

**Key Methods:**

- `CodeLoader.load_from_local(path)` → Recursively walks directory, reads non-binary files, returns metadata + content.
- `CodeLoader.load_from_github(url)` → Clones repo (depth=1), then calls `load_from_local`.
- `CodeLoader._ensure_clean_dir(path)` → Three-tier fallback for temp directory conflicts (force remove → PID alt → UUID alt).

### 5.2 Analysis Layer (`src/analysis/`)

| File                     | Class                | Responsibility                                                                                                                                                                                                                 |
| ------------------------ | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ast_parser.py`          | `ASTParser`          | Uses Python's built-in `ast` module to parse source files. Extracts functions (name, params, docstring, calls, decorators, line numbers), classes (bases, methods, docstring), imports, and global variables.                  |
| `complexity_analyzer.py` | `ComplexityAnalyzer` | Leverages the **Radon** library for cyclomatic complexity (`cc_visit`), maintainability index (`mi_visit`), Halstead metrics (`h_visit`), and raw metrics (LOC, SLOC, comments, blanks). Configurable thresholds for flagging. |
| `metrics_calculator.py`  | `MetricsCalculator`  | Computes file-level and repository-level metrics: LOC/SLOC/comments/blanks, function/class counts, average lengths, documentation coverage (% of entities with docstrings).                                                    |

**Key Algorithms:**

- **Cyclomatic Complexity:** Counts linearly independent paths through the program's control flow graph. Formula: $M = E - N + 2P$ where $E$ = edges, $N$ = nodes, $P$ = connected components.
- **Maintainability Index:** Composite metric combining Halstead Volume, Cyclomatic Complexity, and LOC:

$$MI = 171 - 5.2 \ln(V) - 0.23 \cdot G - 16.2 \ln(LOC)$$

where $V$ = Halstead Volume, $G$ = Cyclomatic Complexity.

### 5.3 Extraction Layer (`src/extraction/`)

| File                      | Class                 | Responsibility                                                                                                                                                                                                                 |
| ------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `dependency_extractor.py` | `DependencyExtractor` | Uses **NetworkX** `DiGraph` to build a dependency graph from imports. Analyzes: most depended-upon files (in-degree), most dependent files (out-degree), circular dependencies (`nx.simple_cycles`), isolated files.           |
| `code_smell_detector.py`  | `CodeSmellDetector`   | Detects 7 code smell types (see list below). Also performs cross-file duplicate detection via function signature comparison.                                                                                                   |
| `call_graph_builder.py`   | `CallGraphBuilder`    | Two-pass approach: (1) collects all function definitions with unique IDs like `filepath::Class.method`, (2) resolves call edges locally and globally. Analyzes recursive functions, dead-end functions, most-called functions. |

**Code Smells Detected:**

| #   | Smell                | Detection Rule                                                  |
| --- | -------------------- | --------------------------------------------------------------- |
| 1   | Long Function        | Function body exceeds configurable line threshold (default: 50) |
| 2   | Large Class          | Class body exceeds configurable line threshold (default: 300)   |
| 3   | Missing Docstring    | Function/class has no docstring                                 |
| 4   | Too Many Parameters  | More than 5 parameters (excluding `self`/`cls`)                 |
| 5   | Dead Code            | Functions defined but never called within the codebase          |
| 6   | Magic Numbers        | Numeric literals in logic detected via regex                    |
| 7   | Non-Constant Globals | Global variables that are not uppercase constants               |

### 5.4 AI Engine (`src/ai_engine/`)

| File                  | Class             | Responsibility                                                                                                                                                                                                                                     |
| --------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `code_summarizer.py`  | `CodeSummarizer`  | Generates natural language summaries for functions, classes, and files. Currently **rule-based**: uses docstrings when available; otherwise infers purpose from naming patterns (e.g., `get*` → "retrieves data", `validate*` → "validates data"). |
| `model_manager.py`    | `ModelManager`    | Placeholder for **Hugging Face Transformers** integration (CodeBERT / `microsoft/codebert-base`). Provides: `load_model()`, `encode_code()` (embeddings), `generate_summary()`, `calculate_similarity()` (cosine with Jaccard fallback).           |
| `prompt_templates.py` | `PromptTemplates` | Static methods generating structured LLM prompts for: function/class/file summarization, code smell explanation, refactoring suggestions, dependency analysis, code quality assessment, documentation generation, bug detection, test generation.  |

**AI Integration Path:**

```
Current: Rule-based summarization (pattern matching on function names + docstrings)
     ↓
Phase 2: CodeBERT embeddings for semantic code similarity
     ↓
Phase 3: Full LLM-powered summarization via Ollama / OpenAI API
```

### 5.5 Visualization Layer (`src/visualization/`)

| File                 | Class            | Responsibility                                                                                                                                                                                                                                         |
| -------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `chart_creator.py`   | `ChartCreator`   | Uses **Plotly** (with Matplotlib fallback). Creates: complexity heatmap (scatter), metrics dashboard (subplots with bar/gauge/pie), dependency network (circular layout), treemap (file sizes colored by complexity), and timeline chart.              |
| `graph_generator.py` | `GraphGenerator` | Uses **Matplotlib** + **NetworkX**. Generates: dependency graph (spring layout, node sizes by degree, colored by in-degree), complexity bar chart (horizontal bars colored green/yellow/red), smell distribution pie chart, metrics summary (4-panel). |

### 5.6 Reporting Layer (`src/reporting/`)

| File                    | Class               | Responsibility                                                                                                                                                                                                                                      |
| ----------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `html_generator.py`     | `HTMLGenerator`     | Uses **Jinja2** templating engine. Renders a full interactive HTML report from `template.html` with quality grade (A–D), file details sorted by complexity, smell counts, dependency info. Also has `generate_mini_report()` for compact summaries. |
| `markdown_generator.py` | `MarkdownGenerator` | Generates comprehensive Markdown reports with: executive summary, quality assessment (✅/⚠️/❌ indicators), per-file analysis (top 10 by complexity), dependency analysis, aggregated code smells, and actionable recommendations.                  |
| `template.html`         | —                   | Jinja2 HTML template (~567 lines) with responsive CSS, gradient headers, metric cards, and styled tables.                                                                                                                                           |

### 5.7 Web Interface (`web/`)

| File               | Description                                                                                                                                                                                                                                                                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `streamlit_app.py` | Full Streamlit dashboard (~1010 lines). Features: sidebar config (local/GitHub input, complexity/function length sliders), **6 tabs** (Overview, Visualizations, Files, Dependencies, Code Smells, Export). Plotly interactive charts. All in-memory (no disk writes during analysis). Export supports JSON, text summary, and HTML downloads. |

### 5.8 Utilities (`src/utils/`)

| File         | Description                                                                                             |
| ------------ | ------------------------------------------------------------------------------------------------------- |
| `logger.py`  | Configurable logging with `colorlog` for colored terminal output, file rotation.                        |
| `helpers.py` | Utility functions: `load_config()` (YAML), `create_output_dir()`, `is_binary_file()`, `format_bytes()`. |

---

## 6. TECHNOLOGY STACK

### 6.1 Core Technologies

| Category            | Technology                       | Purpose                                     |
| ------------------- | -------------------------------- | ------------------------------------------- |
| **Language**        | Python 3.8+                      | Primary development language                |
| **AST Parsing**     | Python `ast` module              | Built-in abstract syntax tree parsing       |
| **Complexity**      | Radon 5.1+                       | Cyclomatic complexity, MI, Halstead metrics |
| **Linting**         | Pylint 2.15+                     | Static code analysis                        |
| **Graph Analysis**  | NetworkX 3.0+                    | Dependency graph construction & analysis    |
| **AI/ML**           | Transformers 4.30+, PyTorch 2.0+ | CodeBERT model for code embeddings          |
| **Visualization**   | Plotly 5.14+, Matplotlib 3.7+    | Interactive & static charts                 |
| **Graph Viz**       | Graphviz 0.20+                   | DOT-format graph rendering                  |
| **Web UI**          | Streamlit 1.22+                  | Interactive web dashboard                   |
| **Web Server**      | Flask 2.3+                       | Alternative web backend                     |
| **Templating**      | Jinja2 3.1+                      | HTML report generation                      |
| **Git Integration** | GitPython 3.1+                   | GitHub repository cloning                   |
| **Config**          | PyYAML 6.0+                      | YAML configuration parsing                  |
| **Logging**         | colorlog 6.7+                    | Colored terminal logging                    |
| **CLI Progress**    | tqdm 4.65+                       | Progress bars                               |
| **Testing**         | pytest 7.3+, pytest-cov 4.1+     | Unit testing & coverage                     |
| **HTTP**            | requests 2.31+                   | HTTP requests for API calls                 |
| **Documents**       | python-docx 0.8+                 | Word document generation                    |

### 6.2 Development & Packaging

```
setuptools       — Package building & distribution
pip              — Dependency management
venv             — Virtual environment isolation
Git              — Version control
```

---

## 7. IMPLEMENTATION DETAILS

### 7.1 Project Structure

```
codebase-archaeologist/
├── cli.py                          # Command-line interface (283 lines)
├── main.py                         # Main orchestrator (283 lines)
├── config.yaml                     # Configuration file (121 lines)
├── requirements.txt                # 20+ dependencies
├── setup.py                        # Package setup with entry points
├── src/
│   ├── __init__.py
│   ├── ingestion/                  # Stage 1: Code Loading
│   │   ├── code_loader.py          # Local & GitHub loading (298 lines)
│   │   └── file_filter.py          # Language/extension filtering (170 lines)
│   ├── analysis/                   # Stage 2: Parsing & Metrics
│   │   ├── ast_parser.py           # AST extraction (193 lines)
│   │   ├── complexity_analyzer.py  # Radon-based analysis (158 lines)
│   │   └── metrics_calculator.py   # Aggregated metrics (296 lines)
│   ├── extraction/                 # Stage 3: Dependency & Smell Detection
│   │   ├── dependency_extractor.py # Import graph (149 lines)
│   │   ├── code_smell_detector.py  # 7 smell types (192 lines)
│   │   └── call_graph_builder.py   # Function call graph (238 lines)
│   ├── ai_engine/                  # Stage 4: AI Summarization
│   │   ├── code_summarizer.py      # Rule-based summaries (202 lines)
│   │   ├── model_manager.py        # CodeBERT integration (195 lines)
│   │   └── prompt_templates.py     # LLM prompt templates (254 lines)
│   ├── visualization/              # Stage 5: Visual Outputs
│   │   ├── chart_creator.py        # Plotly charts (543 lines)
│   │   └── graph_generator.py      # Matplotlib graphs (266 lines)
│   ├── reporting/                  # Stage 6: Reports
│   │   ├── html_generator.py       # Jinja2 HTML reports (218 lines)
│   │   ├── markdown_generator.py   # Markdown reports (305 lines)
│   │   └── template.html           # HTML template (567 lines)
│   └── utils/                      # Shared Utilities
│       ├── helpers.py              # Config, I/O helpers
│       └── logger.py               # Colored logging
├── web/
│   └── streamlit_app.py            # Web dashboard (1010 lines)
├── tests/
│   ├── test_parser.py              # AST parser tests (116 lines)
│   ├── test_analyzer.py            # Analyzer & integration tests (237 lines)
│   └── sample_repo/                # Sample code for tests
│       ├── calculator.py
│       └── utils.py
├── docs/
│   ├── architecture.md             # This document
│   └── viva_questions.md           # Viva preparation guide
└── outputs/                        # Generated reports (gitignored)
    ├── reports/
    ├── graphs/
    └── visualizations/
```

**Total Lines of Source Code:** ~5,200+ lines across 20 Python modules.

### 7.2 Configuration System

The system uses a centralized `config.yaml` with the following sections:

```yaml
analysis:
  supported_languages: [python, javascript, java]
  exclude_dirs: [__pycache__, .git, node_modules, venv, ...]
  exclude_extensions: [.pyc, .pyo, .dll, .exe, ...]
  max_file_size_mb: 10

ai:
  model_name: microsoft/codebert-base
  use_local_model: false
  max_token_length: 512

quality: # Configurable thresholds
  max_complexity: 10 # Cyclomatic complexity flag
  max_function_length: 50 # Lines per function
  max_class_length: 300 # Lines per class
  max_parameters: 5 # Parameters per function
  duplicate_threshold: 0.8 # Similarity threshold
  min_maintainability: 10 # Minimum MI score

output:
  base_dir: ./outputs
  report_format: both # markdown, html, or both
  generate_visualizations: true
  generate_json: true

github:
  temp_dir: ./temp_repo
  clone_depth: 1
  cleanup_after_analysis: true
```

### 7.3 CLI Interface

```
Usage: python cli.py [OPTIONS] PATH

Positional:
  PATH                    Local directory path or GitHub URL

Options:
  -c, --config FILE       Configuration file (default: config.yaml)
  -o, --output DIR        Output directory
  --no-visualize          Skip graph generation
  --no-report             Skip report generation
  --format {json,md,html,all}  Output format (default: all)
  --open-html             Auto-open HTML report in browser
  -q, --quiet             Errors only
  -v, --verbose           Debug-level output
  --version               Show version
```

**Example Commands:**

```bash
# Analyze local project
python cli.py /path/to/project

# Analyze GitHub repository
python cli.py https://github.com/user/repo

# Custom output with HTML auto-open
python cli.py /path/to/project -o ./results --open-html

# JSON-only quiet mode
python cli.py /path/to/project --format json --quiet
```

### 7.4 Streamlit Web Dashboard

The web interface provides an interactive 6-tab dashboard:

| Tab                | Contents                                                                                                       |
| ------------------ | -------------------------------------------------------------------------------------------------------------- |
| **Overview**       | Metric cards (files, functions, classes, LOC), quality grade (A–D), summary statistics                         |
| **Visualizations** | Interactive Plotly charts: complexity scatter, histogram, bar charts, gauges, dependency network, file treemap |
| **Files**          | Detailed per-file breakdown with complexity, MI, LOC, smell counts                                             |
| **Dependencies**   | Dependency graph, most-depended files, circular dependency warnings, isolated files                            |
| **Code Smells**    | Categorized smell listing, distribution charts, severity indicators                                            |
| **Export**         | Download buttons for JSON, text summary, HTML mini-report                                                      |

**Launch:** `streamlit run web/streamlit_app.py`

---

## 8. AI-POWERED DOCUMENTATION GENERATION (DEEP DIVE)

This section provides an in-depth explanation of how the AI Engine automatically generates human-readable documentation for any codebase.

### 8.1 Architecture of the AI Engine

The AI Engine resides in `src/ai_engine/` and consists of three tightly integrated modules:

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI ENGINE LAYER                            │
│                                                                 │
│  ┌──────────────────┐                                           │
│  │  CodeSummarizer   │ ◄── Main entry point                    │
│  │  (267 lines)      │     called by main.py for each file     │
│  └────────┬─────────┘                                           │
│           │ uses                                                │
│           ▼                                                     │
│  ┌──────────────────┐    ┌────────────────────┐                 │
│  │  ModelManager     │    │  PromptTemplates   │                │
│  │  (270 lines)      │    │  (254 lines)       │                │
│  │                   │    │                    │                │
│  │  • load_model()   │    │  • function_prompt │                │
│  │  • encode_code()  │    │  • class_prompt    │                │
│  │  • generate_      │    │  • file_prompt     │                │
│  │    summary()      │    │  • smell_prompt    │                │
│  │  • calculate_     │    │  • refactor_prompt │                │
│  │    similarity()   │    │  • 5 more prompts  │                │
│  └──────────────────┘    └────────────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 CodeSummarizer — Rule-Based Explanation Engine

The `CodeSummarizer` class (`src/ai_engine/code_summarizer.py`, 267 lines) is the primary documentation generator. It produces natural language summaries at three levels of granularity:

#### 8.2.1 Function-Level Summarization

**Method:** `summarize_function(func_data, content)`

**Algorithm:**

1. **Check for existing docstring** — If the function already has a docstring, use it directly.
2. **Detect async functions** — Prepend "This asynchronous function" if applicable.
3. **Infer purpose from naming conventions** — Pattern-match the function name against 15+ common prefixes:

| Prefix Pattern           | Inferred Purpose                  |
| ------------------------ | --------------------------------- |
| `get*`, `fetch*`         | "retrieves data"                  |
| `set*`, `update*`        | "updates data"                    |
| `create*`, `make*`       | "creates new data or objects"     |
| `delete*`, `remove*`     | "removes data"                    |
| `validate*`, `check*`    | "validates data or conditions"    |
| `calculate*`, `compute*` | "performs calculations"           |
| `parse*`, `process*`     | "processes data"                  |
| `save*`, `write*`        | "saves or writes data"            |
| `load*`, `read*`         | "loads or reads data"             |
| `*handler*`, `*handle*`  | "handles events or requests"      |
| `*manager*`              | "manages resources or operations" |
| `*controller*`           | "controls application logic"      |
| `*helper*`, `*util*`     | "provides utility functions"      |

4. **Describe parameters** — Count and list parameter names (excluding `self`/`cls`).
5. **Describe return type** — If return annotation exists, include it.
6. **List function calls** — Show up to 5 called functions; summarize count if more.

**Example Input:**

```python
def validate_user_token(token: str, session_db: dict) -> bool:
    result = check_expiry(token)
    update_session(session_db, token)
    return result
```

**Example Output:**

> "This function validates data or conditions. takes 2 parameter(s): token, session_db and returns bool. It calls: check_expiry, update_session."

#### 8.2.2 Class-Level Summarization

**Method:** `summarize_class(class_data)`

**Algorithm:**

1. Use existing docstring if available.
2. Describe inheritance hierarchy (base classes).
3. Count and list public methods (excluding `_private` methods).
4. Infer class purpose from naming conventions.

**Example Output:**

> "Class 'UserAuthManager' inherits from BaseManager and implements 8 methods including: authenticate, refresh_token, logout, validate_session, get_user. manages resources or operations."

#### 8.2.3 File-Level Summarization

**Method:** `summarize_file(parsed_data)`

**Algorithm:**

1. Count and name all classes defined in the file.
2. Count standalone functions (not class methods).
3. Count imported modules.
4. Infer file purpose from filename patterns:

| Filename Pattern         | Inferred Purpose                            |
| ------------------------ | ------------------------------------------- |
| `*test*`                 | "This appears to be a test file"            |
| `*config*`, `*settings*` | "This file contains configuration settings" |
| `*util*`, `*helper*`     | "This file provides utility functions"      |
| `*model*`                | "This file defines data models"             |
| `*view*`                 | "This file handles view logic"              |
| `*controller*`           | "This file contains controller logic"       |
| `*main*`                 | "This is the main entry point"              |

#### 8.2.4 Complete Documentation Generation

**Method:** `generate_documentation(parsed_data)` — the main entry point called by `main.py` for each file.

**Output Structure:**

```json
{
  "file_summary": "File 'auth_manager.py' defines 2 class(es): AuthManager, TokenValidator and 3 function(s). It imports 5 module(s). This file manages resources or operations.",
  "classes": [
    {
      "name": "AuthManager",
      "summary": "Class 'AuthManager': Manages user authentication and session lifecycle.",
      "methods": ["authenticate", "logout", "refresh_token"]
    }
  ],
  "functions": [
    {
      "name": "create_default_config",
      "summary": "This function creates new data or objects. takes 1 parameter(s): env.",
      "parameters": ["env"],
      "returns": "dict"
    }
  ]
}
```

### 8.3 ModelManager — CodeBERT Integration (Scaffolded)

The `ModelManager` class (`src/ai_engine/model_manager.py`, 270 lines) provides the infrastructure for **Hugging Face Transformers** model integration. While currently a scaffold, it is fully structured for production use.

#### 8.3.1 Model Loading Pipeline

```python
# Configuration in config.yaml
ai:
  model_name: microsoft/codebert-base
  use_local_model: false          # Set to true to enable
  max_token_length: 512
```

**When `use_local_model: true`:**

1. **Load tokenizer** — `AutoTokenizer.from_pretrained('microsoft/codebert-base')`
2. **Load model** — `AutoModel.from_pretrained('microsoft/codebert-base')`
3. **GPU detection** — Automatically moves model to CUDA if available
4. **Evaluation mode** — Sets `model.eval()` for inference

#### 8.3.2 Code Embedding Generation

**Method:** `encode_code(code)` → Tensor embeddings

```
Source Code → Tokenize (max 512 tokens) → Model Forward Pass → Mean Pooling → Embedding Vector
```

The embeddings can be used for:

- **Semantic code search** — Find functions with similar logic
- **Duplicate detection** — Compare code similarity beyond text matching
- **Clustering** — Group related functions/files

#### 8.3.3 Similarity Calculation

**Method:** `calculate_similarity(code1, code2)` → float (0.0–1.0)

- **With model loaded:** Uses cosine similarity on CodeBERT embeddings
- **Without model (fallback):** Uses Jaccard similarity on tokenized text:

$$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$

where $A$ and $B$ are the sets of tokens from each code snippet.

#### 8.3.4 About CodeBERT

**CodeBERT** (`microsoft/codebert-base`) is a bimodal pre-trained model for programming languages and natural language. Key properties:

| Property               | Value                                                           |
| ---------------------- | --------------------------------------------------------------- |
| **Architecture**       | RoBERTa (Transformer encoder, 12 layers)                        |
| **Parameters**         | 125M                                                            |
| **Pre-training Data**  | 6.4M bimodal (code + NL) data points from CodeSearchNet         |
| **Languages**          | Python, Java, JavaScript, PHP, Ruby, Go                         |
| **Pre-training Tasks** | Masked Language Modeling (MLM) + Replaced Token Detection (RTD) |
| **Output**             | 768-dimensional embedding vectors                               |

### 8.4 PromptTemplates — LLM Prompt Engineering

The `PromptTemplates` class (`src/ai_engine/prompt_templates.py`, 254 lines) provides **10 structured prompt templates** for when the system connects to an LLM (Ollama, OpenAI, etc.).

| #   | Template Method                     | Purpose                                       | When Used                   |
| --- | ----------------------------------- | --------------------------------------------- | --------------------------- |
| 1   | `function_summary_prompt()`         | Explain what a function does in plain English | Per-function documentation  |
| 2   | `class_summary_prompt()`            | Explain a class's role and responsibilities   | Per-class documentation     |
| 3   | `file_summary_prompt()`             | Summarize an entire file's purpose            | Per-file documentation      |
| 4   | `code_smell_explanation_prompt()`   | Explain why a detected smell is problematic   | Code smell reports          |
| 5   | `refactoring_suggestion_prompt()`   | Suggest how to refactor problematic code      | Improvement recommendations |
| 6   | `dependency_analysis_prompt()`      | Explain dependency relationships              | Dependency reports          |
| 7   | `code_quality_assessment_prompt()`  | Assess overall code quality                   | Quality dashboards          |
| 8   | `documentation_generation_prompt()` | Generate docstrings for undocumented code     | Auto-documentation          |
| 9   | `bug_detection_prompt()`            | Identify potential bugs in code               | Bug reports                 |
| 10  | `test_generation_prompt()`          | Generate unit test suggestions                | Test scaffolding            |

**Example Prompt (Function Summary):**

````
You are an expert code analyst. Analyze the following Python function
and provide a clear, concise natural language summary.

Function Name: validate_user_token
Parameters: token (str), session_db (dict)
Return Type: bool

Source Code:
```python
def validate_user_token(token, session_db):
    if token not in session_db:
        return False
    if session_db[token]['expired']:
        del session_db[token]
        return False
    return True
````

Provide:

1. A one-sentence summary of what this function does
2. The business logic it implements
3. Any potential issues or improvements

```

### 8.5 AI Integration Roadmap

The AI Engine is designed in three progressive phases:

```

╔══════════════════════════════════════════════════════════════════╗
║ PHASE 1 (CURRENT) — Rule-Based Summarization ║
║ ├─ Pattern matching on function/class/file names ║
║ ├─ Docstring extraction and reuse ║
║ ├─ Parameter/return type description ║
║ └─ Status: ✅ FULLY IMPLEMENTED ║
╠══════════════════════════════════════════════════════════════════╣
║ PHASE 2 — CodeBERT Embeddings ║
║ ├─ Semantic code similarity (beyond text matching) ║
║ ├─ Intelligent duplicate detection ║
║ ├─ Code clustering by functionality ║
║ └─ Status: 🔧 SCAFFOLDED (ModelManager ready) ║
╠══════════════════════════════════════════════════════════════════╣
║ PHASE 3 — Full LLM Integration ║
║ ├─ Natural language summaries via Ollama / OpenAI ║
║ ├─ 10 prompt templates ready (PromptTemplates class) ║
║ ├─ Bug detection, refactoring suggestions, test generation ║
║ └─ Status: 📋 TEMPLATES READY, awaiting API integration ║
╚══════════════════════════════════════════════════════════════════╝

````

### 8.6 How AI Documentation Fits in the Pipeline

In the main orchestrator (`main.py`), AI documentation is generated during Step 4 of file analysis:

```python
def _analyze_file(self, file_data):
    # Step 1: Parse AST
    parsed = self.parser.parse_file(filepath, content)

    # Step 2: Analyze complexity
    complexity = self.complexity_analyzer.analyze_file(filepath, content)

    # Step 3: Detect code smells
    smells = self.smell_detector.detect_smells(parsed, content)

    # Step 4: ★ Generate AI summaries ★
    documentation = self.summarizer.generate_documentation(parsed)
    #             └── calls summarize_file()
    #                 calls summarize_class() for each class
    #                 calls summarize_function() for each function

    return { ...parsed, 'documentation': documentation }
````

The generated documentation is then:

- Included in `analysis_results.json` (raw JSON export)
- Rendered in the **Markdown report** under each file's analysis section
- Displayed in the **HTML report** within file detail cards
- Shown in the **Streamlit dashboard** Files tab

### 8.7 Interactive AI Lab (Live Demo Feature)

The Streamlit dashboard includes a dedicated **� AI Lab** tab where users can interact with the AI engine in real-time without running a full analysis.

#### What Users Can Do

| Feature                   | Description                                                                                  | How It Works                                                  |
| ------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Paste & Summarize**     | Paste any Python function/class and get an instant NL summary                                | Calls `CodeSummarizer.summarize_function()` live              |
| **Compare Summaries**     | See rule-based vs. (future) LLM summary side by side                                         | Split-pane comparison view                                    |
| **Explore Name Patterns** | Type a function name and see what purpose the AI infers                                      | Interactive lookup against the 16-pattern table               |
| **Similarity Calculator** | Paste two code snippets and get a similarity score                                           | Uses `ModelManager.calculate_similarity()` (Jaccard fallback) |
| **Prompt Preview**        | Select any of the 10 prompt templates, fill in sample code, and preview the generated prompt | Read-only output from `PromptTemplates` methods               |

#### Playground Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   � AI LAB TAB                                 │
│                                                                 │
│  ┌─────────────────┐   ┌─────────────────────────────────────┐  │
│  │  Mode Selector   │   │                                     │  │
│  │  ○ Summarize     │   │          LIVE OUTPUT PANEL          │  │
│  │  ○ Compare       │   │                                     │  │
│  │  ○ Name Lookup   │   │  • NL Summary                      │  │
│  │  ○ Similarity    │   │  • Detected patterns                │  │
│  │  ○ Prompt Preview│   │  • Similarity score + breakdown     │  │
│  └─────────────────┘   │  • Formatted prompt text             │  │
│                         │                                     │  │
│  ┌─────────────────┐   │  Visual indicators:                  │  │
│  │  Code Input      │   │  🟢 High confidence inference       │  │
│  │  (text_area)     │   │  🟡 Partial match                   │  │
│  │                  │   │  🔴 No pattern match (generic)      │  │
│  └─────────────────┘   └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

#### Example: Live Summarization

**User pastes:**

```python
async def fetch_user_profile(user_id: str, include_avatar: bool = False) -> dict:
    response = await api_client.get(f"/users/{user_id}")
    profile = response.json()
    if include_avatar:
        avatar = await fetch_avatar(user_id)
        profile['avatar'] = avatar
    return profile
```

**Playground instantly shows:**

| Field             | Output                                                                                                                                                              |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Summary**       | "This asynchronous function retrieves data. takes 2 parameter(s): user_id, include_avatar and returns dict. It calls: api_client.get, response.json, fetch_avatar." |
| **Pattern Match** | 🟢 `fetch_*` → "retrieves data" (high confidence)                                                                                                                   |
| **Parameters**    | `user_id` (str), `include_avatar` (bool, default: False)                                                                                                            |
| **Async**         | ✅ Detected                                                                                                                                                         |
| **Calls**         | `api_client.get`, `response.json`, `fetch_avatar`                                                                                                                   |

### 8.8 AI Decision-Tree: How Summaries Are Generated

The summarization engine follows a deterministic decision tree. This flowchart shows exactly how every summary is produced:

```
                        ┌──────────────────────┐
                        │  INPUT: Function AST  │
                        └──────────┬───────────┘
                                   ▼
                        ┌──────────────────────┐
                        │ Has docstring?        │
                        └──────┬────────┬──────┘
                          YES  │        │  NO
                               ▼        ▼
                   ┌─────────────┐  ┌──────────────────┐
                   │ Return       │  │ Is async?        │
                   │ docstring    │  └──────┬────┬──────┘
                   │ directly     │    YES  │    │  NO
                   └─────────────┘         ▼    ▼
                              ┌─────────────────────────┐
                              │ Prefix: "This           │
                              │ [asynchronous] function" │
                              └────────────┬────────────┘
                                           ▼
                              ┌─────────────────────────┐
                              │ Match name against       │
                              │ 16 prefix patterns       │
                              │ (get→retrieves data,     │
                              │  validate→validates...)  │
                              └────────────┬────────────┘
                                      ┌────┴─────┐
                                MATCH? │          │ NO MATCH
                                      ▼          ▼
                         ┌──────────────┐  ┌──────────────┐
                         │ Append:       │  │ (skip this   │
                         │ inferred      │  │  segment)    │
                         │ purpose       │  └──────┬───────┘
                         └──────┬───────┘         │
                                └─────────┬───────┘
                                          ▼
                              ┌─────────────────────────┐
                              │ Has parameters?          │
                              │ (excluding self/cls)     │
                              └──────┬────────┬─────────┘
                                YES  │        │  NO
                                     ▼        ▼
                         ┌──────────────┐  ┌──────────────┐
                         │"takes N      │  │"takes no     │
                         │ param(s):    │  │ parameters"  │
                         │ a, b, c"     │  └──────┬───────┘
                         └──────┬───────┘         │
                                └─────────┬───────┘
                                          ▼
                              ┌─────────────────────────┐
                              │ Has return annotation?   │
                              └──────┬────────┬─────────┘
                                YES  │        │  NO
                                     ▼        ▼
                         ┌──────────────┐  ┌──────────────┐
                         │"returns X"   │  │ (skip)       │
                         └──────┬───────┘  └──────┬───────┘
                                └─────────┬───────┘
                                          ▼
                              ┌─────────────────────────┐
                              │ Function calls detected? │
                              └──────┬────────┬─────────┘
                              ≤5     │        │  >5
                                     ▼        ▼
                         ┌──────────────┐  ┌──────────────┐
                         │"It calls:    │  │"It makes N   │
                         │ a, b, c"     │  │ function     │
                         └──────┬───────┘  │ calls"       │
                                │          └──────┬───────┘
                                └─────────┬───────┘
                                          ▼
                              ┌─────────────────────────┐
                              │ JOIN all parts with ". " │
                              │ Append final "."         │
                              │                          │
                              │ ► OUTPUT: Complete NL    │
                              │   summary string         │
                              └─────────────────────────┘
```

### 8.9 Before & After: Real-World Examples

These examples show what raw code looks like vs. what the AI engine produces:

#### Example 1 — Simple CRUD Function

**Before (raw code — no docs):**

```python
def delete_expired_sessions(session_store, ttl_seconds=3600):
    now = time.time()
    expired = [k for k, v in session_store.items() if now - v['created'] > ttl_seconds]
    for key in expired:
        del session_store[key]
    return len(expired)
```

**After (AI-generated documentation):**

```
📄 Function Summary
───────────────────
Name:        delete_expired_sessions
Purpose:     removes data (matched pattern: delete*)
Parameters:  2 — session_store, ttl_seconds
Returns:     Not annotated
Calls:       time.time, session_store.items

🤖 Generated Summary:
"This function removes data. takes 2 parameter(s): session_store,
ttl_seconds. It calls: time.time, session_store.items."
```

#### Example 2 — Complex Class

**Before:**

```python
class PaymentGatewayController:
    def __init__(self, api_key, sandbox=True):
        self.client = StripeClient(api_key, sandbox)

    def process_payment(self, amount, currency, card_token): ...
    def refund_payment(self, transaction_id): ...
    def get_transaction_history(self, user_id, limit=50): ...
    def validate_card(self, card_number): ...
    def _encrypt_payload(self, data): ...
```

**After:**

```
📄 Class Summary
────────────────
Name:         PaymentGatewayController
Inheritance:  (none)
Methods:      5 total (4 public, 1 private)
Public:       process_payment, refund_payment, get_transaction_history, validate_card

🤖 Generated Summary:
"Class 'PaymentGatewayController' and implements 5 methods including:
process_payment, refund_payment, get_transaction_history, validate_card.
controls application logic."
```

#### Example 3 — File-Level Summary

**Before (file: `auth_middleware.py`):**

```python
import jwt
from functools import wraps
from flask import request, jsonify

class JWTAuthenticator:
    def verify_token(self, token): ...
    def refresh_token(self, token): ...

class RateLimiter:
    def check_limit(self, ip, endpoint): ...

def require_auth(f): ...
def require_admin(f): ...
```

**After:**

```
📄 File Summary
───────────────
Filename:    auth_middleware.py
Classes:     2 — JWTAuthenticator, RateLimiter
Functions:   2 standalone — require_auth, require_admin
Imports:     3 modules

🤖 Generated Summary:
"File 'auth_middleware.py' defines 2 class(es): JWTAuthenticator,
RateLimiter and 2 function(s). It imports 3 module(s)."
```

### 8.10 Similarity Engine: How Code Comparison Works

The `ModelManager.calculate_similarity()` method provides two modes of operation:

```
┌──────────────────────────────────────────────────────────────────┐
│              SIMILARITY CALCULATION PIPELINE                      │
│                                                                   │
│   Code A ──┐                                                      │
│            │    ┌──────────────────────────────────┐              │
│            ├───►│  Is CodeBERT model loaded?       │              │
│            │    └───────────┬──────────┬───────────┘              │
│   Code B ──┘          YES  │          │  NO                       │
│                            ▼          ▼                           │
│              ┌──────────────┐  ┌──────────────────┐              │
│              │ DEEP MODE     │  │ FALLBACK MODE     │              │
│              │               │  │                   │              │
│              │ 1. Tokenize A │  │ 1. Split on       │              │
│              │ 2. Tokenize B │  │    whitespace      │              │
│              │ 3. Forward    │  │ 2. Create set A    │              │
│              │    pass →     │  │ 3. Create set B    │              │
│              │    embeddings │  │ 4. Compute Jaccard │              │
│              │ 4. Mean pool  │  │    |A ∩ B|         │              │
│              │ 5. Cosine sim │  │    ────────        │              │
│              │    A · B      │  │    |A ∪ B|         │              │
│              │   ───────     │  │                   │              │
│              │   |A||B|      │  │ Score: 0.0 – 1.0  │              │
│              │               │  │                   │              │
│              │ Score: 0 – 1  │  └──────────────────┘              │
│              └──────────────┘                                     │
│                                                                   │
│   Score Interpretation:                                           │
│   ■■■■■■■■■■ 0.8–1.0  Very similar (potential duplicate)         │
│   ■■■■■■■■░░ 0.6–0.8  Similar logic, different style             │
│   ■■■■■░░░░░ 0.3–0.6  Some overlap                               │
│   ■■░░░░░░░░ 0.0–0.3  Different code                             │
└──────────────────────────────────────────────────────────────────┘
```

### 8.11 All 10 Prompt Templates — Quick Reference Card

These ready-to-use templates connect the AI engine to any LLM (Ollama, OpenAI, Claude, etc.):

```
┌────┬──────────────────────────────┬──────────────────────────────────┐
│ #  │ Template                     │ Generates Prompt For             │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 1  │ function_summary_prompt()    │ "Explain this function in 1      │
│    │                              │  sentence + business logic +     │
│    │                              │  potential issues"               │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 2  │ class_summary_prompt()       │ "Explain this class's purpose,   │
│    │                              │  what it manages, key duties"    │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 3  │ file_summary_prompt()        │ "Summarize this file: purpose,   │
│    │                              │  functionality, system role"     │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 4  │ code_smell_explanation()     │ "Why is this a smell? Problems?  │
│    │                              │  Refactoring suggestion?"        │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 5  │ refactoring_suggestion()     │ "Issues causing high complexity, │
│    │                              │  step-by-step refactor plan"     │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 6  │ dependency_analysis()        │ "Coupling assessment, circular   │
│    │                              │  risk, modularity advice"        │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 7  │ code_quality_prompt()        │ "Overall rating, top 3 areas,    │
│    │                              │  priority recommendations"       │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 8  │ documentation_generation()   │ "Google-style docstring + param  │
│    │                              │  descriptions + example usage"   │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 9  │ bug_detection_prompt()       │ "Runtime errors, logic errors,   │
│    │                              │  edge cases, security concerns"  │
├────┼──────────────────────────────┼──────────────────────────────────┤
│ 10 │ test_generation_prompt()     │ "pytest cases: normal, edge,     │
│    │                              │  error, boundary conditions"     │
└────┴──────────────────────────────┴──────────────────────────────────┘
```

### 8.12 AI Engine Configuration & Tuning Guide

Users can customize the AI engine behavior via `config.yaml`:

```yaml
ai:
  # ── Model Selection ──
  model_name: microsoft/codebert-base # Options: codebert-base, graphcodebert-base, codet5-small
  use_local_model: false # Set true to enable CodeBERT embeddings
  max_token_length: 512 # Max tokens per code snippet (512 for BERT models)
  batch_size: 8 # Batch size for bulk encoding


  # ── Similarity Thresholds ──
  # (used by duplicate detection & similarity calculator)
  # duplicate_threshold is in quality section → 0.8 default
```

**Tuning Recommendations:**

| Setting            | Default         | When to Change                                                    | Impact                                                              |
| ------------------ | --------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| `use_local_model`  | `false`         | Set `true` if you have 2GB+ free RAM and want semantic similarity | Enables CodeBERT embeddings; much more accurate duplicate detection |
| `model_name`       | `codebert-base` | Use `codet5-small` for seq2seq summaries                          | Different model = different summary quality                         |
| `max_token_length` | `512`           | Increase to `1024` for very long functions                        | Higher = more context but slower inference                          |
| `batch_size`       | `8`             | Lower to `2` on machines with <8GB RAM                            | Prevents out-of-memory during bulk analysis                         |

**Model Comparison:**

| Model                          | Parameters | Best For                              | Speed  | Quality                         |
| ------------------------------ | ---------- | ------------------------------------- | ------ | ------------------------------- |
| `microsoft/codebert-base`      | 125M       | Code embeddings & similarity          | Fast   | Good for search/compare         |
| `microsoft/graphcodebert-base` | 125M       | Code that has data-flow dependencies  | Medium | Better structural understanding |
| `Salesforce/codet5-small`      | 60M        | Generating text summaries from code   | Fast   | Good NL output                  |
| `Salesforce/codet5-base`       | 220M       | High-quality code→English translation | Slow   | Best NL output                  |

---

## 9. DATA FLOW & PROCESSING PIPELINE

### 9.1 End-to-End Pipeline

```
INPUT                    PROCESSING                           OUTPUT
─────                    ──────────                           ──────

Local Path    ──┐
                ├──→ [1] Ingestion ──→ [2] AST Parsing ──→ [3] Analysis
GitHub URL    ──┘        │                   │                    │
                         │                   │                    │
                    Load files          Parse syntax         Compute:
                    Filter types        Extract:             • Cyclomatic CC
                    Read content        • Functions          • Maintainability
                                        • Classes            • Halstead
                                        • Imports            • Raw Metrics
                                        • Globals
                                             │
                         ┌───────────────────┤
                         ▼                   ▼
                   [4] Extraction      [5] AI Engine
                         │                   │
                   • Dependencies       • NL Summaries
                   • Code Smells        • Documentation
                   • Call Graph         • Explanations
                   • Duplicates
                         │                   │
                         └─────────┬─────────┘
                                   ▼
                            [6] Compilation
                                   │
                         ┌─────────┼─────────┐
                         ▼         ▼         ▼
                      [7a]      [7b]      [7c]
                    Reports   Visuals    JSON Data
                    (MD/HTML)  (PNG)     (Raw Export)
```

### 9.2 Data Structures

**Per-File Analysis Result:**

```json
{
  "filepath": "src/module.py",
  "file_info": {
    "name": "module.py",
    "relative_path": "src/module.py",
    "lines": 150,
    "size": 4096
  },
  "functions": [
    {
      "name": "process_data",
      "params": ["data", "config"],
      "docstring": "Process input data...",
      "calls": ["validate", "transform"],
      "decorators": [],
      "start_line": 10,
      "end_line": 45
    }
  ],
  "classes": [...],
  "imports": [...],
  "globals": [...],
  "complexity": {
    "cyclomatic_complexity": { "average": 4.5, "max": 12, "details": [...] },
    "maintainability_index": 65.2,
    "halstead": {...},
    "raw_metrics": { "loc": 150, "sloc": 120, "comments": 15, "blanks": 15 }
  },
  "code_smells": {
    "smells": [...],
    "total_smell_count": 3
  },
  "documentation": {
    "file_summary": "This module handles data processing...",
    "function_docs": [...],
    "class_docs": [...]
  }
}
```

**Repository-Level Summary:**

```json
{
  "metadata": {
    "source": "/path/to/project",
    "analyzed_at": "2026-02-24 20:00:00",
    "total_files": 15,
    "analysis_time_seconds": 3.45
  },
  "summary": {
    "total_functions": 87,
    "total_classes": 12,
    "total_lines_of_code": 5200,
    "total_code_smells": 23,
    "average_complexity": 4.8,
    "average_maintainability": 62.5,
    "most_complex_files": [...],
    "dependency_analysis": {
      "has_circular_dependencies": false,
      "isolated_files": 2
    }
  },
  "files": [...],
  "dependencies": {
    "dependency_graph": { "nodes": [...], "edges": [...] },
    "analysis": {
      "most_depended": [...],
      "most_dependent": [...],
      "circular_dependencies": [],
      "isolated_files": [...]
    }
  },
  "duplicates": [...],
  "repository_metrics": {
    "average_complexity": 4.8,
    "average_maintainability": 62.5
  }
}
```

---

## 10. OUTPUT ARTIFACTS

### 10.1 Generated Reports

| Artifact                | Format   | Description                                                                                 |
| ----------------------- | -------- | ------------------------------------------------------------------------------------------- |
| `analysis_results.json` | JSON     | Complete raw analysis data; machine-readable                                                |
| `analysis_report.md`    | Markdown | Human-readable report with quality indicators, per-file breakdowns, recommendations         |
| `analysis_report.html`  | HTML     | Interactive styled report with quality grades (A–D), color-coded metrics, responsive layout |
| `dependency_graph.png`  | PNG      | NetworkX spring-layout graph; node sizes = degree, colors = in-degree                       |
| `complexity_chart.png`  | PNG      | Horizontal bar chart; files colored green/yellow/red by complexity                          |
| `metrics_summary.png`   | PNG      | 4-panel summary: stats table, gauge, maintainability bars, top complex files                |

### 10.2 Quality Grading Scale

| Grade | Maintainability Index | Label                                 |
| ----- | --------------------- | ------------------------------------- |
| **A** | ≥ 20                  | Excellent — Well-maintained code      |
| **B** | 10 – 19               | Good — Acceptable quality             |
| **C** | 5 – 9                 | Fair — Needs improvement              |
| **D** | < 5                   | Poor — Significant refactoring needed |

### 10.3 Complexity Thresholds

| Level     | Cyclomatic Complexity | Interpretation                        |
| --------- | --------------------- | ------------------------------------- |
| 🟢 Low    | 1 – 5                 | Simple, low risk                      |
| 🟡 Medium | 6 – 10                | Moderate risk, consider refactoring   |
| 🔴 High   | > 10                  | High risk, difficult to test/maintain |

---

## 11. TESTING STRATEGY

### 11.1 Test Coverage

| Test File          | Module Tested                                                                         | Test Cases                                                                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `test_parser.py`   | `ASTParser`                                                                           | Function parsing, class parsing, imports, parameters, docstrings, syntax error handling, empty files, global variables                                      |
| `test_analyzer.py` | `ComplexityAnalyzer`, `MetricsCalculator`, `CodeSmellDetector`, `DependencyExtractor` | Initialization, simple/complex code, MI calculation, empty code, LOC counting, doc coverage, parameter smell, dead code, global variables, integration test |

### 11.2 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Verbose output
pytest -v tests/
```

### 11.3 Test Fixtures

Tests use a shared `sample_repo/` directory containing:

- `calculator.py` — Sample class with arithmetic methods
- `utils.py` — Utility functions for testing extraction

---

## 12. SCREENSHOTS / SAMPLE OUTPUTS

### 12.1 CLI Output Example

```
╔════════════════════════════════════════════════════════════╗
║     🏛️  CODEBASE ARCHAEOLOGIST  🏛️                        ║
║     AI-Powered Legacy Code Analysis System                 ║
║     Version 1.0.0                                          ║
╚════════════════════════════════════════════════════════════╝

======================================================================
                         ANALYSIS SUMMARY
======================================================================

📊 Code Statistics:
   ├─ Total Functions:          87
   ├─ Total Classes:            12
   └─ Lines of Code:         5,200

📈 Quality Metrics:
   ├─ Avg Complexity:         4.80  ✅ Good
   ├─ Maintainability:       62.50  (A) ✅ Good
   └─ Code Smells:              23  ⚠️  Many

⚠️  Most Complex Files:
   1. 🔴 chart_creator.py                        M=8.5
   2. 🟡 streamlit_app.py                        M=6.2
   3. 🟢 markdown_generator.py                   M=3.1

======================================================================

✅ Analysis complete!
📂 Results saved to: ./outputs
```

### 12.2 HTML Report

The HTML report features:

- Gradient header with project metadata
- Quality grade badge (A/B/C/D)
- Responsive metric cards
- Color-coded file analysis tables
- Code smell summaries
- Dependency information

### 12.3 Dependency Graph

The dependency graph renders as a force-directed network where:

- **Node size** ∝ number of connections (degree centrality)
- **Node color** ∝ number of incoming dependencies (in-degree)
- **Edges** represent import relationships
- **Circular dependencies** are highlighted

---

## 13. TOTAL WORKFLOW PROCESS (STEP-BY-STEP)

> **Presentation Guide:** This section walks through the complete end-to-end workflow of the Codebase Archaeologist system — from user input to final output. Use this to explain the project flow during your demo.

---

### WORKFLOW OVERVIEW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CODEBASE ARCHAEOLOGIST — FULL WORKFLOW                   │
└─────────────────────────────────────────────────────────────────────────────┘

  USER INPUT                                                     USER OUTPUT
  ──────────                                                     ───────────
  ┌──────────────┐                                         ┌──────────────────┐
  │ Local Path   │                                         │ JSON Report      │
  │    OR        │                                         │ Markdown Report  │
  │ GitHub URL   │                                         │ HTML Report      │
  │    OR        │                                         │ PNG Graphs       │
  │ Streamlit UI │                                         │ Interactive Dash │
  └──────┬───────┘                                         └────────▲─────────┘
         │                                                          │
         ▼                                                          │
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌─────┴────────┐
  │  STEP 1      │    │  STEP 2      │    │  STEP 3      │    │  STEP 7      │
  │  Ingestion   │───▶│  AST Parsing │───▶│  Analysis    │    │  Reporting   │
  │              │    │              │    │              │    │              │
  │ • Load files │    │ • Parse tree │    │ • Complexity │    │ • Markdown   │
  │ • Clone repo │    │ • Functions  │    │ • MI Score   │    │ • HTML       │
  │ • Filter     │    │ • Classes    │    │ • Halstead   │    │ • JSON       │
  └──────────────┘    │ • Imports    │    │ • Raw LOC    │    └──────────────┘
                      └──────────────┘    └──────┬───────┘          ▲
                                                 │                  │
                                    ┌────────────┴────────────┐     │
                                    ▼                         ▼     │
                             ┌──────────────┐          ┌──────────────┐
                             │  STEP 4      │          │  STEP 5      │
                             │  Extraction  │          │  AI Engine   │
                             │              │          │              │
                             │ • Deps Graph │          │ • NL Summary │
                             │ • Smells     │          │ • Explain    │
                             │ • Call Graph │          │ • Document   │
                             │ • Duplicates │          │ • Infer      │
                             └──────┬───────┘          └──────┬───────┘
                                    │                         │
                                    └────────────┬────────────┘
                                                 ▼
                                          ┌──────────────┐
                                          │  STEP 6      │
                                          │  Compilation │
                                          │              │
                                          │ • Merge all  │
                                          │ • Summary    │
                                          │ • Metadata   │
                                          └──────┬───────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │  STEP 7      │
                                          │ Visualization│
                                          │              │
                                          │ • Charts     │
                                          │ • Graphs     │
                                          │ • Dashboard  │
                                          └──────────────┘
```

---

### STEP 1 — INGESTION (Loading the Codebase)

**Who does it:** `CodeLoader` (in `src/ingestion/code_loader.py`) + `FileFilter` (`src/ingestion/file_filter.py`)

**What happens:**

| #   | Action                       | Detail                                                                                                                                                                                                                     |
| --- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1.1 | **User provides input**      | Either a local directory path (`C:\myproject`) or a GitHub URL (`https://github.com/user/repo.git`)                                                                                                                        |
| 1.2 | **GitHub clone (if URL)**    | Runs `git clone --depth 1` (shallow clone) into a temp directory. Handles Windows read-only `.git` files via `_force_rmtree()` with `stat.S_IWRITE` fallback. Falls back to UUID-based unique paths if temp dir is locked. |
| 1.3 | **Recursive directory scan** | `_scan_directory()` walks the entire file tree, reading each file's content                                                                                                                                                |
| 1.4 | **Filtering**                | Excludes: `__pycache__`, `.git`, `node_modules`, `venv`, binary files, files > 10 MB. Keeps only supported languages (Python, JS, Java, etc.)                                                                              |
| 1.5 | **Language filtering**       | `filter_by_language()` narrows to the target language (default: Python `.py` files)                                                                                                                                        |

**Output:** A list of file dicts, each containing `path`, `name`, `content`, `lines`, `size`.

**Example:**

```python
# User runs:
python cli.py https://github.com/user/my-project.git

# Step 1 produces:
{
  "source": "./temp_repo",
  "type": "github",
  "files": [
    {"path": "./temp_repo/main.py", "name": "main.py", "content": "...", "lines": 150, "size": 4096},
    {"path": "./temp_repo/utils.py", "name": "utils.py", "content": "...", "lines": 80, "size": 2048}
  ],
  "total_files": 2
}
```

---

### STEP 2 — AST PARSING (Understanding Code Structure)

**Who does it:** `ASTParser` (in `src/analysis/ast_parser.py`)

**What happens:**

| #   | Action                  | Detail                                                                                                                                                                               |
| --- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2.1 | **Parse source to AST** | Uses Python's built-in `ast.parse()` to convert raw source code into an Abstract Syntax Tree                                                                                         |
| 2.2 | **Walk the tree**       | `_analyze_node()` visits every node in the tree                                                                                                                                      |
| 2.3 | **Extract functions**   | For each `ast.FunctionDef` / `ast.AsyncFunctionDef`: name, parameters, return type annotation, docstring, line range (start→end), decorators, and all function calls inside the body |
| 2.4 | **Extract classes**     | For each `ast.ClassDef`: name, base classes (inheritance), docstring, method names, method count, decorators                                                                         |
| 2.5 | **Extract imports**     | For each `ast.Import` / `ast.ImportFrom`: module name, imported names, aliases, relative import level                                                                                |
| 2.6 | **Extract globals**     | Module-level `ast.Assign` nodes: variable names and their types                                                                                                                      |

**Key insight for presentation:** _"We don't just read the code as text — we parse it into a structured tree that a computer can reason about. This is the same technique compilers use."_

**Output per file:**

```python
{
  "filepath": "main.py",
  "functions": [
    {"name": "process_data", "params": ["data", "config"], "docstring": "...",
     "calls": ["validate", "transform"], "start_line": 10, "end_line": 45}
  ],
  "classes": [
    {"name": "DataProcessor", "bases": ["BaseProcessor"], "methods": ["run", "validate"]}
  ],
  "imports": [{"module": "os", "names": ["path"]}],
  "global_variables": [{"name": "MAX_RETRIES", "type": "Constant"}]
}
```

---

### STEP 3 — COMPLEXITY ANALYSIS (Measuring Code Quality)

**Who does it:** `ComplexityAnalyzer` (`src/analysis/complexity_analyzer.py`) + `MetricsCalculator` (`src/analysis/metrics_calculator.py`)

**What happens:**

| #   | Metric                         | How it's calculated                                                        | What it means                                                         |
| --- | ------------------------------ | -------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 3.1 | **Cyclomatic Complexity (CC)** | `radon.cc_visit()` — counts decision points (if/elif/for/while/try/and/or) | CC ≤ 5 = Simple, 6–10 = Moderate, 11–20 = Complex, >20 = Very Complex |
| 3.2 | **Maintainability Index (MI)** | `radon.mi_visit()` — formula combining Halstead Volume, CC, and LOC        | MI ≥ 20 = Grade A (good), 10–19 = Grade B, < 10 = Grade C (poor)      |
| 3.3 | **Halstead Metrics**           | `radon.h_visit()` — counts operators and operands                          | Volume, Difficulty, Effort, Estimated bugs                            |
| 3.4 | **Raw Metrics**                | Line counting                                                              | LOC, SLOC (source lines), Comments, Blank lines                       |
| 3.5 | **Documentation Coverage**     | % of functions + classes with docstrings                                   | Shows how well-documented the code is                                 |

**Key insight for presentation:** _"We use three mathematically proven metrics (McCabe 1976, Halstead 1977, Coleman 1994) to objectively score code quality — not opinions, but numbers."_

**Example output:**

```
File: calculator.py
├── Cyclomatic Complexity:  Avg = 2.3, Max = 5  → ✅ Good
├── Maintainability Index:  65.2 (Grade A)       → ✅ Good
├── Halstead Volume:        1,250                 → Moderate
└── Raw: 150 LOC, 120 SLOC, 15 Comments, 15 Blank
```

---

### STEP 4 — EXTRACTION (Finding Patterns & Problems)

**Who does it:** `DependencyExtractor`, `CodeSmellDetector`, `CallGraphBuilder` (in `src/extraction/`)

**This step runs in parallel with Step 5.** Three sub-analyses happen:

#### 4A. Dependency Graph Construction

| #    | Action                   | Detail                                                                                  |
| ---- | ------------------------ | --------------------------------------------------------------------------------------- |
| 4A.1 | **Build directed graph** | Creates a `networkx.DiGraph` where each file is a node                                  |
| 4A.2 | **Resolve imports**      | Maps `from src.utils import helpers` → edge from current file to `src/utils/helpers.py` |
| 4A.3 | **Analyze graph**        | Finds: most-depended files, circular dependencies (`nx.simple_cycles`), isolated files  |

#### 4B. Code Smell Detection (7 smell categories)

| #    | Smell               | Rule                                               |
| ---- | ------------------- | -------------------------------------------------- |
| 4B.1 | Long Functions      | Body > 50 lines                                    |
| 4B.2 | Long Classes        | Body > 300 lines                                   |
| 4B.3 | Missing Docstrings  | No `"""..."""`                                     |
| 4B.4 | Too Many Parameters | > 5 params (excluding `self`/`cls`)                |
| 4B.5 | Dead Code           | Functions defined but never called within the file |
| 4B.6 | Magic Numbers       | Hardcoded numeric literals like `3.14`, `86400`    |
| 4B.7 | Global Variables    | Non-constant module-level assignments              |

Plus: **Cross-file duplicate detection** — finds functions with same name + same parameter count across different files.

#### 4C. Call Graph Construction

| #    | Action                        | Detail                                                                       |
| ---- | ----------------------------- | ---------------------------------------------------------------------------- |
| 4C.1 | **Collect all functions**     | Creates unique IDs like `main.py::DataProcessor.run`                         |
| 4C.2 | **Build caller→callee edges** | Maps which function calls which                                              |
| 4C.3 | **Analyze**                   | Finds: most-called functions, recursive functions, dead-end (leaf) functions |

---

### STEP 5 — AI-POWERED SUMMARIZATION (Generating Human-Readable Docs)

**Who does it:** `CodeSummarizer` (`src/ai_engine/code_summarizer.py`)

**What happens (runs in parallel with Step 4):**

| #   | Action                           | Detail                                                       |
| --- | -------------------------------- | ------------------------------------------------------------ |
| 5.1 | **Check for existing docstring** | If a function/class already has a docstring, use it directly |
| 5.2 | **Pattern-based name inference** | Matches function name prefixes to meaning:                   |

**Name-to-Purpose Mapping (16 patterns):**

| Prefix                                   | Inferred Purpose        | Example                                         |
| ---------------------------------------- | ----------------------- | ----------------------------------------------- |
| `get_`, `fetch_`                         | "Retrieves data"        | `get_user()` → "Retrieves user data"            |
| `set_`, `update_`                        | "Updates/modifies data" | `set_config()` → "Updates config data"          |
| `calculate_`, `compute_`                 | "Performs calculations" | `calculate_tax()` → "Computes tax calculations" |
| `validate_`, `check_`, `verify_`         | "Validates input"       | `validate_email()` → "Validates email input"    |
| `create_`, `build_`, `make_`             | "Creates/constructs"    | `create_report()` → "Constructs a new report"   |
| `delete_`, `remove_`                     | "Removes data"          | `delete_user()` → "Removes user data"           |
| `is_`, `has_`, `can_`                    | "Boolean check"         | `is_valid()` → "Checks if valid"                |
| `init_`, `setup_`, `configure_`          | "Initializes"           | `setup_db()` → "Sets up database"               |
| `parse_`, `extract_`                     | "Parses/processes"      | `parse_json()` → "Parses JSON input"            |
| `save_`, `write_`, `export_`             | "Persists data"         | `save_results()` → "Saves results to storage"   |
| `load_`, `read_`, `import_`              | "Loads data"            | `load_config()` → "Loads configuration"         |
| `convert_`, `transform_`                 | "Transforms data"       | `convert_csv()` → "Converts CSV format"         |
| `display_`, `show_`, `print_`, `render_` | "Displays output"       | `render_chart()` → "Renders visual output"      |
| `handle_`, `process_`                    | "Handles/processes"     | `handle_request()` → "Processes the request"    |
| `test_`                                  | "Tests functionality"   | `test_login()` → "Tests login functionality"    |
| `_` (leading)                            | "Internal helper"       | `_clean_data()` → "Internal helper method"      |

| #   | Action                      | Detail                                                                |
| --- | --------------------------- | --------------------------------------------------------------------- |
| 5.3 | **Build composite summary** | Combines: purpose (from name) + parameters + return type + calls made |
| 5.4 | **Class summarization**     | Describes inheritance hierarchy, method count, inferred role          |
| 5.5 | **File summarization**      | Describes what classes and standalone functions the file contains     |

**Example:**

```
Input:  def calculate_average(numbers: list, weights: list = None) -> float:
            """..."""

Output: "Performs calculations on numbers with optional weights parameter.
         Returns float. Calls: sum(), len(), zip()."
```

---

### STEP 6 — RESULT COMPILATION (Merging Everything)

**Who does it:** `CodebaseArchaeologist._generate_summary()` in `main.py`

**What happens:**

| #   | Action                          | Detail                                                                              |
| --- | ------------------------------- | ----------------------------------------------------------------------------------- |
| 6.1 | **Merge per-file results**      | Combines AST data + complexity + smells + AI docs into one dict per file            |
| 6.2 | **Generate repository summary** | Aggregates: total functions/classes/LOC, avg complexity, avg MI, most complex files |
| 6.3 | **Add metadata**                | Timestamps, source path, file count, analysis duration                              |
| 6.4 | **Save JSON**                   | Writes `analysis_results.json` to `outputs/reports/` (if `save_to_disk=True`)       |

**The final compiled result is a single Python dictionary containing everything:**

```python
results = {
    "metadata":           {...},   # source, timestamp, file count, duration
    "summary":            {...},   # totals, averages, top complex files
    "files":              [...],   # per-file: AST + complexity + smells + AI docs
    "dependencies":       {...},   # graph + analysis
    "duplicates":         [...],   # cross-file duplicate functions
    "repository_metrics": {...}    # avg complexity, avg MI
}
```

---

### STEP 7 — OUTPUT GENERATION (Reports + Visuals + Dashboard)

**Who does it:** Multiple generators working on the compiled results

#### 7A. Report Generation

| Generator           | Output                  | Key Features                                                                                   |
| ------------------- | ----------------------- | ---------------------------------------------------------------------------------------------- |
| `MarkdownGenerator` | `analysis_report.md`    | Section headers, tables, emoji status indicators, top-10 files, recommendations                |
| `HTMLGenerator`     | `analysis_report.html`  | Styled with CSS, quality grade badge (A/B/C/D), collapsible file sections, color-coded metrics |
| JSON (built-in)     | `analysis_results.json` | Raw machine-readable data for programmatic access                                              |

#### 7B. Visualization Generation

| Generator        | Output                     | Library                                                      |
| ---------------- | -------------------------- | ------------------------------------------------------------ |
| `GraphGenerator` | Dependency graph PNG       | Matplotlib + NetworkX (spring layout, nodes sized by degree) |
| `GraphGenerator` | Complexity bar chart PNG   | Matplotlib (green/yellow/red bars per file)                  |
| `GraphGenerator` | Metrics summary PNG        | Matplotlib (2×2 subplot with gauge)                          |
| `ChartCreator`   | Interactive heatmap HTML   | Plotly (scatter plot of function complexity)                 |
| `ChartCreator`   | Interactive dashboard HTML | Plotly (gauge + donut + bars)                                |
| `ChartCreator`   | Interactive network HTML   | Plotly (circular dependency layout)                          |

#### 7C. Streamlit Dashboard (Interactive Mode)

| Tab                | What User Sees                                                                                                        |
| ------------------ | --------------------------------------------------------------------------------------------------------------------- |
| **Overview**       | KPI cards (files, functions, classes, LOC), quality grade, complexity gauge, maintainability score                    |
| **Visualizations** | Interactive Plotly charts: complexity heatmap, metrics dashboard, dependency network, LOC breakdown                   |
| **Files**          | Searchable file list with expandable details — click any file to see its functions, classes, complexity, AI summaries |
| **Dependencies**   | Dependency table, most-imported files, circular dependency warnings                                                   |
| **Code Smells**    | Tabulated smells by category with severity indicators and fix suggestions                                             |
| **Export**         | Download buttons for JSON, Markdown summary, and full HTML report                                                     |

---

### COMPLETE EXECUTION TRACE (What happens when you run it)

**Method 1 — CLI:**

```powershell
python cli.py tests/sample_repo
```

```
Time    What Happens                                          Code Location
─────   ────────────                                          ─────────────
t=0.00  CLI parses arguments, prints banner                   cli.py → main()
t=0.01  CodebaseArchaeologist initialized                     main.py → __init__()
        ├── Config loaded from config.yaml                    utils/helpers.py
        ├── CodeLoader, ASTParser, ComplexityAnalyzer,         main.py lines 53-58
        │   DependencyExtractor, CodeSmellDetector,
        │   CodeSummarizer all instantiated
        └── Output directory created                          utils/helpers.py

t=0.02  STEP 1: Ingestion starts                              main.py → analyze_local()
        ├── code_loader.load_from_local() scans directory      code_loader.py
        ├── Found 2 Python files                               code_loader.py
        └── filter_by_language('python') applied               code_loader.py

t=0.05  STEP 2-5: Per-file analysis loop (with progress bar)
        For EACH .py file:
        │
        ├── STEP 2: ast_parser.parse_file()                    ast_parser.py
        │   └── Extracts functions, classes, imports, globals
        │
        ├── STEP 3: complexity_analyzer.analyze_file()         complexity_analyzer.py
        │   └── Computes CC, MI, Halstead, raw metrics
        │
        ├── STEP 4: smell_detector.detect_smells()             code_smell_detector.py
        │   └── Runs all 7 smell checks
        │
        └── STEP 5: summarizer.generate_documentation()        code_summarizer.py
            └── Generates NL summaries for all functions/classes

t=0.15  STEP 4 (repo-level): Extract dependencies             main.py line 97
        └── dependency_extractor.extract_dependencies()        dependency_extractor.py
            └── Builds NetworkX DiGraph, detects circular deps

t=0.20  STEP 4 (repo-level): Detect duplicates                main.py line 101
        └── smell_detector.detect_duplicates()                 code_smell_detector.py

t=0.25  STEP 3 (repo-level): Repository metrics               main.py line 105
        └── complexity_analyzer.analyze_repository()           complexity_analyzer.py

t=0.30  STEP 6: Compile results                               main.py → _generate_summary()
        └── Merge everything into single results dict

t=0.32  STEP 6: Save JSON                                     main.py → _save_results()
        └── Write outputs/reports/analysis_results.json

t=0.35  STEP 7: Generate reports                               cli.py lines 218-240
        ├── MarkdownGenerator → analysis_report.md
        └── HTMLGenerator → analysis_report.html

t=0.38  STEP 7: Generate visualizations                        cli.py lines 242-260
        ├── Dependency graph → PNG
        ├── Complexity chart → PNG
        └── Metrics summary → PNG

t=0.41  Print summary table to terminal                       cli.py → print_summary_table()
        └── Shows: functions, classes, LOC, complexity, MI, smells

        ✅ DONE — Total time: 0.41 seconds
```

**Method 2 — Streamlit Dashboard:**

```powershell
streamlit run web/streamlit_app.py
```

```
Time    What Happens                                          Code Location
─────   ────────────                                          ─────────────
t=0.00  Streamlit launches on http://localhost:8501            streamlit_app.py
t=0.01  Welcome screen displayed with feature cards            display_welcome()

        USER ACTION: Enters GitHub URL + clicks "Analyze"

t=0.02  CodebaseArchaeologist(save_to_disk=False) initialized  main.py
t=0.05  analyze_github() → clones repo → analyze_local()      main.py
t=0.10  All 7 steps execute (same as CLI)                     main.py
t=0.40  Results stored in st.session_state                     streamlit_app.py
t=0.41  6-tab dashboard rendered:                              streamlit_app.py
        ├── Tab 1: Overview with KPI cards
        ├── Tab 2: Interactive Plotly charts
        ├── Tab 3: Searchable file explorer
        ├── Tab 4: Dependency tables
        ├── Tab 5: Code smell breakdown
        └── Tab 6: Export/download buttons

        USER ACTION: Clicks "Download HTML"
        → File downloads WITHOUT page redirect (session_state preserves results)
```

---

### HOW TO DEMO (Presentation Script)

**Step 1 — Show the problem (30 seconds):**

> _"Imagine you join a company and are given 50,000 lines of undocumented Python code. How long would it take you to understand it? Weeks? Months?"_

**Step 2 — Run CLI analysis (1 minute):**

```powershell
python cli.py tests/sample_repo
```

> _"In under 1 second, our tool analyzes the entire codebase — parsing every function, measuring complexity, detecting code smells, and generating AI documentation."_

**Step 3 — Show the output (1 minute):**

> Point to the terminal summary table showing functions, classes, LOC, complexity score, maintainability grade.
> Open `outputs/reports/analysis_report.html` in browser.

**Step 4 — Launch Streamlit dashboard (2 minutes):**

```powershell
streamlit run web/streamlit_app.py
```

> Walk through each tab:
>
> - **Overview tab:** _"These metrics tell us the code health at a glance"_
> - **Visualizations tab:** _"Interactive charts let you drill into complexity hotspots"_
> - **Files tab:** _"Click any file to see AI-generated summaries for every function"_
> - **Code Smells tab:** _"57 issues detected automatically — long functions, missing docs, magic numbers"_

**Step 5 — Analyze a GitHub repo live (1 minute):**

> Enter any public GitHub URL in the sidebar → click Analyze
> _"It works on any Python project — local or remote."_

**Step 6 — Show architecture (30 seconds):**

> _"The system uses a 7-layer pipeline: Ingestion → AST Parsing → Complexity Analysis → Extraction → AI Summarization → Compilation → Output Generation. Each layer is a separate module that can be upgraded independently."_

---

## 14. LIMITATIONS & FUTURE SCOPE

### 13.1 Current Limitations

| Limitation                       | Description                                                                 |
| -------------------------------- | --------------------------------------------------------------------------- |
| **Python-only deep analysis**    | AST parsing works fully only for Python; JS/Java support is structural only |
| **Rule-based AI**                | Current summarization uses pattern matching, not true LLM inference         |
| **No incremental analysis**      | Re-analyzes entire codebase on each run (no caching/diffing)                |
| **Single-language dependencies** | Cross-language import resolution not supported                              |
| **No runtime analysis**          | Static-only; cannot detect runtime behaviors or dynamic imports             |

### 13.2 Future Scope

1. **Full LLM Integration** — Connect to Ollama/OpenAI for true natural language code explanation using the existing `PromptTemplates` and `ModelManager` scaffolding.

2. **Multi-Language AST** — Extend `ASTParser` with Tree-sitter for JavaScript, TypeScript, Java, Go parsing.

3. **Incremental Analysis** — Cache previous results and analyze only changed files (Git diff-based).

4. **Interactive Knowledge Graph** — Browser-based explorable dependency graph with click-to-navigate.

5. **CI/CD Integration** — GitHub Actions / GitLab CI plugin for automated quality gates.

6. **VS Code Extension** — In-editor annotations showing complexity, smells, and AI summaries inline.

7. **Historical Trend Tracking** — Track quality metrics over time across Git commits.

8. **Refactoring Suggestions** — Actionable, automated refactoring recommendations with code diffs.

---

## 15. CONCLUSION

The **Codebase Archaeologist** successfully demonstrates that combining static analysis techniques (AST parsing, complexity metrics, dependency graphs) with AI-powered summarization can significantly reduce the cognitive burden of understanding unfamiliar codebases.

The system achieves all three primary objectives:

1. **AI-Based Explanation Engine** — Implemented via rule-based summarization with a clear upgrade path to transformer models (CodeBERT scaffolding in place).
2. **Dependency Knowledge Graph** — Fully functional NetworkX-based graph with circular dependency detection, critical path analysis, and visual rendering.
3. **Comprehensive Audit Report** — Multi-format output (JSON + Markdown + HTML) combining metrics, explanations, and visualizations into a single navigable document.

The modular architecture ensures extensibility, allowing each component to be upgraded independently—from rule-based summarization to full LLM integration, from Python-only parsing to multi-language support via Tree-sitter.

---

## 16. REFERENCES

1. McCabe, T.J. (1976). "A Complexity Measure." _IEEE Transactions on Software Engineering_, SE-2(4), 308–320.
2. Halstead, M.H. (1977). _Elements of Software Science_. Elsevier.
3. Coleman, D. et al. (1994). "Using Metrics to Evaluate Software System Maintainability." _Computer_, 27(8), 44–49.
4. Feng, Z. et al. (2020). "CodeBERT: A Pre-Trained Model for Programming and Natural Languages." _EMNLP 2020_.
5. Wang, Y. et al. (2021). "CodeT5: Identifier-aware Unified Pre-trained Encoder-Decoder Models for Code Understanding and Generation." _EMNLP 2021_.
6. Fowler, M. (2018). _Refactoring: Improving the Design of Existing Code_. Addison-Wesley Professional.
7. Python `ast` Module Documentation — https://docs.python.org/3/library/ast.html
8. Radon Documentation — https://radon.readthedocs.io/
9. NetworkX Documentation — https://networkx.org/documentation/
10. Streamlit Documentation — https://docs.streamlit.io/

---

_Document generated for the Codebase Archaeologist Project — Version 1.0.0_
