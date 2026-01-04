"""
Helper utilities for Codebase Archaeologist
Common functions used across modules
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any
import yaml

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return get_default_config()

def get_default_config() -> Dict[str, Any]:
    """Return default configuration if file not found"""
    return {
        'analysis': {
            'supported_languages': ['python'],
            'max_file_size_mb': 10,
            'exclude_dirs': ['__pycache__', '.git', 'venv'],
            'exclude_extensions': ['.pyc', '.pyo']
        },
        'ai': {
            'model_name': 'microsoft/codebert-base',
            'max_token_length': 512
        },
        'quality': {
            'max_complexity': 10,
            'max_function_length': 50
        },
        'output': {
            'base_dir': './outputs',
            'report_format': 'markdown'
        }
    }

def get_file_hash(filepath: str) -> str:
    """Generate MD5 hash of file content"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return ""

def count_lines(filepath: str) -> int:
    """Count lines in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except:
        return 0

def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def create_output_dir(base_dir: str = "./outputs") -> Path:
    """Create output directory structure"""
    output_path = Path(base_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (output_path / "reports").mkdir(exist_ok=True)
    (output_path / "graphs").mkdir(exist_ok=True)
    (output_path / "visualizations").mkdir(exist_ok=True)
    
    return output_path

def format_bytes(bytes_size: int) -> str:
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def is_binary_file(filepath: str) -> bool:
    """Check if file is binary"""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except:
        return True

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."