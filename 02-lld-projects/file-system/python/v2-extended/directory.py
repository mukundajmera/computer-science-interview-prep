"""
File System - V1 Basic

Directory class (Composite Composite) - contains files and subdirectories.
"""
from typing import Dict, List, Optional
from file_system_entry import FileSystemEntry


class Directory(FileSystemEntry):
    """Directory class representing a composite in the composite pattern."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._children: Dict[str, FileSystemEntry] = {}
    
    def add_entry(self, entry: FileSystemEntry) -> bool:
        """Add an entry to this directory."""
        if entry is None:
            raise ValueError("Entry cannot be None")
        if entry.name in self._children:
            return False
        
        # Remove from old parent if exists
        if entry.parent is not None:
            entry.parent.remove_entry(entry.name)
        
        self._children[entry.name] = entry
        entry._set_parent(self)
        self._update_modified()
        return True
    
    def remove_entry(self, name: str) -> bool:
        """Remove an entry by name."""
        if name in self._children:
            entry = self._children.pop(name)
            entry._set_parent(None)
            self._update_modified()
            return True
        return False
    
    def get_entry(self, name: str) -> Optional[FileSystemEntry]:
        """Get an entry by name."""
        return self._children.get(name)
    
    def has_entry(self, name: str) -> bool:
        """Check if directory contains an entry with given name."""
        return name in self._children
    
    def list_entries(self) -> List[FileSystemEntry]:
        """List all entries in this directory."""
        return list(self._children.values())
    
    def list_files(self) -> List['File']:
        """List only files in this directory."""
        from file import File
        return [e for e in self._children.values() if e.is_file()]
    
    def list_directories(self) -> List['Directory']:
        """List only subdirectories."""
        return [e for e in self._children.values() if e.is_directory()]
    
    def get_size(self) -> int:
        """Get the total size of this directory (sum of all children)."""
        return sum(entry.get_size() for entry in self._children.values())
    
    def get_child_count(self) -> int:
        """Get the number of direct children."""
        return len(self._children)
    
    def is_empty(self) -> bool:
        """Check if directory is empty."""
        return len(self._children) == 0
    
    def is_file(self) -> bool:
        return False
    
    def is_directory(self) -> bool:
        return True
    
    def delete(self) -> bool:
        """Delete this directory and all its contents recursively."""
        # First delete all children
        for entry in list(self._children.values()):
            if entry.is_directory():
                entry.delete()
            self._children.pop(entry.name, None)
        return super().delete()
    
    def __str__(self) -> str:
        return f"[D] {self._name} ({len(self._children)} items)"
    
    def display_tree(self, indent: str = "") -> None:
        """Display directory tree structure."""
        print(f"{indent}{self}")
        for entry in self._children.values():
            if entry.is_directory():
                entry.display_tree(indent + "  ")
            else:
                print(f"{indent}  {entry}")
