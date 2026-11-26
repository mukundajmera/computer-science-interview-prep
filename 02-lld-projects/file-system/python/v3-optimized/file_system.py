"""
File System - V1 Basic

Main FileSystem class implementing Singleton pattern.
Manages root directory and provides path-based operations.
"""
from typing import List, Optional
import fnmatch

from file_system_entry import FileSystemEntry
from file import File
from directory import Directory


class FileSystem:
    """Main file system class using Singleton pattern."""
    
    _instance: Optional['FileSystem'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Create root directory with special path handling
        self._root = _RootDirectory()
        self._current_directory = self._root
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'FileSystem':
        """Get the singleton instance."""
        return cls()
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton (for testing only)."""
        cls._instance = None
    
    @property
    def root(self) -> Directory:
        return self._root
    
    @property
    def current_directory(self) -> Directory:
        return self._current_directory
    
    def change_directory(self, path: str) -> bool:
        """Change current directory."""
        entry = self.resolve_path(path)
        if entry is not None and entry.is_directory():
            self._current_directory = entry
            return True
        return False
    
    def create_file(self, path: str, content: str = "") -> Optional[File]:
        """Create a file at the given path."""
        if not path:
            raise ValueError("Path cannot be null or empty")
        
        parent_path, file_name = self._parse_path(path)
        parent = self._get_or_create_directory(parent_path)
        
        if parent is None:
            print(f"Cannot create parent directory: {parent_path}")
            return None
        
        if parent.has_entry(file_name):
            print(f"Entry already exists: {file_name}")
            return None
        
        file = File(file_name, content)
        parent.add_entry(file)
        return file
    
    def create_directory(self, path: str) -> Optional[Directory]:
        """Create a directory at the given path."""
        if not path or path == "/":
            raise ValueError("Invalid path")
        
        parent_path, dir_name = self._parse_path(path)
        parent = self._get_or_create_directory(parent_path)
        
        if parent is None:
            print(f"Cannot create parent directory: {parent_path}")
            return None
        
        if parent.has_entry(dir_name):
            existing = parent.get_entry(dir_name)
            if existing.is_directory():
                return existing
            print(f"File exists with same name: {dir_name}")
            return None
        
        directory = Directory(dir_name)
        parent.add_entry(directory)
        return directory
    
    def _get_or_create_directory(self, path: str) -> Optional[Directory]:
        """Get or create directory at path (like mkdir -p)."""
        if not path or path == "/":
            return self._root
        
        components = self._get_path_components(path)
        current = self._root
        
        for component in components:
            if not component:
                continue
            
            entry = current.get_entry(component)
            if entry is None:
                new_dir = Directory(component)
                current.add_entry(new_dir)
                current = new_dir
            elif entry.is_directory():
                current = entry
            else:
                return None
        
        return current
    
    def delete(self, path: str) -> bool:
        """Delete entry at path."""
        if not path or path == "/":
            print("Cannot delete root directory")
            return False
        
        entry = self.resolve_path(path)
        if entry is None:
            print(f"Path not found: {path}")
            return False
        
        return entry.delete()
    
    def list(self, path: str) -> List[FileSystemEntry]:
        """List contents of directory at path."""
        entry = self.resolve_path(path)
        if entry is None:
            print(f"Path not found: {path}")
            return []
        if not entry.is_directory():
            return [entry]
        return entry.list_entries()
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content."""
        entry = self.resolve_path(path)
        if entry is None:
            print(f"File not found: {path}")
            return None
        if not entry.is_file():
            print(f"Not a file: {path}")
            return None
        return entry.read()
    
    def write_file(self, path: str, content: str) -> bool:
        """Write content to file."""
        entry = self.resolve_path(path)
        if entry is None:
            file = self.create_file(path, content)
            return file is not None
        if not entry.is_file():
            print(f"Not a file: {path}")
            return False
        entry.write(content)
        return True
    
    def resolve_path(self, path: str) -> Optional[FileSystemEntry]:
        """Resolve a path to a FileSystemEntry."""
        if not path:
            return self._current_directory
        
        start = self._root if path.startswith("/") else self._current_directory
        
        if path == "/":
            return self._root
        
        components = self._get_path_components(path)
        current = start
        
        for component in components:
            if not component or component == ".":
                continue
            
            if component == "..":
                if current.parent is not None:
                    current = current.parent
                continue
            
            if not current.is_directory():
                return None
            
            next_entry = current.get_entry(component)
            if next_entry is None:
                return None
            current = next_entry
        
        return current
    
    def exists(self, path: str) -> bool:
        """Check if path exists."""
        return self.resolve_path(path) is not None

    def copy(self, source_path: str, destination_path: str) -> bool:
        """Copy a file or directory to destination path."""
        source = self.resolve_path(source_path)
        if source is None or not destination_path:
            return False

        source_abs = source.path
        destination_abs = self._normalize_path(destination_path)
        if source.is_directory() and (
            destination_abs == source_abs or destination_abs.startswith(source_abs + "/")
        ):
            return False

        dest_parent_path, dest_name = self._parse_path(destination_path)
        dest_parent = self._get_or_create_directory(dest_parent_path)
        if dest_parent is None or not dest_name or dest_parent.has_entry(dest_name):
            return False

        self._copy_entry(source, dest_parent, dest_name)
        return True

    def move(self, source_path: str, destination_path: str) -> bool:
        """Move a file or directory to destination path."""
        if not self.copy(source_path, destination_path):
            return False
        return self.delete(source_path)

    def find_by_extension(self, start_path: str, extension: str) -> List[File]:
        """Find files recursively by extension."""
        root = self.resolve_path(start_path)
        if root is None:
            return []
        ext = extension.lstrip(".").lower()
        matches: List[File] = []

        def walk(entry: FileSystemEntry) -> None:
            if entry.is_file():
                file_entry = entry
                if file_entry.get_extension().lower() == ext:
                    matches.append(file_entry)
                return
            for child in entry.list_entries():
                walk(child)

        walk(root)
        return matches

    def find_by_name(self, start_path: str, pattern: str) -> List[FileSystemEntry]:
        """Find files/directories recursively by glob-style name pattern."""
        root = self.resolve_path(start_path)
        if root is None:
            return []
        matches: List[FileSystemEntry] = []

        def walk(entry: FileSystemEntry) -> None:
            if fnmatch.fnmatch(entry.name, pattern):
                matches.append(entry)
            if entry.is_directory():
                for child in entry.list_entries():
                    walk(child)

        if root.path != "/":
            walk(root)
        else:
            for child in root.list_entries():
                walk(child)
        return matches
    
    def _parse_path(self, path: str) -> tuple:
        """Parse path into parent path and entry name."""
        if path.endswith("/") and len(path) > 1:
            path = path[:-1]
        
        last_slash = path.rfind("/")
        
        if last_slash == -1:
            return ("", path)
        elif last_slash == 0:
            return ("/", path[1:])
        else:
            return (path[:last_slash], path[last_slash + 1:])
    
    def _get_path_components(self, path: str) -> List[str]:
        """Split path into components."""
        if path.startswith("/"):
            path = path[1:]
        if path.endswith("/"):
            path = path[:-1]
        if not path:
            return []
        return path.split("/")

    def _normalize_path(self, path: str) -> str:
        """Return normalized absolute path for cycle prevention checks."""
        if path.startswith("/"):
            base_components = []
        else:
            base_components = self._get_path_components(self._current_directory.path)
        for component in self._get_path_components(path):
            if component in ("", "."):
                continue
            if component == "..":
                if base_components:
                    base_components.pop()
                continue
            base_components.append(component)
        return "/" + "/".join(base_components) if base_components else "/"

    def _copy_entry(self, source: FileSystemEntry, parent: Directory, name: str) -> None:
        """Deep copy helper for file and directory entries."""
        if source.is_file():
            parent.add_entry(File(name, source.read()))
            return
        copied_dir = Directory(name)
        parent.add_entry(copied_dir)
        for child in source.list_entries():
            self._copy_entry(child, copied_dir, child.name)
    
    def display_tree(self) -> None:
        """Display the file system tree."""
        print("/")
        for entry in self._root.list_entries():
            if entry.is_directory():
                entry.display_tree("  ")
            else:
                print(f"  {entry}")


class _RootDirectory(Directory):
    """Special root directory with path='/'."""
    
    def __init__(self):
        # Root is the only directory allowed to have an empty logical name.
        # Bypass FileSystemEntry name validation while keeping base fields aligned.
        from datetime import datetime
        now = datetime.now()
        self._name = ""
        self._parent = None
        self._created_at = now
        self._modified_at = now
        self._children = {}
    
    @property
    def path(self) -> str:
        return "/"
