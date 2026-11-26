"""
File System - V3 Optimized

SearchCriteria class (same as v2).
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
        self._name_pattern = pattern
        return self
    
    def with_extension(self, ext: str) -> 'SearchCriteria':
        self._extension = ext
        return self
    
    def with_min_size(self, min_size: int) -> 'SearchCriteria':
        self._min_size = min_size
        return self
    
    def with_max_size(self, max_size: int) -> 'SearchCriteria':
        self._max_size = max_size
        return self
    
    def with_size_range(self, min_size: int, max_size: int) -> 'SearchCriteria':
        self._min_size = min_size
        self._max_size = max_size
        return self
    
    def files_only(self) -> 'SearchCriteria':
        self._files_only = True
        self._directories_only = False
        return self
    
    def directories_only(self) -> 'SearchCriteria':
        self._directories_only = True
        self._files_only = False
        return self
    
    def matches(self, entry) -> bool:
        if self._files_only and not entry.is_file():
            return False
        if self._directories_only and not entry.is_directory():
            return False
        
        if self._name_pattern and not self._matches_pattern(entry.name, self._name_pattern):
            return False
        
        if self._extension:
            if not entry.is_file():
                return False
            if entry.get_extension().lower() != self._extension.lower():
                return False
        
        size = entry.get_size()
        if self._min_size is not None and size < self._min_size:
            return False
        if self._max_size is not None and size > self._max_size:
            return False
        
        return True
    
    def _matches_pattern(self, name: str, pattern: str) -> bool:
        regex = pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
        return bool(re.match(f"^{regex}$", name))
