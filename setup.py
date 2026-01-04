"""
Setup script for Codebase Archaeologist
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding='utf-8')
else:
    long_description = "AI-Powered Legacy Code Analysis System"

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding='utf-8').strip().split('\n')
    # Filter out comments and empty lines
    requirements = [r.strip() for r in requirements if r.strip() and not r.startswith('#')]
else:
    requirements = []

setup(
    name="codebase-archaeologist",
    version="1.0.0",
    author="Codebase Archaeologist Team",
    author_email="archaeologist@example.com",
    description="AI-Powered Legacy Code Analysis & Documentation System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/codebase-archaeologist",
    
    packages=find_packages(exclude=['tests*', 'docs*']),
    include_package_data=True,
    
    python_requires=">=3.8",
    install_requires=requirements,
    
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'ai': [
            'transformers>=4.30.0',
            'torch>=2.0.0',
            'sentencepiece>=0.1.99',
        ],
        'web': [
            'streamlit>=1.22.0',
            'flask>=2.3.0',
        ],
    },
    
    entry_points={
        'console_scripts': [
            'archaeologist=cli:main',
            'codebase-archaeologist=cli:main',
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Testing",
    ],
    
    keywords=[
        "code-analysis",
        "static-analysis",
        "code-quality",
        "documentation",
        "ast",
        "complexity",
        "legacy-code",
        "refactoring",
        "ai",
        "machine-learning"
    ],
    
    project_urls={
        "Bug Reports": "https://github.com/yourusername/codebase-archaeologist/issues",
        "Source": "https://github.com/yourusername/codebase-archaeologist",
        "Documentation": "https://github.com/yourusername/codebase-archaeologist#readme",
    },
)
