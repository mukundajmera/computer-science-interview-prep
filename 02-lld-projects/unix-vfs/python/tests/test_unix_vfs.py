import unittest
import sys
import os

# dynamic import to avoid ImportErrors with hyphenated directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

try:
    from unix_vfs import UnixVfs, FileType
except ImportError:
    pass

class TestUnixVfs(unittest.TestCase):
    def test_open_files_are_not_freed_on_unlink(self):
        vfs = UnixVfs()
        vfs.mkdir("/dir1", 0o755)
        vfs.create("/dir1/file1", 0o755)
        
        fd = vfs.open("/dir1/file1", "w")
        self.assertIsNotNone(fd)
        
        inode = vfs.stat("/dir1/file1")
        self.assertIsNotNone(inode)
        self.assertEqual(inode.link_count, 1)
        self.assertEqual(inode.open_count, 1)
        
        self.assertTrue(vfs.unlink("/dir1/file1"))
        self.assertEqual(inode.link_count, 0)
        self.assertEqual(inode.open_count, 1)
        
        self.assertIn(inode.inode_id, vfs.inodes)
        
        vfs.close(fd)
        self.assertEqual(inode.open_count, 0)
        self.assertNotIn(inode.inode_id, vfs.inodes)

    def test_normal_use_case(self):
        vfs = UnixVfs()
        vfs.mkdir("/dir1", 0o755)
        vfs.create("/dir1/file1", 0o755)
        
        fd = vfs.open("/dir1/file1", "w")
        vfs.write(fd, b"test data")
        vfs.close(fd)
        
        fd2 = vfs.open("/dir1/file1", "r")
        data = vfs.read(fd2, 9)
        vfs.close(fd2)
        
        self.assertEqual(data, b"test data")

    def test_empty_invalid_input(self):
        vfs = UnixVfs()
        self.assertFalse(vfs.create("", 0o755))
        self.assertFalse(vfs.create(None, 0o755))
        self.assertFalse(vfs.create("invalid", 0o755))
        self.assertFalse(vfs.mkdir("", 0o755))

    def test_duplicate_operation(self):
        vfs = UnixVfs()
        vfs.mkdir("/dir1", 0o755)
        self.assertTrue(vfs.create("/dir1/file1", 0o755))
        self.assertFalse(vfs.create("/dir1/file1", 0o755))

    def test_capacity_boundary(self):
        vfs = UnixVfs()
        vfs.symlink("/link2", "/link1")
        vfs.symlink("/link1", "/link2")
        
        with self.assertRaises(RecursionError):
            vfs.stat("/link1")

    def test_failure_rollback(self):
        vfs = UnixVfs()
        vfs.mkdir("/dir1", 0o755)
        vfs.create("/dir1/file1", 0o755)
        
        self.assertFalse(vfs.link("/dir1/file1", "/missing/file2"))
        inode = vfs.stat("/dir1/file1")
        self.assertEqual(inode.link_count, 1)

if __name__ == '__main__':
    unittest.main()
