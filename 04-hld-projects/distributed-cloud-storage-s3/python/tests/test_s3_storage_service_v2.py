import unittest
import time
import os
import sys

# Load v1 (parity checks) and v2 modules; distinctive _v2 module names avoid
# same-process import collisions with the v1 flat imports.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "v1-basic")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "v2-extended")))

from s3_storage_service import S3StorageService as V1StorageService
from multipart_upload_manager import MultipartUploadManager as V1MultipartManager
from s3_storage_service_v2 import (
    S3StorageService, ChunkStore, ChunkIntegrityError, InjectedWriteError,
)
from multipart_upload_manager_v2 import MultipartUploadManager, CompletedPart


class FakeClock:
    def __init__(self, start: float = 1_000_000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float):
        self.now += seconds


class TestV1Parity(unittest.TestCase):
    """v1 behavior must keep working on the v1 classes (regression guard)."""

    def setUp(self):
        self.s3_service = V1StorageService()
        self.mp_manager = V1MultipartManager(self.s3_service)

    def test_v1_bucket_and_object_roundtrip(self):
        self.s3_service.create_bucket("parity-bucket")
        version_id = self.s3_service.put_object("parity-bucket", "a.txt", b"hello")
        self.assertEqual(self.s3_service.get_object("parity-bucket", "a.txt", version_id), b"hello")


