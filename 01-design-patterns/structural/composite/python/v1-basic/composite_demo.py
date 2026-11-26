"""
Composite Pattern - Python Implementation: File System
"""
from abc import ABC, abstractmethod
from typing import List

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')



# Component Interface
class FileSystemItem(ABC):
    @abstractmethod
    def get_name(self) -> str: pass
    
    @abstractmethod
    def get_size(self) -> int: pass
    
    @abstractmethod
    def display(self, indent: str = "") -> None: pass


# Leaf
class File(FileSystemItem):
    def __init__(self, name: str, size: int):
        self._name = name
        self._size = size
    
    def get_name(self) -> str:
        return self._name
    
    def get_size(self) -> int:
        return self._size
    
    def display(self, indent: str = "") -> None:
        print(f"{indent}{self._name} ({self._size} KB)")


# Composite
class Directory(FileSystemItem):
    def __init__(self, name: str):
        self._name = name
        self._children: List[FileSystemItem] = []
    
    def add(self, item: FileSystemItem) -> None:
        self._children.append(item)
    
    def remove(self, item: FileSystemItem) -> None:
        self._children.remove(item)
    
    def get_name(self) -> str:
        return self._name
    
    def get_size(self) -> int:
        return sum(child.get_size() for child in self._children)
    
    def display(self, indent: str = "") -> None:
        print(f"{indent}{self._name} ({self.get_size()} KB)")
        for child in self._children:
            child.display(indent + "  ")


if __name__ == "__main__":
    # Build file system
    root = Directory("root")
    
    docs = Directory("docs")
    docs.add(File("readme.txt", 10))
    docs.add(File("guide.pdf", 250))
    
    src = Directory("src")
    src.add(File("main.py", 15))
    src.add(File("utils.py", 8))
    
    lib = Directory("lib")
    lib.add(File("django.whl", 5000))
    src.add(lib)  # Nested composite
    
    root.add(docs)
    root.add(src)
    root.add(File("config.yaml", 5))
    
    # Display tree
    print("=== File System ===")
    root.display()
    
    print(f"\n=== Total Size ===")
    print(f"Root: {root.get_size()} KB")
    print(f"Src: {src.get_size()} KB")
