"""
File System - V1 Basic

File class (Composite Leaf) - stores content and metadata.
"""
from file_system_entry import FileSystemEntry


class File(FileSystemEntry):
    """File class representing a leaf in the composite pattern."""
    
    def __init__(self, name: str, content: str = ""):
        super().__init__(name)
        self._content = content if content else ""
    
    def read(self) -> str:
        """Read the file content."""
        return self._content
    
    def write(self, content: str) -> None:
        """Write content to the file (overwrites existing content)."""
        self._content = content if content else ""
        self._update_modified()
    
    def append(self, content: str) -> None:
        """Append content to the file."""
        if content:
            self._content += content
            self._update_modified()
    
    def get_size(self) -> int:
        """Get the file size (content length)."""
        return len(self._content)
    
    def is_file(self) -> bool:
        return True
    
    def is_directory(self) -> bool:
        return False
    
    def get_extension(self) -> str:
        """Get the file extension (e.g., 'txt' from 'file.txt')."""
        dot_index = self._name.rfind('.')
        if dot_index > 0 and dot_index < len(self._name) - 1:
            return self._name[dot_index + 1:]
        return ""
    
    def __str__(self) -> str:
        return f"[F] {self._name} ({self.get_size()} bytes)"
