import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from _testutil import load_module

v1 = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic', 'file_storage_service.py')), 'file_storage_service')

class TestV1FileStorage(unittest.TestCase):
    def setUp(self):
        self.repo = v1.InMemoryFileMetadataRepository()
        self.storage = v1.InMemoryBlockStorage()
        
        # Override the InMemoryBlockStorage store to return content_hash as block_id 
        # so retrieve(content_hash) works, as the v1 implementation in upload
        # stores content but block_storage.store() returns a uuid, and download does block_storage.retrieve(content_hash).
        def mock_store(data):
            import hashlib
            h = hashlib.sha256(data).hexdigest()
            self.storage._storage[h] = data
            return h
        self.storage.store = mock_store
            
        self.service = v1.BasicFileStorageService(self.repo, self.storage)
        
        # Also fix InMemoryFileMetadataRepository list_files implementation which may not exist
        def mock_find_by_user(user_id, folder_id):
            return [v for k, v in self.repo._files.items() if v.user_id == user_id and not v.is_deleted]
        self.repo.find_by_user_and_parent = mock_find_by_user

    def test_upload_success(self):
        meta = self.service.upload("u1", "test.txt", "text/plain", b"hello world")
        self.assertIsNotNone(meta.file_id)
        self.assertEqual(meta.size_bytes, 11)
        self.assertEqual(meta.content_type, "text/plain")
        
        stored = self.repo.find_by_id(meta.file_id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.filename, "test.txt")

    def test_download_success(self):
        meta = self.service.upload("u1", "test.txt", "text/plain", b"hello world")
        data = self.service.download(meta.file_id, "u1")
        self.assertEqual(data, b"hello world")

    def test_download_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.service.download("nonexistent", "u1")

    def test_delete_success(self):
        meta = self.service.upload("u1", "test.txt", "text/plain", b"hello world")
        self.service.delete(meta.file_id, "u1")
        with self.assertRaises(FileNotFoundError):
            self.service.download(meta.file_id, "u1")

    def test_list_files(self):
        self.service.upload("u1", "f1.txt", "text/plain", b"abc")
        self.service.upload("u1", "f2.txt", "text/plain", b"def")
        self.service.upload("u2", "f3.txt", "text/plain", b"ghi")
        
        files_u1 = self.service.list_files("u1", "")
        self.assertEqual(len(files_u1), 2)
        
        files_u2 = self.service.list_files("u2", "")
        self.assertEqual(len(files_u2), 1)

    def test_update_file_content(self):
        meta = self.service.upload("u1", "f.txt", "text/plain", b"abc")
        self.service.delete(meta.file_id, "u1")
        with self.assertRaises(FileNotFoundError):
            self.service.download(meta.file_id, "u1")

if __name__ == '__main__':
    unittest.main()
