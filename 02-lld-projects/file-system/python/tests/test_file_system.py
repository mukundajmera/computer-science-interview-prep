"""
Unit tests for File System
"""
import unittest
import sys
import os

# Add v2-extended to path for testing (has most features)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-extended'))

from file_system import FileSystem
from file import File
from directory import Directory



class TestFile(unittest.TestCase):
    """Tests for File class."""
    
    def test_file_content(self):
        """File stores content correctly."""
        file = File("test.txt", "Hello World")
        self.assertEqual("Hello World", file.read())
        self.assertEqual(11, file.get_size())
    
    def test_file_append(self):
        """File append works correctly."""
        file = File("test.txt", "Hello")
        file.append(" World")
        self.assertEqual("Hello World", file.read())
    
    def test_file_extension(self):
        """File extension extraction works."""
        txt = File("notes.txt")
        java = File("Main.java")
        no_ext = File("README")
        
        self.assertEqual("txt", txt.get_extension())
        self.assertEqual("java", java.get_extension())
        self.assertEqual("", no_ext.get_extension())
    
    def test_invalid_file_name(self):
        """Invalid file name throws exception."""
        with self.assertRaises(ValueError):
            File("")
        with self.assertRaises(ValueError):
            File("path/file")


class TestDirectory(unittest.TestCase):
    """Tests for Directory class."""
    
    def test_directory_add_entry(self):
        """Directory add and get entry works."""
        dir = Directory("docs")
        file = File("test.txt")
        
        self.assertTrue(dir.add_entry(file))
        self.assertEqual(file, dir.get_entry("test.txt"))
        self.assertTrue(dir.has_entry("test.txt"))
    
    def test_directory_duplicate_prevention(self):
        """Directory prevents duplicate entries."""
        dir = Directory("docs")
        file1 = File("test.txt")
        file2 = File("test.txt")
        
        self.assertTrue(dir.add_entry(file1))
        self.assertFalse(dir.add_entry(file2))
    
    def test_directory_remove_entry(self):
        """Directory remove entry works."""
        dir = Directory("docs")
        file = File("test.txt")
        
        dir.add_entry(file)
        self.assertTrue(dir.remove_entry("test.txt"))
        self.assertIsNone(dir.get_entry("test.txt"))
        self.assertFalse(dir.remove_entry("nonexistent.txt"))
    
    def test_directory_size(self):
        """Directory size is sum of children."""
        dir = Directory("docs")
        dir.add_entry(File("a.txt", "1234567890"))
        dir.add_entry(File("b.txt", "12345"))
        
        self.assertEqual(15, dir.get_size())
    
    def test_directory_path(self):
        """Directory path is calculated correctly."""
        root = Directory("home")
        user = Directory("user")
        docs = Directory("documents")
        
        root.add_entry(user)
        user.add_entry(docs)
        
        self.assertEqual("/home", root.path)
        self.assertEqual("/home/user", user.path)
        self.assertEqual("/home/user/documents", docs.path)


