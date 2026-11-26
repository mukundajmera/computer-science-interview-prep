import unittest
import sys
import os
import hashlib
import asyncio
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from _testutil import load_module

v2 = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-scaled', 'cached_file_service.py')), 'cached_file_service')

class MockMetadataRepo(v2.FileMetadataRepository):
    def __init__(self):
        self.files = {}
    def save(self, metadata):
        self.files[metadata.file_id] = metadata
        return metadata
    def find_by_id(self, file_id):
        return self.files.get(file_id)
    def find_by_id_from_replica(self, file_id):
        return self.files.get(file_id)
    def delete(self, file_id):
        if file_id in self.files:
            del self.files[file_id]
    def find_by_folder_id(self, folder_id):
        return []
    def find_by_folder_id_from_replica(self, folder_id):
        return []

class MockCache(v2.Cache):
    def __init__(self):
        self.store = {}
    def get(self, key):
        return self.store.get(key)
    def put(self, key, value, ttl_seconds):
        self.store[key] = value
    def exists(self, key):
        return key in self.store
    def invalidate(self, key):
        if key in self.store:
            del self.store[key]

class MockCDN(v2.CDNService):
    def get_signed_url(self, file_id, expiry):
        return f"http://cdn/{file_id}"
    def invalidate_cache(self, file_id):
        pass
    def warm_cache(self, file_id):
        pass

class MockChunkManager(v2.ChunkManager):
    def __init__(self):
        self.uploads = {}
    def initiate_chunked_upload(self, file_id, total_size, chunk_size):
        uid = f"up_{file_id}"
        self.uploads[uid] = {
            "file_id": file_id,
            "total_size": total_size,
            "chunk_size": chunk_size,
            "chunks": {}
        }
        return uid
    def upload_chunk(self, upload_id, chunk_number, data):
        self.uploads[upload_id]["chunks"][chunk_number] = data
    def complete_chunked_upload(self, upload_id):
        pass
    def abort_chunked_upload(self, upload_id):
        del self.uploads[upload_id]
    def get_upload_status(self, upload_id):
        up = self.uploads[upload_id]
        return v2.ChunkStatus(
            upload_id=upload_id,
            uploaded_chunks=list(up["chunks"].keys()),
            pending_chunks=[],
            total_size=up["total_size"],
            uploaded_size=sum(len(d) for d in up["chunks"].values())
        )

class TestV2CachedFileStorage(unittest.TestCase):
    def setUp(self):
        self.repo = MockMetadataRepo()
        self.cache = MockCache()
        self.cdn = MockCDN()
        self.chunk_mgr = MockChunkManager()
        self.service = v2.CachedFileStorageService(
            self.repo, self.cache, self.cdn, self.chunk_mgr
        )
        self.dedup_worker = v2.DeduplicationWorker()

    def test_chunked_upload_flow(self):
        req = v2.ChunkedUploadRequest(
            file_name="large.bin", total_size=15, content_type="app/bin",
            user_id="u1", folder_id="f1", chunk_size_bytes=5
        )
        uid = self.service.initiate_chunked_upload(req)
        self.service.upload_chunk(uid, 1, b"12345")
        self.service.upload_chunk(uid, 2, b"67890")
        
        status = self.service.get_upload_progress(uid)
        self.assertEqual(status.uploaded_size, 10)
        self.assertEqual(len(status.uploaded_chunks), 2)
        
        self.service.upload_chunk(uid, 3, b"abcde")
        meta = self.service.complete_chunked_upload(uid, "large.bin", "u1", "f1")
        
        self.assertEqual(meta.file_name, "large.bin")
        self.assertEqual(meta.size, 15)

    def test_deduplication(self):
        async def run_dedup():
            return await self.dedup_worker.check_duplicate("somehash")
            
        res = asyncio.run(run_dedup())
        self.assertIsNone(res)

    def test_metadata_caching(self):
        meta = v2.FileMetadataCache(file_id="f1", file_name="f.txt", size=10, content_type="txt")
        self.repo.save(meta)
        
        res1 = self.service.get_file_metadata("f1")
        self.assertIsNotNone(res1)
        self.assertIsNotNone(self.cache.get("f1"))
        
        self.repo.delete("f1")
        res2 = self.service.get_file_metadata("f1")
        self.assertEqual(res2.file_name, "f.txt")

    def test_get_download_url(self):
        meta = v2.FileMetadataCache(file_id="f1", file_name="f.txt", size=10, content_type="txt", cdn_url="http://cdn/f1")
        self.repo.save(meta)
        
        res = self.service.get_download_url("f1")
        self.assertTrue(res.is_cdn_url)
        self.assertEqual(res.download_url, "http://cdn/f1")

    def test_get_download_url_no_cdn(self):
        meta = v2.FileMetadataCache(file_id="f1", file_name="f.txt", size=10, content_type="txt", cdn_url=None)
        self.repo.save(meta)
        
        res = self.service.get_download_url("f1")
        self.assertIsNotNone(res.download_url)
        
    def test_rate_limiter(self):
        limiter = v2.UploadRateLimiter(max_uploads_per_minute=2, max_bytes_per_hour=100)
        self.assertTrue(limiter.is_allowed("u1", 10))
        limiter.record_upload("u1", 10)
        
        self.assertTrue(limiter.is_allowed("u1", 10))
        limiter.record_upload("u1", 10)
        
        self.assertFalse(limiter.is_allowed("u1", 10)) 
        
        self.assertTrue(limiter.is_allowed("u2", 90))
        limiter.record_upload("u2", 90)
        
        self.assertFalse(limiter.is_allowed("u2", 20)) 

if __name__ == '__main__':
    unittest.main()
