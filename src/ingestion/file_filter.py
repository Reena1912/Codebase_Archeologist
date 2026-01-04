"""
File Filter Module
Filters and validates files for analysis
"""

from pathlib import Path
from typing import List, Set, Dict
from src.utils.logger import logger

class FileFilter:
    """Filter files based on various criteria"""
    
    def __init__(self, config: Dict):
        """
        Initialize file filter
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.exclude_dirs = set(config['analysis'].get('exclude_dirs', []))
        self.exclude_extensions = set(config['analysis'].get('exclude_extensions', []))
        self.max_file_size = config['analysis'].get('max_file_size_mb', 10) * 1024 * 1024
        self.supported_languages = config['analysis'].get('supported_languages', ['python'])
    
    def should_analyze_file(self, filepath: Path, root_path: Path) -> bool:
        """
        Determine if a file should be analyzed
        
        Args:
            filepath: Path to file
            root_path: Root directory path
            
        Returns:
            True if file should be analyzed, False otherwise
        """
        # Check if it's a file
        if not filepath.is_file():
            return False
        
        # Check excluded directories
        try:
            relative_path = filepath.relative_to(root_path)
            if any(excluded in relative_path.parts for excluded in self.exclude_dirs):
                return False
        except ValueError:
            # filepath is not relative to root_path
            pass
        
        # Check excluded extensions
        if filepath.suffix in self.exclude_extensions:
            return False
        
        # Check file size
        try:
            if filepath.stat().st_size > self.max_file_size:
                logger.warning(f"File too large: {filepath}")
                return False
        except OSError:
            return False
        
        # Check if it's a supported language
        if not self.is_supported_language(filepath):
            return False
        
        return True
    
    def is_supported_language(self, filepath: Path) -> bool:
        """
        Check if file is a supported programming language
        
        Args:
            filepath: Path to file
            
        Returns:
            True if supported, False otherwise
        """
        extension_map = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'cpp': ['.cpp', '.cc', '.cxx', '.h', '.hpp'],
            'c': ['.c', '.h'],
            'go': ['.go'],
            'rust': ['.rs'],
            'ruby': ['.rb'],
            'php': ['.php']
        }
        
        for language in self.supported_languages:
            if filepath.suffix in extension_map.get(language.lower(), []):
                return True
        
        return False
    
    def get_language(self, filepath: Path) -> str:
        """
        Determine the programming language of a file
        
        Args:
            filepath: Path to file
            
        Returns:
            Language name or 'unknown'
        """
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.h': 'c/cpp',
            '.hpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        return extension_map.get(filepath.suffix, 'unknown')
    
    def filter_files(self, files: List[Path], root_path: Path) -> List[Path]:
        """
        Filter a list of files
        
        Args:
            files: List of file paths
            root_path: Root directory path
            
        Returns:
            Filtered list of file paths
        """
        filtered = []
        
        for filepath in files:
            if self.should_analyze_file(filepath, root_path):
                filtered.append(filepath)
        
        logger.info(f"Filtered {len(files)} files to {len(filtered)} files")
        return filtered
    
    def get_file_statistics(self, files: List[Path]) -> Dict:
        """
        Get statistics about filtered files
        
        Args:
            files: List of file paths
            
        Returns:
            Dictionary with file statistics
        """
        stats = {
            'total_files': len(files),
            'by_language': {},
            'total_size': 0,
            'by_extension': {}
        }
        
        for filepath in files:
            # Language count
            language = self.get_language(filepath)
            stats['by_language'][language] = stats['by_language'].get(language, 0) + 1
            
            # Extension count
            ext = filepath.suffix
            stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
            
            # Total size
            try:
                stats['total_size'] += filepath.stat().st_size
            except OSError:
                pass
        
        return stats

# Example usage
if __name__ == "__main__":
    from src.utils.helpers import get_default_config
    
    config = get_default_config()
    filter_obj = FileFilter(config)
    
    # Test with current directory
    test_files = list(Path('.').rglob('*.py'))
    
    print(f"Found {len(test_files)} Python files")
    
    filtered = filter_obj.filter_files(test_files, Path('.'))
    
    print(f"After filtering: {len(filtered)} files")
    
    stats = filter_obj.get_file_statistics(filtered)
    print("\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")