class TestFileSystem(unittest.TestCase):
    """Tests for FileSystem class."""
    
    def setUp(self):
        FileSystem.reset_instance()
    
    def tearDown(self):
        FileSystem.reset_instance()
    
    def test_singleton_instance(self):
        """FileSystem singleton returns same instance."""
        fs1 = FileSystem.get_instance()
        fs2 = FileSystem.get_instance()
        self.assertIs(fs1, fs2)
    
    def test_create_file(self):
        """FileSystem creates file."""
        fs = FileSystem.get_instance()
        file = fs.create_file("/test.txt", "content")
        
        self.assertIsNotNone(file)
        self.assertEqual("test.txt", file.name)
        self.assertEqual("content", file.read())
    
    def test_create_directory(self):
        """FileSystem creates nested directories."""
        fs = FileSystem.get_instance()
        dir = fs.create_directory("/home/user/documents")
        
        self.assertIsNotNone(dir)
        self.assertEqual("documents", dir.name)
        self.assertTrue(fs.exists("/home"))
        self.assertTrue(fs.exists("/home/user"))
    
    def test_resolve_path(self):
        """FileSystem resolves paths correctly."""
        fs = FileSystem.get_instance()
        fs.create_directory("/home/user")
        fs.create_file("/home/user/file.txt")
        
        self.assertIsNotNone(fs.resolve_path("/home"))
        self.assertIsNotNone(fs.resolve_path("/home/user"))
        self.assertIsNotNone(fs.resolve_path("/home/user/file.txt"))
        self.assertIsNone(fs.resolve_path("/nonexistent"))
    
    def test_relative_path_resolution(self):
        """FileSystem handles relative paths with .."""
        fs = FileSystem.get_instance()
        fs.create_directory("/home/user")
        fs.change_directory("/home/user")
        
        parent = fs.resolve_path("..")
        self.assertIsNotNone(parent)
        self.assertEqual("/home", parent.path)
    
    def test_delete(self):
        """FileSystem delete works."""
        fs = FileSystem.get_instance()
        fs.create_file("/test.txt")
        
        self.assertTrue(fs.exists("/test.txt"))
        self.assertTrue(fs.delete("/test.txt"))
        self.assertFalse(fs.exists("/test.txt"))
    
    def test_copy_file(self):
        """FileSystem copy file works."""
        fs = FileSystem.get_instance()
        fs.create_file("/original.txt", "content")
        
        self.assertTrue(fs.copy("/original.txt", "/copy.txt"))
        self.assertEqual("content", fs.read_file("/copy.txt"))
        self.assertEqual("content", fs.read_file("/original.txt"))
    
    def test_move_file(self):
        """FileSystem move file works."""
        fs = FileSystem.get_instance()
        fs.create_file("/original.txt", "content")
        fs.create_directory("/target")
        
        self.assertTrue(fs.move("/original.txt", "/target/moved.txt"))
        self.assertFalse(fs.exists("/original.txt"))
        self.assertEqual("content", fs.read_file("/target/moved.txt"))
    
    def test_copy_directory(self):
        """FileSystem copy directory works."""
        fs = FileSystem.get_instance()
        fs.create_directory("/source")
        fs.create_file("/source/file1.txt", "content1")
        fs.create_file("/source/file2.txt", "content2")
        
        self.assertTrue(fs.copy("/source", "/destination"))
        self.assertTrue(fs.exists("/source/file1.txt"))
        self.assertTrue(fs.exists("/destination/file1.txt"))
        self.assertEqual("content1", fs.read_file("/destination/file1.txt"))
    
    def test_copy_into_self_prevented(self):
        """FileSystem prevents copy into self."""
        fs = FileSystem.get_instance()
        fs.create_directory("/parent/child")
        
        self.assertFalse(fs.copy("/parent", "/parent/child/copy"))
    
    def test_search_by_extension(self):
        """FileSystem search by extension works."""
        fs = FileSystem.get_instance()
        fs.create_file("/file1.txt", "a")
        fs.create_file("/file2.txt", "b")
        fs.create_file("/file3.md", "c")
        
        results = fs.find_by_extension("/", "txt")
        self.assertEqual(2, len(results))
    
    def test_search_by_name(self):
        """FileSystem search by name pattern works."""
        fs = FileSystem.get_instance()
        fs.create_file("/test_one.txt", "a")
        fs.create_file("/test_two.txt", "b")
        fs.create_file("/other.txt", "c")
        
        results = fs.find_by_name("/", "test*")
        self.assertEqual(2, len(results))
    
    def test_full_workflow(self):
        """Full workflow test."""
        fs = FileSystem.get_instance()
        
        # Create structure
        fs.create_directory("/home/user/documents")
        fs.create_directory("/home/user/backup")
        fs.create_file("/home/user/documents/notes.txt", "Important notes")
        
        # Copy
        fs.copy("/home/user/documents/notes.txt", "/home/user/backup/notes_backup.txt")
        
        # Verify
        self.assertEqual("Important notes", fs.read_file("/home/user/documents/notes.txt"))
        self.assertEqual("Important notes", fs.read_file("/home/user/backup/notes_backup.txt"))
        
        # Modify original
        fs.write_file("/home/user/documents/notes.txt", "Updated notes")
        
        # Verify independence
        self.assertEqual("Updated notes", fs.read_file("/home/user/documents/notes.txt"))
        self.assertEqual("Important notes", fs.read_file("/home/user/backup/notes_backup.txt"))
        
        # Delete
        fs.delete("/home/user/documents")
        self.assertFalse(fs.exists("/home/user/documents"))
        self.assertTrue(fs.exists("/home/user/backup/notes_backup.txt"))


if __name__ == '__main__':
    unittest.main()
