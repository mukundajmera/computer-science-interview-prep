"""
File System - V3 Optimized

Permission class for access control (Unix-style).
"""


class Permission:
    """Permission for a single user class (owner/group/others)."""
    
    def __init__(self, read: bool = True, write: bool = True, execute: bool = False):
        self._read = read
        self._write = write
        self._execute = execute
    
    @classmethod
    def from_octal(cls, octal: int) -> 'Permission':
        """Create permission from Unix-style octal (e.g., 7 = rwx, 6 = rw-, 4 = r--)."""
        if octal < 0 or octal > 7:
            raise ValueError("Octal must be 0-7")
        read = (octal & 4) != 0
        write = (octal & 2) != 0
        execute = (octal & 1) != 0
        return cls(read, write, execute)
    
    def can_read(self) -> bool:
        return self._read
    
    def can_write(self) -> bool:
        return self._write
    
    def can_execute(self) -> bool:
        return self._execute
    
    def set_read(self, value: bool) -> None:
        self._read = value
    
    def set_write(self, value: bool) -> None:
        self._write = value
    
    def set_execute(self, value: bool) -> None:
        self._execute = value
    
    def to_octal(self) -> int:
        """Convert to Unix-style octal."""
        octal = 0
        if self._read:
            octal += 4
        if self._write:
            octal += 2
        if self._execute:
            octal += 1
        return octal
    
    def copy(self) -> 'Permission':
        """Copy this permission."""
        return Permission(self._read, self._write, self._execute)
    
    def __str__(self) -> str:
        r = 'r' if self._read else '-'
        w = 'w' if self._write else '-'
        x = 'x' if self._execute else '-'
        return r + w + x


class PermissionSet:
    """Full permission set (owner/group/others)."""
    
    def __init__(self, owner_octal: int = 7, group_octal: int = 5, others_octal: int = 5):
        self._owner = Permission.from_octal(owner_octal)
        self._group = Permission.from_octal(group_octal)
        self._others = Permission.from_octal(others_octal)
    
    @property
    def owner(self) -> Permission:
        return self._owner
    
    @property
    def group(self) -> Permission:
        return self._group
    
    @property
    def others(self) -> Permission:
        return self._others
    
    def set_mode(self, mode: int) -> None:
        """Set from Unix-style mode (e.g., 755, 644)."""
        owner_octal = (mode // 100) % 10
        group_octal = (mode // 10) % 10
        others_octal = mode % 10
        self._owner = Permission.from_octal(owner_octal)
        self._group = Permission.from_octal(group_octal)
        self._others = Permission.from_octal(others_octal)
    
    def copy(self) -> 'PermissionSet':
        """Copy this permission set."""
        result = PermissionSet()
        result._owner = self._owner.copy()
        result._group = self._group.copy()
        result._others = self._others.copy()
        return result
    
    def __str__(self) -> str:
        return str(self._owner) + str(self._group) + str(self._others)
