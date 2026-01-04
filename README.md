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
