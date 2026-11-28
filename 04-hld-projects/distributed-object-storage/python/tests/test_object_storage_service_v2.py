import os
import shutil
import sys
import tempfile

import pytest

# Dynamic path resolution for python tests (mirrors the v1 test file)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))
from object_storage_service_v2 import ObjectStorageServiceV2
from chunk_server_v2 import ChunkServerV2


class TestObjectStorageServiceV2Parity:
    """The v1 test scenarios re-run against v2 to lock in v1 behavior."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = ObjectStorageServiceV2(self.temp_dir)
        self.bucket = "test-bucket"
        self.service.create_bucket(self.bucket)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    def test_bucket_and_object_crud(self):
        data = b"Hello, Distributed World!"
        self.service.put_object(self.bucket, "test_file.txt", data)
        assert self.service.get_object(self.bucket, "test_file.txt") == data

        self.service.put_object(self.bucket, "test_file2.txt", b"Another file")
        self.service.put_object(self.bucket, "other_file.txt", b"Different prefix")
        files = self.service.list_objects(self.bucket, prefix="test_")
        assert len(files) == 2
        assert "test_file.txt" in files
        assert "test_file2.txt" in files

    def test_object_versioning_and_rollback(self):
        v1_id = self.service.put_object(self.bucket, "versioned.txt", b"Version 1")
        v2_id = self.service.put_object(self.bucket, "versioned.txt", b"Version 2")

        assert self.service.get_object(self.bucket, "versioned.txt") == b"Version 2"
        assert self.service.get_object(self.bucket, "versioned.txt", version_id=v1_id) == b"Version 1"

        self.service.delete_object(self.bucket, "versioned.txt")
        assert self.service.get_object(self.bucket, "versioned.txt") is None
        assert self.service.get_object(self.bucket, "versioned.txt", version_id=v2_id) == b"Version 2"

    def test_multipart_upload_workflow(self):
        upload_id = self.service.initiate_multipart_upload(self.bucket, "large_file.txt")
        part1, part2, part3 = b"Part 1 ", b"Part 2 ", b"Part 3"
        self.service.upload_part(upload_id, 1, part1)
        self.service.upload_part(upload_id, 2, part2)
        self.service.upload_part(upload_id, 3, part3)
        self.service.complete_multipart_upload(upload_id)
        assert self.service.get_object(self.bucket, "large_file.txt") == part1 + part2 + part3

    def test_checksum_validation_and_tamper_detection(self):
        data = b"Important Data"
        self.service.put_object(self.bucket, "secure.txt", data)

        metadata = self.service.metadata_store.get_object_metadata(self.bucket, "secure.txt")
        chunk_id = metadata.chunks[0]
        target_replica = self.service._get_replicas(chunk_id)[0]

        offset, size, _ = target_replica.get_chunk_info(chunk_id)
        with open(target_replica.container_file, "r+b") as f:
            f.seek(offset)
            f.write(b"Corrupted Data")  # same length, corrupt payload

        assert self.service.get_object(self.bucket, "secure.txt") == data
        # Read repair rewrote the corrupted replica.
        assert target_replica.read_chunk(chunk_id) == data

    def test_block_compaction_and_tombstone_clean(self):
        self.service.put_object(self.bucket, "file1.txt", b"File 1")
        self.service.put_object(self.bucket, "file2.txt", b"File 2 V1")
        self.service.put_object(self.bucket, "file2.txt", b"File 2 V2")
        self.service.delete_object(self.bucket, "file1.txt")

        sizes_before = [os.path.getsize(s.container_file) for s in self.service.chunk_servers]

        active_chunks = set()
        metadata = self.service.metadata_store.get_object_metadata(self.bucket, "file2.txt")
        active_chunks.update(metadata.chunks)
        for server in self.service.chunk_servers:
            server.compact(active_chunks)

        sizes_after = [os.path.getsize(s.container_file) for s in self.service.chunk_servers]
        assert sum(sizes_after) < sum(sizes_before)


class TestObjectStorageServiceV2:
    """Tests for the three named v2 improvements."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.service = ObjectStorageServiceV2(self.temp_dir)
        self.bucket = "test-bucket"
        self.service.create_bucket(self.bucket)

    def teardown_method(self):
        shutil.rmtree(self.temp_dir)

    # --- Improvement #2: self-describing frames + index rebuild ---

    def test_index_rebuild_restores_reads(self):
        self.service.put_object(self.bucket, "a.txt", b"data a")
        self.service.put_object(self.bucket, "b.txt", b"data b")
        server = self.service.chunk_servers[0]
        index_before = dict(server.index)

        server.index.clear()
        recovered = server.rebuild_index_from_container()

        assert recovered == len(index_before)
        assert server.index == index_before
        assert self.service.get_object(self.bucket, "a.txt") == b"data a"

    def test_rebuild_tolerates_truncated_tail(self):
        self.service.put_object(self.bucket, "a.txt", b"data a")
        server = self.service.chunk_servers[0]
        chunk_id = next(iter(server.index))
        # A torn write leaves trailing garbage after the last full frame.
        with open(server.container_file, "ab") as f:
            f.write(b"CHK1\x00\x00")

        server.index.clear()
        assert server.rebuild_index_from_container() == 1
        assert server.read_chunk(chunk_id) == b"data a"

    # --- Improvement #1: throttled repair + failure injection ---

    def test_repair_pass_restores_replicas_after_chunk_loss(self):
        self.service.put_object(self.bucket, "a.txt", b"replicate me")
        chunk_id = self.service.metadata_store.get_object_metadata(self.bucket, "a.txt").chunks[0]
        victim = self.service._get_replicas(chunk_id)[0]
        victim.simulate_chunk_loss(chunk_id)
        assert not victim.has_chunk(chunk_id)

        result = self.service.repair_pass()

        assert result["repaired"] == [chunk_id]
        assert result["bytes_written"] == len(b"replicate me")
        assert victim.has_chunk(chunk_id)
        assert victim.read_chunk(chunk_id) == b"replicate me"

    def test_repair_pass_respects_byte_budget(self):
        self.service.put_object(self.bucket, "a.txt", b"x" * 30)
        chunk_id = self.service.metadata_store.get_object_metadata(self.bucket, "a.txt").chunks[0]
        victim = self.service._get_replicas(chunk_id)[0]
        victim.simulate_chunk_loss(chunk_id)

        result = self.service.repair_pass(byte_budget=29)
        assert result["repaired"] == []
        assert result["bytes_written"] == 0
        assert not victim.has_chunk(chunk_id)

        result = self.service.repair_pass(byte_budget=30)
        assert result["repaired"] == [chunk_id]
        assert victim.has_chunk(chunk_id)

    def test_reads_skip_down_server(self):
        data = b"still readable"
        self.service.put_object(self.bucket, "a.txt", data)
        chunk_id = self.service.metadata_store.get_object_metadata(self.bucket, "a.txt").chunks[0]
        down_server = self.service._get_replicas(chunk_id)[0]
        down_server.set_down(True)

        assert self.service.get_object(self.bucket, "a.txt") == data
        with pytest.raises(RuntimeError):
            down_server.read_chunk(chunk_id)
        down_server.set_down(False)
        assert self.service.get_object(self.bucket, "a.txt") == data

    def test_writes_succeed_with_one_replica_down(self):
        self.service.chunk_servers[0].set_down(True)
        self.service.put_object(self.bucket, "a.txt", b"written during outage")
        self.service.chunk_servers[0].set_down(False)

        assert self.service.get_object(self.bucket, "a.txt") == b"written during outage"
        # The read repaired the replica that missed the write.
        chunk_id = self.service.metadata_store.get_object_metadata(self.bucket, "a.txt").chunks[0]
        assert self.service.chunk_servers[0].has_chunk(chunk_id)

    # --- Improvement #3: version retention + garbage collection ---

    def test_version_retention_gc_drops_old_versions(self):
        v1_id = self.service.put_object(self.bucket, "doc.txt", b"draft 1")
        v2_id = self.service.put_object(self.bucket, "doc.txt", b"draft 2")
        self.service.put_object(self.bucket, "doc.txt", b"final")

        sizes_before = sum(os.path.getsize(s.container_file) for s in self.service.chunk_servers)
        pruned = self.service.collect_garbage(keep_latest=1)
        sizes_after = sum(os.path.getsize(s.container_file) for s in self.service.chunk_servers)

        assert len(pruned) == 2  # one chunk per pruned version
        assert self.service.get_object(self.bucket, "doc.txt") == b"final"
        assert self.service.get_object(self.bucket, "doc.txt", version_id=v1_id) is None
        assert self.service.get_object(self.bucket, "doc.txt", version_id=v2_id) is None
        assert sizes_after < sizes_before

    def test_retention_preserves_latest_delete_marker(self):
        self.service.put_object(self.bucket, "doc.txt", b"gone soon")
        self.service.delete_object(self.bucket, "doc.txt")

        self.service.collect_garbage(keep_latest=1)

        assert self.service.get_object(self.bucket, "doc.txt") is None
        assert self.service.list_objects(self.bucket) == []

    def test_versions_kept_without_policy(self):
        v1_id = self.service.put_object(self.bucket, "doc.txt", b"one")
        self.service.put_object(self.bucket, "doc.txt", b"two")

        with pytest.raises(ValueError):
            self.service.collect_garbage()

        assert self.service.get_object(self.bucket, "doc.txt", version_id=v1_id) == b"one"
        assert self.service.get_object(self.bucket, "doc.txt") == b"two"

    def test_configured_retention_policy_applies_by_default(self):
        service = ObjectStorageServiceV2(self.temp_dir, retention_keep_latest=2)
        service.create_bucket("b2")
        first = service.put_object("b2", "k", b"v1")
        second = service.put_object("b2", "k", b"v2")
        service.put_object("b2", "k", b"v3")

        service.collect_garbage()

        assert service.get_object("b2", "k", version_id=first) is None
        assert service.get_object("b2", "k", version_id=second) == b"v2"
        assert service.get_object("b2", "k") == b"v3"
