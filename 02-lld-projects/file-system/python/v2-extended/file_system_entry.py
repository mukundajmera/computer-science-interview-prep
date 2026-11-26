"""
File System - V1 Basic

Abstract base class for file system entries using Composite pattern.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class FileSystemEntry(ABC):
    """Abstract base class for file system entries."""
    
    def __init__(self, name: str):
        self._validate_name(name)
        self._name = name
        self._parent: Optional['Directory'] = None
        self._created_at = datetime.now()
        self._modified_at = datetime.now()
    
    def _validate_name(self, name: str) -> None:
        if not name:
            raise ValueError("Name cannot be null or empty")
        if '/' in name or '\\' in name:
            raise ValueError("Name cannot contain path separators")
    
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._validate_name(value)
        self._name = value
        self._update_modified()
    
    @property
    def parent(self) -> Optional['Directory']:
        return self._parent
    
    def _set_parent(self, parent: Optional['Directory']) -> None:
        self._parent = parent
    
    @property
    def path(self) -> str:
        if self._parent is None:
            return "/" + self._name
        parent_path = self._parent.path
        if parent_path == "/":
            return "/" + self._name
        return parent_path + "/" + self._name
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def modified_at(self) -> datetime:
        return self._modified_at
    
    def _update_modified(self) -> None:
        self._modified_at = datetime.now()
    
    @abstractmethod
    def get_size(self) -> int:
        pass
    
    @abstractmethod
    def is_file(self) -> bool:
        pass
    
    @abstractmethod
    def is_directory(self) -> bool:
        pass
    
    def delete(self) -> bool:
        """Delete this entry from its parent."""
        if self._parent is not None:
            return self._parent.remove_entry(self._name)
        return False
    
    def __str__(self) -> str:
        prefix = "[D] " if self.is_directory() else "[F] "
        return prefix + self._name
