"""
File System - V2 Extended

Metadata class to track file/directory information.
"""
from datetime import datetime
import getpass


class Metadata:
    """Metadata for file system entries."""
    
    def __init__(self, owner: str = None):
        self._created_at = datetime.now()
        self._modified_at = datetime.now()
        self._accessed_at = datetime.now()
        self._owner = owner or getpass.getuser()
    
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
    
    def update_modified(self) -> None:
        self._modified_at = datetime.now()
    
    def update_accessed(self) -> None:
        self._accessed_at = datetime.now()
    
    def copy(self) -> 'Metadata':
        """Create a copy of this metadata with new timestamps."""
        new_meta = Metadata(self._owner)
        return new_meta
    
    def __str__(self) -> str:
        return f"Metadata(owner={self._owner}, created={self._created_at})"
