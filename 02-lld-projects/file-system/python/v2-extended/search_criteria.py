"""
File System - V2 Extended

SearchCriteria class for flexible file searching.
"""
import re
from typing import Optional


class SearchCriteria:
    """Criteria for searching file system entries."""
    
    def __init__(self):
        self._name_pattern: Optional[str] = None
        self._extension: Optional[str] = None
        self._min_size: Optional[int] = None
        self._max_size: Optional[int] = None
        self._files_only: bool = False
        self._directories_only: bool = False
    
    def with_name(self, pattern: str) -> 'SearchCriteria':
        """Set name pattern to match."""
        self._name_pattern = pattern
        return self
    
    def with_extension(self, ext: str) -> 'SearchCriteria':
        """Set file extension to match."""
        self._extension = ext
        return self
    
    def with_min_size(self, min_size: int) -> 'SearchCriteria':
        """Set minimum size filter."""
        self._min_size = min_size
        return self
    
    def with_max_size(self, max_size: int) -> 'SearchCriteria':
        """Set maximum size filter."""
        self._max_size = max_size
        return self
    
    def with_size_range(self, min_size: int, max_size: int) -> 'SearchCriteria':
        """Set size range filter."""
        self._min_size = min_size
        self._max_size = max_size
        return self
    
    def files_only(self) -> 'SearchCriteria':
        """Only match files."""
        self._files_only = True
        self._directories_only = False
        return self
    
    def directories_only(self) -> 'SearchCriteria':
        """Only match directories."""
        self._directories_only = True
        self._files_only = False
        return self
    
    def matches(self, entry) -> bool:
        """Check if an entry matches all specified criteria."""
        # Type check
        if self._files_only and not entry.is_file():
            return False
        if self._directories_only and not entry.is_directory():
            return False
        
        # Name pattern check
        if self._name_pattern and not self._matches_pattern(entry.name, self._name_pattern):
            return False
        
        # Extension check (only for files)
        if self._extension:
            if not entry.is_file():
                return False
            if entry.get_extension().lower() != self._extension.lower():
                return False
        
        # Size checks
        size = entry.get_size()
        if self._min_size is not None and size < self._min_size:
            return False
        if self._max_size is not None and size > self._max_size:
            return False
        
        return True
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        """Simple pattern matching with * wildcard."""
        regex = pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
        return bool(re.match(f"^{regex}$", name))
    
    def __str__(self) -> str:
        parts = []
        if self._name_pattern:
            parts.append(f"name={self._name_pattern}")
        if self._extension:
            parts.append(f"ext={self._extension}")
        if self._min_size is not None:
            parts.append(f"min_size={self._min_size}")
        if self._max_size is not None:
            parts.append(f"max_size={self._max_size}")
        if self._files_only:
            parts.append("files_only")
        if self._directories_only:
            parts.append("directories_only")
        return f"SearchCriteria({', '.join(parts)})"