class TestS3StorageServiceV2(unittest.TestCase):

    def setUp(self):
        self.chunk_store = ChunkStore()
        self.s3_service = S3StorageService(self.chunk_store)
        self.mp_manager = MultipartUploadManager(self.s3_service)

    # --- Parity tests: v2 must keep every v1 guarantee ---

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

        with self.assertRaises(ValueError):
            self.mp_manager.complete_multipart_upload(upload_id2, [
                CompletedPart(2, etag2_2),
                CompletedPart(1, etag2_1)
            ])

        with self.assertRaises(ValueError):
            self.mp_manager.complete_multipart_upload(upload_id2, [
                CompletedPart(1, etag2_1),
                CompletedPart(1, etag2_1)
            ])

        with self.assertRaises(ValueError):
            self.mp_manager.complete_multipart_upload(upload_id2, [
                CompletedPart(3, "fake-etag")
            ])

        with self.assertRaises(ValueError):
            self.mp_manager.complete_multipart_upload(upload_id2, [
                CompletedPart(1, "bad-etag")
            ])

        self.mp_manager.abort_multipart_upload(upload_id2)

        with self.assertRaises(ValueError):
            self.mp_manager.abort_multipart_upload(upload_id2)

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

        self.assertTrue(self.s3_service.verify_presigned_url(url, "GET", now))
        self.assertFalse(self.s3_service.verify_presigned_url(url, "GET", now))  # Replay attack

    # --- v2 item 1: data chunks before metadata, with failure injection ---

    def test_failed_chunk_write_commits_no_metadata(self):
        bucket = "fail-bucket"
        self.s3_service.create_bucket(bucket)
        data = b"0123456789ABCDEF0123456789ABCDEF"  # 2 chunks at 16-byte chunk size

        self.chunk_store.inject_write_failures(1)  # second chunk write fails
        with self.assertRaises(InjectedWriteError):
            self.s3_service.put_object(bucket, "obj.bin", data)

        # No dangling pointer: the object is invisible through every read path.
        with self.assertRaises(ValueError):
            self.s3_service.get_object(bucket, "obj.bin", None)

    def test_failed_chunk_write_leaves_tracked_orphans(self):
        bucket = "orphan-bucket"
        self.s3_service.create_bucket(bucket)
        data = b"0123456789ABCDEF0123456789ABCDEF"  # 2 chunks

        self.chunk_store.inject_write_failures(1, skip=1)  # first chunk lands, second fails
        with self.assertRaises(InjectedWriteError):
            self.s3_service.put_object(bucket, "obj.bin", data)

        # One chunk landed before the failure; it is tracked for GC.
        self.assertEqual(len(self.s3_service.orphan_chunk_ids), 1)
        freed = self.s3_service.collect_orphan_chunks()
        self.assertEqual(freed, 16)
        self.assertEqual(len(self.chunk_store.chunks), 0)

    def test_successful_put_creates_no_orphans(self):
        bucket = "clean-bucket"
        self.s3_service.create_bucket(bucket)
        self.s3_service.put_object(bucket, "obj.bin", b"0123456789ABCDEF0123456789ABCDEF")
        self.assertEqual(self.s3_service.orphan_chunk_ids, [])
        self.assertEqual(self.s3_service.collect_orphan_chunks(), 0)

    def test_object_spans_multiple_chunks(self):
        bucket = "multi-chunk-bucket"
        self.s3_service.create_bucket(bucket)
        data = bytes(range(64))  # 4 chunks at 16 bytes
        version_id = self.s3_service.put_object(bucket, "wide.bin", data)
        self.assertEqual(len(self.s3_service.chunk_ids_for(bucket, "wide.bin", version_id)), 4)
        # Range read across a chunk boundary reassembles correctly.
        self.assertEqual(
            self.s3_service.get_object_with_range(bucket, "wide.bin", version_id, 14, 18),
            bytes([14, 15, 16, 17, 18]))

    # --- v2 item 2: integrity checking and scrubber ---

    def test_corrupted_chunk_raises_integrity_error(self):
        bucket = "bitrot-bucket"
        self.s3_service.create_bucket(bucket)
        self.s3_service.put_object(bucket, "obj.bin", b"0123456789ABCDEF")
        chunk_id = self.s3_service.chunk_ids_for(bucket, "obj.bin")[0]

        self.chunk_store.corrupt(chunk_id)
        with self.assertRaises(ChunkIntegrityError):
            self.s3_service.get_object(bucket, "obj.bin", None)

    def test_scrub_repairs_corrupted_chunk(self):
        bucket = "scrub-bucket"
        self.s3_service.create_bucket(bucket)
        data = b"0123456789ABCDEF"
        self.s3_service.put_object(bucket, "obj.bin", data)
        chunk_id = self.s3_service.chunk_ids_for(bucket, "obj.bin")[0]

        self.chunk_store.corrupt(chunk_id)
        repaired = self.s3_service.scrub()
        self.assertEqual(repaired, 1)
        self.assertEqual(self.s3_service.get_object(bucket, "obj.bin", None), data)

    def test_scrub_on_clean_store_repairs_nothing(self):
        bucket = "healthy-bucket"
        self.s3_service.create_bucket(bucket)
        self.s3_service.put_object(bucket, "obj.bin", b"0123456789ABCDEF0123456789ABCDEF")
        self.assertEqual(self.s3_service.scrub(), 0)

    # --- v2 item 3: multipart lifecycle expiry ---

    def test_expired_upload_is_rejected_and_swept(self):
        clock = FakeClock()
        service = S3StorageService()
        manager = MultipartUploadManager(service, upload_ttl_seconds=60.0, clock=clock)
        service.create_bucket("ttl-bucket")

        upload_id = manager.initiate_multipart_upload("ttl-bucket", "big.bin")
        manager.upload_part(upload_id, 1, b"0123456789ABCDEF")

        clock.advance(61)
        with self.assertRaises(ValueError):
            manager.upload_part(upload_id, 2, b"more data")

        expired_ids, freed = manager.sweep_expired_uploads()
        self.assertEqual(expired_ids, [upload_id])
        self.assertEqual(freed, 16)
        self.assertEqual(manager.uploads, {})

    def test_fresh_upload_survives_sweep(self):
        clock = FakeClock()
        service = S3StorageService()
        manager = MultipartUploadManager(service, upload_ttl_seconds=60.0, clock=clock)
        service.create_bucket("fresh-bucket")

        upload_id = manager.initiate_multipart_upload("fresh-bucket", "big.bin")
        etag = manager.upload_part(upload_id, 1, b"0123456789ABCDEF")

        clock.advance(30)
        expired_ids, freed = manager.sweep_expired_uploads()
        self.assertEqual(expired_ids, [])
        self.assertEqual(freed, 0)
        self.assertIn(upload_id, manager.uploads)

        # And it still completes normally.
        composite = manager.complete_multipart_upload(upload_id, [CompletedPart(1, etag)])
        self.assertTrue(composite.endswith("-1"))

    def test_no_ttl_means_no_expiry(self):
        clock = FakeClock()
        service = S3StorageService()
        manager = MultipartUploadManager(service, clock=clock)  # v1 parity default
        service.create_bucket("no-ttl-bucket")

        upload_id = manager.initiate_multipart_upload("no-ttl-bucket", "big.bin")
        manager.upload_part(upload_id, 1, b"data")
        clock.advance(10_000)
        expired_ids, freed = manager.sweep_expired_uploads()
        self.assertEqual(expired_ids, [])
        self.assertEqual(freed, 0)
        self.assertIn(upload_id, manager.uploads)

    def test_completed_upload_is_not_swept(self):
        clock = FakeClock()
        service = S3StorageService()
        manager = MultipartUploadManager(service, upload_ttl_seconds=60.0, clock=clock)
        service.create_bucket("done-bucket")

        upload_id = manager.initiate_multipart_upload("done-bucket", "big.bin")
        etag = manager.upload_part(upload_id, 1, b"0123456789ABCDEF")
        manager.complete_multipart_upload(upload_id, [CompletedPart(1, etag)])

        clock.advance(3600)
        expired_ids, _ = manager.sweep_expired_uploads()
        self.assertEqual(expired_ids, [])
        # The completed object is still fully readable.
        self.assertEqual(service.get_object("done-bucket", "big.bin", None), b"0123456789ABCDEF")


if __name__ == '__main__':
    unittest.main()
