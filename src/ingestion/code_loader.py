"""
Code Ingestion Module
Loads codebase from local directory or GitHub repository
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from git import Repo
from git.exc import GitCommandError
from src.utils.logger import logger
from src.utils.helpers import is_binary_file, format_bytes

class CodeLoader:
    """Load and prepare codebase for analysis"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.exclude_dirs = set(config['analysis'].get('exclude_dirs', []))
        self.exclude_extensions = set(config['analysis'].get('exclude_extensions', []))
        self.max_file_size = config['analysis'].get('max_file_size_mb', 10) * 1024 * 1024
        
    def load_from_local(self, path: str) -> Dict:
        """
        Load codebase from local directory
        
        Args:
            path: Path to local codebase
            
        Returns:
            Dictionary containing file information
        """
        logger.info(f"Loading codebase from: {path}")
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        if not path_obj.is_dir():
            raise ValueError(f"Path is not a directory: {path}")
        
        files = self._scan_directory(path_obj)
        
        logger.info(f"Found {len(files)} files to analyze")
        return {
            'source': path,
            'type': 'local',
            'files': files,
            'total_files': len(files)
        }
    
    def load_from_github(self, repo_url: str, local_path: str = "./temp_repo") -> Dict:
        """
        Clone GitHub repository and load codebase
        
        Args:
            repo_url: GitHub repository URL
            local_path: Temporary path to clone repository
            
        Returns:
            Dictionary containing file information
        """
        logger.info(f"Cloning repository: {repo_url}")
        
        # Clean up existing directory
        if Path(local_path).exists():
            shutil.rmtree(local_path)
        
        try:
            # Clone repository
            Repo.clone_from(repo_url, local_path, depth=1)
            logger.info("Repository cloned successfully")
            
            # Load files
            result = self.load_from_local(local_path)
            result['type'] = 'github'
            result['repo_url'] = repo_url
            
            return result
            
        except GitCommandError as e:
            logger.error(f"Failed to clone repository: {e}")
            raise
    
    def _scan_directory(self, root_path: Path) -> List[Dict]:
        """
        Recursively scan directory and collect file information
        
        Args:
            root_path: Root directory path
            
        Returns:
            List of file dictionaries
        """
        files = []
        
        for item in root_path.rglob('*'):
            # Skip directories
            if item.is_dir():
                continue
            
            # Skip excluded directories
            if any(excluded in item.parts for excluded in self.exclude_dirs):
                continue
            
            # Skip excluded extensions
            if item.suffix in self.exclude_extensions:
                continue
            
            # Skip binary files
            if is_binary_file(str(item)):
                continue
            
            # Check file size
            file_size = item.stat().st_size
            if file_size > self.max_file_size:
                logger.warning(f"Skipping large file: {item} ({format_bytes(file_size)})")
                continue
            
            # Add file info
            try:
                with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                files.append({
                    'path': str(item),
                    'relative_path': str(item.relative_to(root_path)),
                    'name': item.name,
                    'extension': item.suffix,
                    'size': file_size,
                    'lines': content.count('\n') + 1,
                    'content': content
                })
                
            except Exception as e:
                logger.warning(f"Error reading file {item}: {e}")
                continue
        
        return files
    
    def filter_by_language(self, files: List[Dict], language: str = 'python') -> List[Dict]:
        """
        Filter files by programming language
        
        Args:
            files: List of file dictionaries
            language: Programming language to filter
            
        Returns:
            Filtered list of files
        """
        extension_map = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'java': ['.java'],
            'cpp': ['.cpp', '.h', '.hpp'],
            'c': ['.c', '.h']
        }
        
        target_extensions = extension_map.get(language.lower(), ['.py'])
        filtered = [f for f in files if f['extension'] in target_extensions]
        
        logger.info(f"Filtered to {len(filtered)} {language} files")
        return filtered