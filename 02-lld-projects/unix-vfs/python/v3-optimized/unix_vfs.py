import os
from enum import Enum
from typing import Dict, List, Optional, Tuple

class FileType(Enum):
    FILE = 1
    DIRECTORY = 2
    SYMLINK = 3

class Inode:
    def __init__(self, inode_id: int, file_type: FileType, permissions: int):
        self.inode_id = inode_id
        self.file_type = file_type
        self.permissions = permissions
        self.link_count = 1
        self.open_count = 0
        self.data: bytearray = bytearray()
        self.symlink_target: Optional[str] = None
        self.directory_entries: Dict[str, int] = {}

class FileDescriptor:
    def __init__(self, inode: Inode, mode: str):
        self.inode = inode
        self.mode = mode
        self.offset = 0
        self.closed = False

class UnixVfs:
    """
    v3-optimized version of the Unix Virtual File System.
    This version implements advanced in-memory storage efficiency, including
    hard link reference counting, an inode allocation bitmap, and proper 
    memory deallocation upon unlinking.
    """
    MAX_SYMLINKS = 40

    def __init__(self):
        self.inodes: Dict[int, Inode] = {}
        self.inode_bitmap = [False] * 1000

        
        root_inode = self._create_inode(FileType.DIRECTORY, 0o755)
        self.root_inode_id = root_inode.inode_id
        root_inode.directory_entries["."] = root_inode.inode_id
        root_inode.directory_entries[".."] = root_inode.inode_id

    def _create_inode(self, file_type: FileType, permissions: int) -> Inode:
        inode_id = self._allocate_inode()
        inode = Inode(inode_id, file_type, permissions)
        self.inodes[inode_id] = inode
        return inode

    def _allocate_inode(self) -> int:
        for i in range(1, len(self.inode_bitmap)):
            if not self.inode_bitmap[i]:
                self.inode_bitmap[i] = True
                return i
        self.inode_bitmap.append(True)
        return len(self.inode_bitmap) - 1

    def _resolve_path(self, path: str, follow_symlink: bool = True) -> Optional[Inode]:
        if not path or not path.startswith("/"):
            return None

        current_inode = self.inodes[self.root_inode_id]
        parts = [p for p in path.split("/") if p]
        
        symlink_count = 0
        i = 0
        
        while i < len(parts):
            part = parts[i]

            if part not in current_inode.directory_entries:
                return None

            next_inode_id = current_inode.directory_entries[part]
            next_inode = self.inodes[next_inode_id]

            if i == len(parts) - 1 and not follow_symlink:
                return next_inode

            if next_inode.file_type == FileType.SYMLINK:
                symlink_count += 1
                if symlink_count > self.MAX_SYMLINKS:
                    raise RecursionError("Too many levels of symbolic links")
                if symlink_count > self.MAX_SYMLINKS:
                    raise RecursionError("Too many levels of symbolic links")

                target_path = next_inode.symlink_target
                if not target_path:
                    return None

                target_parts = [p for p in target_path.split("/") if p]
                
                if target_path.startswith("/"):
                    current_inode = self.inodes[self.root_inode_id]
                    parts = target_parts + parts[i+1:]
                    i = 0
                else:
                    parts = target_parts + parts[i+1:]
                    i = 0
            else:
                current_inode = next_inode
                i += 1

        return current_inode

    def _get_parent_and_name(self, path: str) -> Tuple[Optional[Inode], str]:
        parts = [p for p in path.split("/") if p]
        if not parts:
            return self.inodes[self.root_inode_id], ""
            
        name = parts[-1]
        parent_path = "/" + "/".join(parts[:-1])
        if parent_path == "/":
            parent_path = "/"
            
        parent_inode = self._resolve_path(parent_path)
        return parent_inode, name

    def mkdir(self, path: str, permissions: int = 0o755) -> bool:
        """
        Creates a new directory at the specified path with given permissions.
        """
        if not path or not path.strip() or not path.startswith("/"):
            return False
        parent_inode, name = self._get_parent_and_name(path)
        if not parent_inode or parent_inode.file_type != FileType.DIRECTORY:
            return False
            
        if name in parent_inode.directory_entries or not name:
            return False
            
        new_inode = self._create_inode(FileType.DIRECTORY, permissions)
        new_inode.directory_entries["."] = new_inode.inode_id
        new_inode.directory_entries[".."] = parent_inode.inode_id
        
        parent_inode.directory_entries[name] = new_inode.inode_id
        parent_inode.link_count += 1
        
        return True

    def create(self, path: str, permissions: int = 0o644) -> bool:
        """
        Creates a new regular file at the specified path with given permissions.
        """
        if not path or not path.strip() or not path.startswith("/"):
            return False
        parent_inode, name = self._get_parent_and_name(path)
        if not parent_inode or parent_inode.file_type != FileType.DIRECTORY:
            return False
            
        if name in parent_inode.directory_entries or not name:
            return False
            
        new_inode = self._create_inode(FileType.FILE, permissions)
        parent_inode.directory_entries[name] = new_inode.inode_id
        
        return True

    def link(self, old_path: str, new_path: str) -> bool:
        target_inode = self._resolve_path(old_path)
        if not target_inode or target_inode.file_type == FileType.DIRECTORY:
            return False
            
        parent_inode, name = self._get_parent_and_name(new_path)
        if not parent_inode or parent_inode.file_type != FileType.DIRECTORY:
            return False
            
        if name in parent_inode.directory_entries or not name:
            return False
            
        parent_inode.directory_entries[name] = target_inode.inode_id
        target_inode.link_count += 1
        
        return True

    def symlink(self, target: str, link_path: str) -> bool:
        parent_inode, name = self._get_parent_and_name(link_path)
        if not parent_inode or parent_inode.file_type != FileType.DIRECTORY:
            return False
            
        if name in parent_inode.directory_entries or not name:
            return False
            
        symlink_inode = self._create_inode(FileType.SYMLINK, 0o777)
        symlink_inode.symlink_target = target
        
        parent_inode.directory_entries[name] = symlink_inode.inode_id
        
        return True

    def _check_and_free(self, inode: Inode):
        if inode.link_count <= 0 and inode.open_count <= 0:
            if inode.inode_id in self.inodes:
                del self.inodes[inode.inode_id]
                self.inode_bitmap[inode.inode_id] = False

    def unlink(self, path: str) -> bool:
        if not path:
            return False
        parent_inode, name = self._get_parent_and_name(path)
        if not parent_inode or parent_inode.file_type != FileType.DIRECTORY:
            return False
            
        if name not in parent_inode.directory_entries:
            return False
            
        target_inode_id = parent_inode.directory_entries[name]
        target_inode = self.inodes.get(target_inode_id)
        if not target_inode:
            return False
            
        if target_inode.file_type == FileType.DIRECTORY:
            if len(target_inode.directory_entries) > 2:
                return False
                
        del parent_inode.directory_entries[name]
        
        if target_inode.file_type == FileType.DIRECTORY:
            parent_inode.link_count -= 1
            
        target_inode.link_count -= 1
        
        self._check_and_free(target_inode)
        
        return True

    def open(self, path: str, mode: str) -> Optional[FileDescriptor]:
        """
        Opens a file and returns a FileDescriptor.
        Maintains an independent cursor for read/write/seek operations.
        """
        inode = self._resolve_path(path)
        if not inode or inode.file_type == FileType.DIRECTORY:
            return None
            
        inode.open_count += 1
        return FileDescriptor(inode, mode)

    def close(self, fd: FileDescriptor) -> None:
        if not fd or fd.closed:
            return
        fd.closed = True
        inode = fd.inode
        inode.open_count -= 1
        self._check_and_free(inode)

    def read(self, fd: FileDescriptor, size: int) -> bytes:
        if not fd or fd.closed or ('r' not in fd.mode and '+' not in fd.mode):
            return b""
            
        inode = fd.inode
        data = inode.data
        offset = fd.offset
        
        if offset >= len(data):
            return b""
            
        bytes_to_read = min(size, len(data) - offset)
        result = data[offset:offset + bytes_to_read]
        fd.offset += bytes_to_read
        
        return bytes(result)

    def write(self, fd: FileDescriptor, data: bytes) -> int:
        if not fd or fd.closed or ('w' not in fd.mode and '+' not in fd.mode and 'a' not in fd.mode):
            return -1
            
        inode = fd.inode
        offset = fd.offset
        
        if 'a' in fd.mode:
            offset = len(inode.data)
            fd.offset = offset
            
        new_length = max(len(inode.data), offset + len(data))
        new_data = bytearray(new_length)
        new_data[:len(inode.data)] = inode.data
        new_data[offset:offset + len(data)] = data
        
        inode.data = new_data
        fd.offset = offset + len(data)
        
        return len(data)

    def lseek(self, fd: FileDescriptor, offset: int, whence: int = 0) -> int:
        if not fd or fd.closed:
            return -1
        inode = fd.inode
        new_offset = -1
        
        if whence == 0:
            new_offset = offset
        elif whence == 1:
            new_offset = fd.offset + offset
        elif whence == 2:
            new_offset = len(inode.data) + offset
            
        if new_offset < 0:
            return -1
            
        fd.offset = new_offset
        return new_offset

    def chmod(self, path: str, mode: int) -> bool:
        inode = self._resolve_path(path)
        if not inode:
            return False
        inode.permissions = mode
        return True

    def stat(self, path: str) -> Optional[Inode]:
        return self._resolve_path(path)
