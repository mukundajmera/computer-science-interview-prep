"""
File System - V3 Optimized

Metadata class with enhanced tracking.
"""
from datetime import datetime
import getpass


class Metadata:
    """Metadata for file system entries."""
    
    def __init__(self, owner: str = None, group: str = "users"):
        self._created_at = datetime.now()
        self._modified_at = datetime.now()
        self._accessed_at = datetime.now()
        self._owner = owner or getpass.getuser()
        self._group = group
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def modified_at(self) -> datetime:
        return self._modified_at
    
    @property
    def accessed_at(self) -> datetime:
        return self._accessed_at
    
    @property
    def owner(self) -> str:
        return self._owner
    
    @owner.setter
    def owner(self, value: str) -> None:
        self._owner = value
    
    @property
    def group(self) -> str:
        return self._group
    
    @group.setter
    def group(self, value: str) -> None:
        self._group = value
    
    def update_modified(self) -> None:
        self._modified_at = datetime.now()
    
    def update_accessed(self) -> None:
        self._accessed_at = datetime.now()
    
    def copy(self) -> 'Metadata':
        """Create a copy of this metadata with new timestamps."""
        new_meta = Metadata(self._owner, self._group)
        return new_meta
    
    def __str__(self) -> str:
        return f"Metadata(owner={self._owner}, group={self._group})"
