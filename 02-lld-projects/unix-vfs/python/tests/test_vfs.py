import pytest
import sys
import os

# dynamic import to avoid ImportErrors with hyphenated directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

try:
    from unix_vfs import UnixVfs as VFS, FileType
except ImportError:
    pass

def test_hard_links_and_ref_counting():
    vfs = VFS()
    vfs.mkdir("/dir1")
    vfs.create("/dir1/file1")
    
    inode = vfs.stat("/dir1/file1")
    assert inode is not None
    assert inode.link_count == 1
    
    vfs.mkdir("/dir2")
    assert vfs.link("/dir1/file1", "/dir2/file2") is True
    
    assert inode.link_count == 2
    
    assert vfs.unlink("/dir1/file1") is True
    assert inode.link_count == 1
    assert vfs.stat("/dir2/file2") == inode
    
    assert vfs.unlink("/dir2/file2") is True
    assert inode.link_count == 0
    # The inode should be removed from VFS
    assert inode.inode_id not in vfs.inodes

def test_symlink_cycle_detection():
    vfs = VFS()
    vfs.symlink("/link2", "/link1")
    vfs.symlink("/link1", "/link2")
    
    with pytest.raises(RecursionError, match="Too many levels of symbolic links"):
        vfs.stat("/link1")

def test_file_descriptor_independent_cursor():
    vfs = VFS()
    vfs.create("/testfile")
    
    fd1 = vfs.open("/testfile", "w")
    assert fd1 is not None
    vfs.write(fd1, b"Hello, World!")
    
    fd2 = vfs.open("/testfile", "r")
    assert fd2 is not None
    assert fd2.offset == 0
    
    data = vfs.read(fd2, 5)
    assert data == b"Hello"
    assert fd2.offset == 5
    
    fd3 = vfs.open("/testfile", "r")
    assert fd3 is not None
    assert fd3.offset == 0
    data2 = vfs.read(fd3, 5)
    assert data2 == b"Hello"
    
    vfs.lseek(fd2, 7, 0) # SEEK_SET
    data3 = vfs.read(fd2, 6)
    assert data3 == b"World!"
    assert fd2.offset == 13

def test_octal_permission_bitmask():
    vfs = VFS()
    vfs.create("/file1", 0o644)
    inode = vfs.stat("/file1")
    assert inode is not None
    assert inode.permissions == 0o644
    
    assert vfs.chmod("/file1", 0o755) is True
    assert inode.permissions == 0o755

def test_error_cases_and_hierarchy():
    vfs = VFS()
    
    # 1. Directory recursion and path parsing
    assert vfs.mkdir("/a") is True
    assert vfs.mkdir("/a/b") is True
    assert vfs.mkdir("/a/b/c") is True
    assert vfs.create("/a/b/c/file.txt") is True
    
    inode = vfs.stat("/a/b/c/file.txt")
    assert inode is not None
    assert inode.file_type == FileType.FILE
    
    # 2. File not found
    assert vfs.stat("/a/b/c/missing.txt") is None
    assert vfs.open("/a/b/c/missing.txt", "r") is None
    
    # 3. Not a directory error (trying to create a file inside a file)
    assert vfs.create("/a/b/c/file.txt/nested.txt") is False
    assert vfs.mkdir("/a/b/c/file.txt/dir") is False
    
    # 4. Opening a directory as a file should fail
    assert vfs.open("/a/b", "r") is None

def test_open_files_are_not_freed_on_unlink():
    vfs = VFS()
    vfs.mkdir("/dir1")
    vfs.create("/dir1/file1")
    
    fd = vfs.open("/dir1/file1", "w")
    assert fd is not None
    
    inode = vfs.stat("/dir1/file1")
    assert inode is not None
    assert getattr(inode, 'link_count', 0) == 1
    assert getattr(inode, 'open_count', 0) == 1
    
    assert vfs.unlink("/dir1/file1") is True
    assert getattr(inode, 'link_count', 0) == 0
    assert getattr(inode, 'open_count', 0) == 1
    
    assert inode.inode_id in vfs.inodes
    
    vfs.close(fd)
    assert getattr(inode, 'open_count', 0) == 0
    assert inode.inode_id not in vfs.inodes
