# 🏛️ Codebase Archaeologist

**AI-Powered Legacy Code Analysis System**

Codebase Archaeologist is a Python-based tool that analyzes codebases to provide insights into code quality, complexity, dependencies, and maintainability. It generates comprehensive reports with visualizations to help developers understand and improve their code.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **📊 Code Analysis** - Parse and analyze Python files using AST
- **📈 Complexity Metrics** - Calculate cyclomatic complexity, cognitive complexity, and maintainability index
- **🔗 Dependency Extraction** - Map imports and module dependencies
- **🔍 Code Smell Detection** - Identify long methods, large classes, duplicate code, and more
- **📄 Report Generation** - Generate HTML, Markdown, and JSON reports
- **📉 Visualizations** - Create dependency graphs, complexity charts, and metrics summaries
- **🤖 AI Summaries** - Generate AI-powered code explanations (optional)

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/codebase-archaeologist.git
   cd codebase-archaeologist
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 Usage

### Command Line Interface

```bash
# Analyze a local directory
python cli.py /path/to/your/codebase

# Analyze with custom output directory
python cli.py /path/to/codebase -o ./my_analysis

# Analyze a GitHub repository
python cli.py https://github.com/user/repo

# Enable AI summaries (requires API key in config.yaml)
python cli.py /path/to/codebase --ai-summary

# Generate only specific outputs
python cli.py /path/to/codebase --no-viz  # Skip visualizations
```

### Streamlit Web Interface

```bash
streamlit run web/streamlit_app.py
```

---

## 📁 Project Structure

```
codebase-archaeologist/
├── cli.py                 # Command-line interface
├── main.py                # Main orchestrator
├── config.yaml            # Configuration file
├── requirements.txt       # Python dependencies
├── src/
│   ├── ai_engine/         # AI-powered code summarization
│   ├── analysis/          # AST parsing & complexity analysis
│   ├── extraction/        # Dependency & code smell detection
│   ├── ingestion/         # Code loading & file filtering
│   ├── reporting/         # HTML & Markdown report generation
│   ├── utils/             # Helpers & logging
│   └── visualization/     # Charts & graph generation
├── web/                   # Streamlit web application
├── tests/                 # Unit tests
├── docs/                  # Documentation
└── outputs/               # Generated reports (gitignored)
```

---

## 📊 Output Reports

After analysis, you'll find the following in your output directory:

| File | Description |
|------|-------------|
| `analysis_results.json` | Raw analysis data in JSON format |
| `analysis_report.md` | Human-readable Markdown report |
| `analysis_report.html` | Interactive HTML report |
| `dependency_graph.png` | Visual dependency graph |
| `complexity_chart.png` | Complexity metrics chart |
| `metrics_summary.png` | Overall metrics summary |

---

## ⚙️ Configuration

Edit `config.yaml` to customize analysis settings:

