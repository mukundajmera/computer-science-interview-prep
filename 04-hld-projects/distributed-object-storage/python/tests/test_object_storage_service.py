import os
import shutil
import tempfile
import pytest
import sys

# Dynamic path resolution for python tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from object_storage_service import ObjectStorageService
from chunk_server import ChunkServer

class TestObjectStorageService:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = ObjectStorageService(self.temp_dir)
        self.bucket = "test-bucket"
        self.service.create_bucket(self.bucket)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_bucket_and_object_crud(self):
        # Test Put
        data = b"Hello, Distributed World!"
        self.service.put_object(self.bucket, "test_file.txt", data)
        
        # Test Get
        retrieved = self.service.get_object(self.bucket, "test_file.txt")
        assert retrieved == data
        
        # Test List
        self.service.put_object(self.bucket, "test_file2.txt", b"Another file")
        self.service.put_object(self.bucket, "other_file.txt", b"Different prefix")
        
        files = self.service.list_objects(self.bucket, prefix="test_")
        assert len(files) == 2
        assert "test_file.txt" in files
        assert "test_file2.txt" in files

    def test_object_versioning_and_rollback(self):
        # Version 1
        v1_data = b"Version 1"
        v1_id = self.service.put_object(self.bucket, "versioned.txt", v1_data)
        
        # Version 2
        v2_data = b"Version 2"
        v2_id = self.service.put_object(self.bucket, "versioned.txt", v2_data)
        
        # Default get should return v2
        assert self.service.get_object(self.bucket, "versioned.txt") == v2_data
        
        # Get specific version
        assert self.service.get_object(self.bucket, "versioned.txt", version_id=v1_id) == v1_data
        
        # Delete object creates a tombstone
        delete_id = self.service.delete_object(self.bucket, "versioned.txt")
        assert self.service.get_object(self.bucket, "versioned.txt") is None
        
        # Previous versions still accessible
        assert self.service.get_object(self.bucket, "versioned.txt", version_id=v2_id) == v2_data

    def test_multipart_upload_workflow(self):
        upload_id = self.service.initiate_multipart_upload(self.bucket, "large_file.txt")
        
        part1 = b"Part 1 "
        part2 = b"Part 2 "
        part3 = b"Part 3"
        
        self.service.upload_part(upload_id, 1, part1)
        self.service.upload_part(upload_id, 2, part2)
        self.service.upload_part(upload_id, 3, part3)
        
        self.service.complete_multipart_upload(upload_id)
        
        retrieved = self.service.get_object(self.bucket, "large_file.txt")
        assert retrieved == part1 + part2 + part3

    def test_checksum_validation_and_tamper_detection(self):
        data = b"Important Data"
        self.service.put_object(self.bucket, "secure.txt", data)
        
        # Simulate corruption in one replica
        metadata = self.service.metadata_store.get_object_metadata(self.bucket, "secure.txt")
        chunk_id = metadata.chunks[0]
        
        # Corrupt data on the first replica that has it
        replicas = self.service._get_replicas(chunk_id)
        target_replica = replicas[0]
        
        offset, size, _ = target_replica.get_chunk_info(chunk_id)
        with open(target_replica.container_file, 'r+b') as f:
            f.seek(offset)
            f.write(b"Corrupted Data") # Same length but corrupted
            
        # The get_object method should handle read-repair implicitly or at least return valid data
        # since we have replication factor of 3 and only 1 is corrupted.
        retrieved = self.service.get_object(self.bucket, "secure.txt")
        assert retrieved == data
        
        # Ensure repair happened
        repaired_data = target_replica.read_chunk(chunk_id)
        assert repaired_data == data

    def test_block_compaction_and_tombstone_clean(self):
        # Create some data
        self.service.put_object(self.bucket, "file1.txt", b"File 1")
        v1_id = self.service.put_object(self.bucket, "file2.txt", b"File 2 V1")
        self.service.put_object(self.bucket, "file2.txt", b"File 2 V2")
        self.service.delete_object(self.bucket, "file1.txt")
        
        # Get sizes before compaction
        sizes_before = [os.path.getsize(server.container_file) for server in self.service.chunk_servers]
        
        # We need to manually simulate the dropping of old versions from metadata for compaction to be effective
        # in a real system this might be based on age. Here we'll clear active chunks to only latest and not deleted
        
        active_chunks = set()
        metadata = self.service.metadata_store.get_object_metadata(self.bucket, "file2.txt")
        active_chunks.update(metadata.chunks)
        
        # Let's compact using custom active chunks simulating garbage collection of old versions
        for server in self.service.chunk_servers:
            server.compact(active_chunks)
            
        sizes_after = [os.path.getsize(server.container_file) for server in self.service.chunk_servers]
        
        assert sum(sizes_after) < sum(sizes_before)
