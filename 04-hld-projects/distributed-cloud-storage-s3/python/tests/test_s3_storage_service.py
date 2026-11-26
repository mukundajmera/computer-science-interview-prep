import unittest
import time
import os
import sys

# Load local modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "v1-basic")))

from s3_storage_service import S3StorageService
from multipart_upload_manager import MultipartUploadManager, CompletedPart

class TestS3StorageService(unittest.TestCase):

    def setUp(self):
        self.s3_service = S3StorageService()
        self.mp_manager = MultipartUploadManager(self.s3_service)

    def test_bucket_operations(self):
        bucket = "test-bucket"
        self.s3_service.create_bucket(bucket)
        
        key = "test.txt"
        data = b"Hello, S3!"
        
        version_id = self.s3_service.put_object(bucket, key, data)
        self.assertIsNotNone(version_id)
        
        retrieved = self.s3_service.get_object(bucket, key, version_id)
        self.assertEqual(retrieved, data)
        
        self.s3_service.delete_bucket(bucket)
        with self.assertRaises(ValueError):
            self.s3_service.get_object(bucket, key, version_id)

    def test_byte_range_request(self):
        bucket = "range-bucket"
        self.s3_service.create_bucket(bucket)
        
        key = "data.bin"
        data = bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        
        version_id = self.s3_service.put_object(bucket, key, data)
        
        retrieved = self.s3_service.get_object_with_range(bucket, key, version_id, 2, 5)
        self.assertEqual(retrieved, bytes([2, 3, 4, 5]))
        
        retrieved_end = self.s3_service.get_object_with_range(bucket, key, version_id, 7, -1)
        self.assertEqual(retrieved_end, bytes([7, 8, 9]))
        
        with self.assertRaises(ValueError):
            self.s3_service.get_object_with_range(bucket, key, version_id, 10, 12)
            
        with self.assertRaises(ValueError):
            self.s3_service.get_object_with_range(bucket, key, version_id, 5, 2)

    def test_soft_delete_and_versions(self):
        bucket = "version-bucket"
        self.s3_service.create_bucket(bucket)
        
        key = "doc.txt"
        data1 = b"V1"
        data2 = b"V2"
        
        v1 = self.s3_service.put_object(bucket, key, data1)
        v2 = self.s3_service.put_object(bucket, key, data2)
        
        self.assertEqual(self.s3_service.get_object(bucket, key, v1), data1)
        self.assertEqual(self.s3_service.get_object(bucket, key, v2), data2)
        self.assertEqual(self.s3_service.get_object(bucket, key, None), data2)
        
        self.s3_service.delete_object(bucket, key)
        
        with self.assertRaises(ValueError):
            self.s3_service.get_object(bucket, key, None)
            
        self.assertEqual(self.s3_service.get_object(bucket, key, v1), data1)

    def test_versioned_deletes(self):
        bucket = "delete-version-bucket"
        self.s3_service.create_bucket(bucket)
        
        key = "file.txt"
        data1 = b"V1"
        data2 = b"V2"
        
        v1 = self.s3_service.put_object(bucket, key, data1)
        v2 = self.s3_service.put_object(bucket, key, data2)
        
        self.s3_service.delete_object(bucket, key, v1)
        
        with self.assertRaises(ValueError):
            self.s3_service.get_object(bucket, key, v1)
            
        self.assertEqual(self.s3_service.get_object(bucket, key, v2), data2)

    def test_multipart_upload(self):
        bucket = "mp-bucket"
        self.s3_service.create_bucket(bucket)
        key = "large.bin"
        
        upload_id = self.mp_manager.initiate_multipart_upload(bucket, key)
        
        part1 = b"Part 1 Data "
        part2 = b"Part 2 Data"
        
        etag1 = self.mp_manager.upload_part(upload_id, 1, part1)
        etag2 = self.mp_manager.upload_part(upload_id, 2, part2)
        
        composite_etag = self.mp_manager.complete_multipart_upload(upload_id, [
            CompletedPart(1, etag1),
            CompletedPart(2, etag2)
        ])
        self.assertTrue(composite_etag.endswith("-2"))
        
        # Replayed complete
        with self.assertRaises(ValueError):
            self.mp_manager.complete_multipart_upload(upload_id, [
                CompletedPart(1, etag1),
                CompletedPart(2, etag2)
            ])
            
        combined = self.s3_service.get_object(bucket, key, None)
        self.assertEqual(combined, b"Part 1 Data Part 2 Data")
        
        upload_id2 = self.mp_manager.initiate_multipart_upload(bucket, "other.bin")
        etag2_1 = self.mp_manager.upload_part(upload_id2, 1, part1)
        etag2_2 = self.mp_manager.upload_part(upload_id2, 2, part2)
        
        # Out of order
        with self.assertRaises(ValueError):
            self.mp_manager.complete_multipart_upload(upload_id2, [
                CompletedPart(2, etag2_2),
                CompletedPart(1, etag2_1)
            ])

        # Duplicate parts
        with self.assertRaises(ValueError):
            self.mp_manager.complete_multipart_upload(upload_id2, [
                CompletedPart(1, etag2_1),
                CompletedPart(1, etag2_1)
            ])

        # Missing parts
        with self.assertRaises(ValueError):
            self.mp_manager.complete_multipart_upload(upload_id2, [
                CompletedPart(3, "fake-etag")
            ])

        # Checksum mismatch
        with self.assertRaises(ValueError):
            self.mp_manager.complete_multipart_upload(upload_id2, [
                CompletedPart(1, "bad-etag")
            ])
            
        # Abort upload
        self.mp_manager.abort_multipart_upload(upload_id2)
        
        # Replayed abort
        with self.assertRaises(ValueError):
            self.mp_manager.abort_multipart_upload(upload_id2)
            
        # Ensure no metadata was published for aborted upload
        with self.assertRaises(ValueError):
            self.s3_service.get_object(bucket, "other.bin", None)

    def test_presigned_url(self):
        bucket = "auth-bucket"
        key = "private.png"
        
        now = int(time.time() * 1000)
        expiry = now + 3600_000
        
        url = self.s3_service.generate_presigned_url(bucket, key, "GET", expiry)
        self.assertIn(f"expires={expiry}", url)
        
        self.assertFalse(self.s3_service.verify_presigned_url(url, "GET", expiry + 1000))
        self.assertFalse(self.s3_service.verify_presigned_url(url, "PUT", now))
        
        tampered_url = url.replace(f"expires={expiry}", f"expires={expiry + 10000}")
        self.assertFalse(self.s3_service.verify_presigned_url(tampered_url, "GET", now))
        
        tampered_path_url = url.replace("private.png", "public.png")
        self.assertFalse(self.s3_service.verify_presigned_url(tampered_path_url, "GET", now))
        
        # Final assertions - register the valid URL, then test replay
        self.assertTrue(self.s3_service.verify_presigned_url(url, "GET", now))
        self.assertFalse(self.s3_service.verify_presigned_url(url, "GET", now)) # Replay attack

if __name__ == '__main__':
    unittest.main()
