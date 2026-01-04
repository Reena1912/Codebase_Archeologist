"""
Codebase Archaeologist - AI-Powered Code Analysis System

A comprehensive tool for analyzing legacy codebases:
- Static analysis using AST
- Complexity metrics calculation
- Code smell detection
- Dependency extraction
- AI-powered documentation generation
"""

__version__ = "1.0.0"
__author__ = "Codebase Archaeologist Team"

from src.analysis.ast_parser import ASTParser
from src.analysis.complexity_analyzer import ComplexityAnalyzer
from src.analysis.metrics_calculator import MetricsCalculator
from src.ingestion.code_loader import CodeLoader
from src.extraction.dependency_extractor import DependencyExtractor
from src.extraction.code_smell_detector import CodeSmellDetector
from src.ai_engine.code_summarizer import CodeSummarizer

__all__ = [
    'ASTParser',
    'ComplexityAnalyzer',
    'MetricsCalculator',
    'CodeLoader',
    'DependencyExtractor',
    'CodeSmellDetector',
    'CodeSummarizer'
]