```yaml
analysis:
  max_file_size: 1048576          # Max file size (1MB)
  exclude_patterns:
    - "**/test_*"
    - "**/__pycache__/**"

thresholds:
  complexity:
    low: 5
    medium: 10
    high: 20
  maintainability:
    good: 20
    moderate: 10

ai:
  enabled: false
  provider: "ollama"              # or "openai"
  model: "codellama"
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

---

## 📈 Metrics Explained

| Metric | Description | Good | Moderate | Poor |
|--------|-------------|------|----------|------|
| **Cyclomatic Complexity** | Number of independent paths | ≤5 | 6-10 | >10 |
| **Maintainability Index** | Code maintainability score | ≥20 | 10-19 | <10 |
| **Cognitive Complexity** | Mental effort to understand | ≤15 | 16-30 | >30 |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with Python and love for clean code
- Inspired by the need to understand legacy codebases
- Uses matplotlib, networkx, and other amazing open-source libraries

---

<p align="center">
  Made with ❤️ for developers who inherit legacy code
</p>



# 🏛️ Codebase Archaeologist

**AI-Powered Legacy Code Analysis & Documentation System**

A comprehensive tool that automatically analyzes, explains, and documents unfamiliar codebases using AI and static analysis.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Modules](#modules)
- [Configuration](#configuration)
- [Sample Output](#sample-output)
- [Technology Stack](#technology-stack)
- [Future Enhancements](#future-enhancements)
- [Viva Questions](#viva-questions)
- [Contributing](#contributing)

---

## 🎯 Overview

**Codebase Archaeologist** is a final-year AI/ML project that helps developers understand legacy or unfamiliar codebases. It combines:

- **Static Code Analysis** (AST parsing, metrics)
- **AI-Powered Explanations** (Natural language generation)
- **Dependency Visualization** (Graph generation)
- **Code Quality Detection** (Smells, complexity)
- **Automated Documentation** (Markdown/HTML reports)

### Problem Statement

Understanding large, undocumented codebases is time-consuming. This tool automates the process by:
1. Parsing source code structure
2. Generating human-readable explanations
3. Detecting quality issues
4. Visualizing dependencies
5. Creating comprehensive documentation

---

## ✨ Features

### Core Features

✅ **Multi-Language Support** (Python, with extensibility to JS, Java)  
✅ **AST-Based Parsing** (Functions, classes, imports)  
✅ **AI Code Summarization** (Natural language explanations)  
✅ **Complexity Analysis** (Cyclomatic complexity, maintainability index)  
✅ **Code Smell Detection** (Long functions, magic numbers, duplicates)  
✅ **Dependency Graphs** (File and function relationships)  
✅ **Dead Code Detection** (Unused functions)  
✅ **Automated Documentation** (Markdown/HTML reports)  
✅ **GitHub Integration** (Clone and analyze remote repositories)  
✅ **Web Dashboard** (Optional Streamlit interface)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│        CODEBASE ARCHAEOLOGIST           │
│          (Main Orchestrator)            │
└─────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌────────┐   ┌──────────┐   ┌──────────┐
│Ingestion│   │ Analysis │   │Extraction│
│ Module  │   │  Module  │   │  Module  │
└────────┘   └──────────┘   └──────────┘
    │              │              │
    └──────────────┼──────────────┘
                   ▼
        ┌──────────────────────┐
        │   AI Engine Module   │
        └──────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌──────────────┐    ┌──────────────┐
│Visualization │    │   Reporting  │
│   Module     │    │    Module    │
└──────────────┘    └──────────────┘
```

### Module Responsibilities

1. **Ingestion**: Load local/GitHub repositories
2. **Analysis**: Parse AST, calculate metrics
3. **Extraction**: Dependencies, call graphs, smells
4. **AI Engine**: Generate natural language summaries
5. **Visualization**: Create dependency graphs
6. **Reporting**: Generate documentation

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip
- Git (for GitHub integration)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/codebase-archaeologist.git
cd codebase-archaeologist
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Graphviz (For Visualizations)

**Ubuntu/Debian:**
```bash
sudo apt-get install graphviz
```

**macOS:**
```bash
brew install graphviz
```

