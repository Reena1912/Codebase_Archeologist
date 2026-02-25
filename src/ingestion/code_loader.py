"""
Code Ingestion Module
Loads codebase from local directory or GitHub repository
"""

import os
import re
import stat
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import List, Dict, Optional
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
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
        
        # Validate and normalize the GitHub URL
        repo_url = self._normalize_github_url(repo_url)
        
        # Clean up existing directory
        local_path = self._ensure_clean_dir(local_path)
        
        try:
            # First check if git is available
            self._check_git_available()
            
            # Clone repository with explicit configuration
            logger.info("Starting repository clone (this may take a moment)...")
            
            # Use subprocess for better error handling
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, local_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                raise GitCommandError('clone', error_msg)
            
            logger.info("Repository cloned successfully")
            
            # Load files
            result = self.load_from_local(local_path)
            result['type'] = 'github'
            result['repo_url'] = repo_url
            
            return result
            
        except subprocess.TimeoutExpired:
            logger.error("Repository clone timed out. The repository may be too large or network is slow.")
            raise RuntimeError("Clone operation timed out after 5 minutes")
            
        except FileNotFoundError:
            logger.error("Git is not installed or not in PATH")
            raise RuntimeError(
                "Git is not installed or not found in PATH.\n"
                "Please install Git from https://git-scm.com/downloads and ensure it's in your PATH."
            )
            
        except GitCommandError as e:
            error_str = str(e).lower()
            
            if 'authentication' in error_str or 'access denied' in error_str or 'permission denied' in error_str:
                logger.error("Authentication failed - repository may be private")
                raise RuntimeError(
                    f"Access denied to repository: {repo_url}\n\n"
                    "This could be because:\n"
                    "1. The repository is private and requires authentication\n"
                    "2. The repository URL is incorrect\n"
                    "3. Your Git credentials are not configured\n\n"
                    "For private repos, try:\n"
                    "- Use SSH URL: git@github.com:username/repo.git\n"
                    "- Or configure Git credentials: git config --global credential.helper store"
                )
            elif 'not found' in error_str or 'does not exist' in error_str or 'repository not found' in error_str:
                logger.error("Repository not found")
                raise RuntimeError(
                    f"Repository not found: {repo_url}\n\n"
                    "Please check:\n"
                    "1. The repository URL is correct\n"
                    "2. The repository exists and is accessible\n"
                    "3. If private, ensure you have access permissions"
                )
            elif 'could not resolve host' in error_str or 'unable to access' in error_str:
                logger.error("Network error - cannot reach GitHub")
                raise RuntimeError(
                    f"Cannot connect to GitHub: {repo_url}\n\n"
                    "Please check:\n"
                    "1. Your internet connection\n"
                    "2. GitHub.com is accessible\n"
                    "3. No firewall/proxy is blocking the connection"
                )
            else:
                logger.error(f"Failed to clone repository: {e}")
                raise RuntimeError(f"Failed to clone repository: {e}")
    
    @staticmethod
    def _force_rmtree(path: str) -> None:
        """Remove a directory tree, handling read-only .git files on Windows."""
        def _on_rm_error(_func, _path, _exc_info):
            # Clear the read-only flag and retry
            try:
                os.chmod(_path, stat.S_IWRITE)
                os.unlink(_path)
            except Exception:
                pass

        shutil.rmtree(path, onerror=_on_rm_error)

    def _ensure_clean_dir(self, local_path: str) -> str:
        """
        Make sure the target directory does not exist before cloning.
        Falls back to alternative names if deletion is impossible.
        """
        if not Path(local_path).exists():
            return local_path

        # Try force-removing (handles read-only .git objects)
        try:
            self._force_rmtree(local_path)
            logger.info(f"Cleaned up existing directory: {local_path}")
            return local_path
        except Exception as e:
            logger.warning(f"Cannot remove {local_path}: {e}")

        # Try PID-based alternative
        alt_path = f"./temp_repo_{os.getpid()}"
        if Path(alt_path).exists():
            try:
                self._force_rmtree(alt_path)
                logger.info(f"Cleaned up existing directory: {alt_path}")
                return alt_path
            except Exception as e2:
                logger.warning(f"Cannot remove {alt_path}: {e2}")
        else:
            return alt_path

        # Last resort: unique name guaranteed not to exist
        unique_path = f"./temp_repo_{uuid.uuid4().hex[:8]}"
        logger.info(f"Using unique temp path: {unique_path}")
        return unique_path

    def _normalize_github_url(self, url: str) -> str:
        """
        Normalize GitHub URL to ensure it's valid for cloning
        
        Args:
            url: Raw GitHub URL
            
        Returns:
            Normalized URL ready for cloning
        """
        url = url.strip()
        
        # Handle common URL patterns
        # Pattern 1: https://github.com/user/repo (missing .git)
        # Pattern 2: https://github.com/user/repo.git (correct)
        # Pattern 3: github.com/user/repo (missing https://)
        # Pattern 4: https://github.com/user/repo/tree/branch (has branch path)
        # Pattern 5: git@github.com:user/repo.git (SSH - keep as is)
        
        # If SSH URL, return as is
        if url.startswith('git@'):
            return url
        
        # Remove trailing slashes
        url = url.rstrip('/')
        
        # Add https:// if missing
        if url.startswith('github.com'):
            url = 'https://' + url
        
        # Remove tree/branch paths (e.g., /tree/main, /tree/master, /tree/branch-name)
        url = re.sub(r'/tree/[^/]+.*$', '', url)
        
        # Remove blob paths (e.g., /blob/main/file.py)
        url = re.sub(r'/blob/[^/]+.*$', '', url)
        
        # Remove /pulls, /issues, /actions etc.
        url = re.sub(r'/(pulls|issues|actions|wiki|projects|releases|tags|commits).*$', '', url)
        
        # Add .git if missing (for HTTPS URLs)
        if url.startswith('https://') and not url.endswith('.git'):
            url = url + '.git'
        
        logger.debug(f"Normalized URL: {url}")
        return url
    
    def _check_git_available(self) -> None:
        """Check if Git is installed and accessible"""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.debug(f"Git found: {result.stdout.strip()}")
            else:
                raise FileNotFoundError("Git not found")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            raise FileNotFoundError("Git is not installed or not in PATH")
    
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