**Windows:**
Download from [graphviz.org](https://graphviz.org/download/)

---

## 💻 Usage

### Command Line Interface

#### Analyze Local Codebase

```bash
python main.py /path/to/your/codebase
```

#### Analyze GitHub Repository

```bash
python main.py https://github.com/username/repo.git
```

#### With Custom Configuration

```bash
python main.py /path/to/code --config custom_config.yaml
```

### Python API

```python
from main import CodebaseArchaeologist

# Initialize
archaeologist = CodebaseArchaeologist('config.yaml')

# Analyze local codebase
results = archaeologist.analyze_local('./my_project')

# Analyze GitHub repo
results = archaeologist.analyze_github('https://github.com/user/repo.git')

# Access results
print(results['summary'])
```

### Web Dashboard (Optional)

```bash
streamlit run web/streamlit_app.py
```

Then open `http://localhost:8501` in your browser.

---

## 📁 Project Structure

```
codebase_archaeologist/
│
├── README.md                          # This file
├── requirements.txt                   # Dependencies
├── config.yaml                        # Configuration
├── main.py                           # Entry point
│
├── src/
│   ├── ingestion/
│   │   └── code_loader.py            # Load repositories
│   ├── analysis/
│   │   ├── ast_parser.py             # AST parsing
│   │   └── complexity_analyzer.py    # Metrics calculation
│   ├── extraction/
│   │   ├── dependency_extractor.py   # Dependency graphs
│   │   └── code_smell_detector.py    # Quality detection
│   ├── ai_engine/
│   │   └── code_summarizer.py        # AI summaries
│   ├── visualization/
│   │   └── graph_generator.py        # Graph creation
│   ├── reporting/
│   │   └── markdown_generator.py     # Report generation
│   └── utils/
│       ├── logger.py                 # Logging
│       └── helpers.py                # Utilities
│
├── tests/
│   └── sample_repo/                  # Test codebase
│       └── calculator.py
│
└── outputs/                          # Generated reports
    ├── reports/
    ├── graphs/
    └── visualizations/
```

---

## 🧩 Modules

### 1. Code Ingestion Module

**Purpose**: Load codebase from local directory or GitHub

**Features**:
- Recursive directory scanning
- File filtering (extensions, size limits)
- Binary file exclusion
- GitHub cloning

**Key Class**: `CodeLoader`

### 2. AST Parser Module

**Purpose**: Parse Python code using Abstract Syntax Trees

**Extracts**:
- Functions (parameters, returns, docstrings)
- Classes (methods, inheritance)
- Imports (modules, dependencies)
- Global variables

**Key Class**: `ASTParser`

### 3. Complexity Analyzer Module

**Purpose**: Calculate code quality metrics

**Metrics**:
- Cyclomatic Complexity
- Maintainability Index
- Halstead Metrics
- Lines of Code (LOC, SLOC)

**Key Class**: `ComplexityAnalyzer`

**Uses**: [Radon](https://radon.readthedocs.io/) library

### 4. Code Smell Detector Module

**Purpose**: Identify code quality issues

**Detects**:
- Long functions/classes
- Missing docstrings
- Too many parameters
- Magic numbers
- Dead code
- Duplicate code
- Global variables

**Key Class**: `CodeSmellDetector`

### 5. Dependency Extractor Module

**Purpose**: Analyze file and function dependencies

**Generates**:
- Dependency graphs (NetworkX)
- Circular dependency detection
- Most depended-upon files
- Isolated files

**Key Class**: `DependencyExtractor`

### 6. AI Code Summarizer Module

**Purpose**: Generate natural language explanations

**Generates**:
- Function summaries
- Class descriptions
- File overviews
- Purpose inference

**Implementation**:
- Rule-based (current)
- Extensible to Transformers/GPT models

**Key Class**: `CodeSummarizer`

### 7. Main Orchestrator

**Purpose**: Coordinate all modules

**Workflow**:
1. Load codebase
2. Parse files
3. Analyze complexity
4. Extract dependencies
5. Detect smells
6. Generate AI summaries
7. Create reports

**Key Class**: `CodebaseArchaeologist`

---

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
analysis:
  supported_languages: [python]
  max_file_size_mb: 10
  exclude_dirs: [__pycache__, .git, venv]

quality:
  max_complexity: 10
  max_function_length: 50

ai:
  model_name: "microsoft/codebert-base"
  use_local_model: false

output:
  base_dir: "./outputs"
  report_format: "markdown"
```

---

## 📊 Sample Output

### Terminal Output

```
🏛️  Codebase Archaeologist initialized
📂 Starting analysis of: ./my_project
📊 Parsing and analyzing files...
Analyzing files: 100%|████████| 25/25 [00:05<00:00, 4.8it/s]
🔗 Extracting dependencies...
🔍 Detecting code smells and duplicates...
📈 Calculating repository metrics...
✅ Analysis complete in 5.23s

============================================================
📊 ANALYSIS SUMMARY
============================================================
Total Files: 25
Total Functions: 142
Total Classes: 18
Total Lines: 3,458
Code Smells: 23
Avg Complexity: 4.2
Maintainability: 68.5
============================================================
```

### Generated Files

```
outputs/
├── reports/
│   └── analysis_results.json       # Complete analysis data
├── graphs/
│   └── dependency_graph.png        # Visual dependency graph
└── visualizations/
    └── complexity_heatmap.png      # Complexity visualization
```

### Sample JSON Output

```json
{
  "metadata": {
    "source": "./my_project",
    "analyzed_at": "2026-01-03 10:30:00",
    "total_files": 25,
    "analysis_time_seconds": 5.23
  },
  "summary": {
    "total_functions": 142,
    "total_classes": 18,
    "total_lines_of_code": 3458,
    "total_code_smells": 23,
    "average_complexity": 4.2,
    "average_maintainability": 68.5
  },
  "files": [...]
}
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.8+ |
| AST Parsing | `ast` module |
| Metrics | Radon, Pylint |
| AI/ML | Hugging Face Transformers (extensible) |
| Graphs | NetworkX, Graphviz |
| Visualization | Matplotlib, Plotly |
| CLI | argparse |
| Web UI | Streamlit |
| Version Control | GitPython |
| Testing | pytest |

---

## 🔮 Future Enhancements

### Short-term
- [ ] HTML report generation
- [ ] Interactive web dashboard
- [ ] Support for JavaScript/TypeScript
- [ ] Real-time analysis mode

### Medium-term
- [ ] Integration with CodeBERT/GPT models
- [ ] Code suggestion engine
- [ ] Refactoring recommendations
- [ ] IDE plugins (VS Code, PyCharm)

### Long-term
- [ ] Multi-repository comparison
- [ ] Team collaboration features
- [ ] CI/CD integration
- [ ] Machine learning for smell prediction
- [ ] Automated refactoring tools

---

## 🎓 Viva Questions & Answers

### Technical Questions

**Q1: How does AST parsing work?**

**A**: AST (Abstract Syntax Tree) parsing converts source code into a tree structure. Python's `ast` module parses code, creating nodes for functions, classes, statements. We traverse this tree to extract metadata like function names, parameters, and call relationships.

**Q2: What is cyclomatic complexity?**

**A**: Cyclomatic complexity measures code complexity by counting independent paths through code. Higher values indicate more complex, harder-to-test code. Formula: `M = E - N + 2P` where E=edges, N=nodes, P=connected components.

**Q3: How do you detect dead code?**

**A**: We track function calls within files. Functions never called (and not entry points like `main`) are flagged as potentially dead. Note: This is file-scoped; true dead code detection requires whole-program analysis.

**Q4: Explain the dependency extraction algorithm**

**A**: 
1. Parse `import` statements from AST
2. Map imports to actual files
3. Build directed graph (NetworkX)
4. Detect cycles using graph algorithms
5. Calculate centrality metrics

**Q5: Why rule-based AI instead of deep learning?**

**A**: For prototyping, rule-based is:
- Faster (no model loading)
- More interpretable
- Lightweight (no GPU needed)

Production version would use CodeBERT or GPT for better summaries.

### Project-Specific Questions

**Q6: What makes this project unique?**

**A**: Combines static analysis, AI summarization, and visualization in one tool. Most tools do one aspect; we provide end-to-end codebase understanding.

**Q7: What challenges did you face?**

**A**: 
- Handling syntax errors in legacy code
- Balancing analysis depth vs. speed
- Generating meaningful summaries without ML models
- Cross-file dependency resolution

**Q8: How is this useful in industry?**

**A**: 
- Onboarding new developers
- Legacy system modernization
- Code review automation
- Technical debt assessment
- Documentation generation

### Implementation Questions

**Q9: Why NetworkX for graphs?**

**A**: NetworkX provides:
- Graph algorithms (cycle detection, centrality)
- Easy serialization
- Visualization integration
- Academic-friendly API

**Q10: How do you ensure scalability?**

**A**: 
- Stream processing (don't load all files in memory)
- Configurable file size limits
- Parallel processing capability (future)
- Incremental analysis (future)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👥 Authors

- Your Name - *Initial work* - [YourGitHub](https://github.com/yourusername)

---

## 🙏 Acknowledgments

- Radon library for complexity metrics
- NetworkX for graph algorithms
- Anthropic's Claude for documentation assistance
- Open source community

---

## 📞 Contact

- Email: your.email@example.com
- Project Link: [https://github.com/yourusername/codebase-archaeologist](https://github.com/yourusername/codebase-archaeologist)

---

**⭐ If you found this project helpful, please give it a star!**