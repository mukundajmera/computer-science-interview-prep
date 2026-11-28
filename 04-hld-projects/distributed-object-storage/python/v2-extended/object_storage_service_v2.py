"""v2-extended distributed object storage simulator.

Improvements over v1-basic (each has dedicated tests):

1. Throttled background repair with failure injection: FOLLOW-UPS.md #3
   requires chunk rebuilds to be rate-limited so they do not degrade user
   reads and writes. ChunkServerV2 can simulate single-chunk loss and whole
   server downtime, and repair_pass() re-replicates under-replicated chunks
   under an explicit byte budget per sweep.

2. Self-describing container format with index rebuild: the FOLLOW-UPS.md
   interviewer probe asks what happens when a chunk server's local index is
   corrupted. v2 frames every chunk with a magic header (see
   chunk_server_v2.py) so rebuild_index_from_container() can reconstruct the
   index by scanning the container, and startup always rebuilds from disk.

3. Configurable version retention with garbage collection: v1's compaction
   test had to drop old versions by hand ("in a real system this might be
   based on age. Here we'll clear ... manually"). v2 adds a keep-latest-N
   retention policy and collect_garbage() so compaction actually reclaims
   the space held by superseded versions.
"""
import threading
import uuid
from typing import Any, Dict, List, Optional

from chunk_server_v2 import ChunkServerV2


class ObjectMetadata:
    def __init__(self, obj_key: str, version_id: str, is_delete_marker: bool = False):
        self.obj_key = obj_key
        self.version_id = version_id
        self.is_delete_marker = is_delete_marker
        self.chunks: List[str] = []
        self.size: int = 0


class MetadataStoreV2:
    """v1 metadata store plus keep-latest-N version pruning for GC."""

    def __init__(self):
        self.lock = threading.RLock()
        self.buckets: set = set()
        self.objects: Dict[str, Dict[str, List[ObjectMetadata]]] = {}

    def create_bucket(self, bucket_name: str):
        with self.lock:
            if bucket_name in self.buckets:
                raise ValueError(f"Bucket {bucket_name} already exists")
            self.buckets.add(bucket_name)
            self.objects[bucket_name] = {}

    def list_buckets(self) -> List[str]:
        with self.lock:
            return list(self.buckets)

    def put_object_metadata(self, bucket_name: str, obj_key: str, metadata: ObjectMetadata):
        with self.lock:
            if bucket_name not in self.buckets:
                raise ValueError(f"Bucket {bucket_name} does not exist")
            if obj_key not in self.objects[bucket_name]:
                self.objects[bucket_name][obj_key] = []
            self.objects[bucket_name][obj_key].append(metadata)

    def get_object_metadata(self, bucket_name: str, obj_key: str, version_id: Optional[str] = None) -> Optional[ObjectMetadata]:
        with self.lock:
            if bucket_name not in self.buckets or obj_key not in self.objects[bucket_name]:
                return None
            versions = self.objects[bucket_name][obj_key]
            if not versions:
                return None
            if version_id:
                for v in versions:
                    if v.version_id == version_id:
                        return v
                return None
            return versions[-1]

    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        with self.lock:
            if bucket_name not in self.buckets:
                raise ValueError(f"Bucket {bucket_name} does not exist")
            result = []
            for obj_key, versions in self.objects[bucket_name].items():
                if obj_key.startswith(prefix) and versions:
                    if not versions[-1].is_delete_marker:
                        result.append(obj_key)
            return result

    def get_all_active_chunks(self) -> set:
        with self.lock:
            active = set()
            for bucket_objs in self.objects.values():
                for versions in bucket_objs.values():
                    for version in versions:
                        if not version.is_delete_marker:
                            active.update(version.chunks)
            return active

    def prune_versions(self, keep_latest: int) -> List[str]:
        """Drops all but the newest keep_latest versions of every object.
        The newest version is never pruned, so a trailing delete marker
        keeps the object deleted. Returns the chunks the pruned versions
        held; they become garbage once compaction runs."""
        pruned_chunks: List[str] = []
        with self.lock:
            for bucket_objs in self.objects.values():
                for versions in bucket_objs.values():
                    if len(versions) > keep_latest:
                        for old in versions[:-keep_latest]:
                            pruned_chunks.extend(old.chunks)
                        del versions[:-keep_latest]
        return pruned_chunks


class ObjectStorageServiceV2:
    def __init__(self, data_dir: str, retention_keep_latest: Optional[int] = None):
        self.metadata_store = MetadataStoreV2()
        self.chunk_servers: List[ChunkServerV2] = [
            ChunkServerV2(data_dir, "server_0"),
            ChunkServerV2(data_dir, "server_1"),
            ChunkServerV2(data_dir, "server_2"),
        ]
        self.replication_factor = 3
        self.lock = threading.RLock()
        self.multipart_uploads: Dict[str, Dict[str, Any]] = {}
        self.retention_keep_latest = retention_keep_latest

    def create_bucket(self, bucket_name: str):
        self.metadata_store.create_bucket(bucket_name)

    def _get_replicas(self, chunk_id: str) -> List[ChunkServerV2]:
        hash_val = hash(chunk_id)
        return [self.chunk_servers[(hash_val + i) % len(self.chunk_servers)] for i in range(self.replication_factor)]

    def _write_chunk_replicas(self, chunk_id: str, data: bytes):
        replicas = self._get_replicas(chunk_id)
        success_count = 0
        for replica in replicas:
            if replica.is_down:
                continue
            try:
                replica.write_chunk(chunk_id, data)
                success_count += 1
            except ValueError as e:
                if "already exists" in str(e):
                    success_count += 1
        if success_count == 0:
            raise RuntimeError("Failed to write chunk to any replica")

    def put_object(self, bucket_name: str, obj_key: str, data: bytes) -> str:
        version_id = str(uuid.uuid4())
        chunk_id = f"{bucket_name}_{obj_key}_{version_id}_0"
        self._write_chunk_replicas(chunk_id, data)
        metadata = ObjectMetadata(obj_key, version_id)
        metadata.chunks = [chunk_id]
        metadata.size = len(data)
        self.metadata_store.put_object_metadata(bucket_name, obj_key, metadata)
        return version_id

    def get_object(self, bucket_name: str, obj_key: str, version_id: Optional[str] = None) -> Optional[bytes]:
        metadata = self.metadata_store.get_object_metadata(bucket_name, obj_key, version_id)
        if not metadata or metadata.is_delete_marker:
            return None
        data = bytearray()
        for chunk_id in metadata.chunks:
            replicas = self._get_replicas(chunk_id)
            chunk_data = None
            for replica in replicas:
                if replica.is_down:
                    continue
                try:
                    chunk_data = replica.read_chunk(chunk_id)
                    break
                except (KeyError, ValueError):
                    continue
            if chunk_data is None:
                raise RuntimeError(f"Data loss: Chunk {chunk_id} unavailable or corrupt on all replicas")
            data.extend(chunk_data)
            # Read repair for replicas that are up but missing or corrupt.
            for replica in replicas:
                if replica.is_down:
                    continue
                try:
                    replica.read_chunk(chunk_id)
                except (KeyError, ValueError):
                    replica.repair_chunk(chunk_id, chunk_data)
        return bytes(data)

    def delete_object(self, bucket_name: str, obj_key: str) -> str:
        version_id = str(uuid.uuid4())
        metadata = ObjectMetadata(obj_key, version_id, is_delete_marker=True)
        self.metadata_store.put_object_metadata(bucket_name, obj_key, metadata)
        return version_id

    def initiate_multipart_upload(self, bucket_name: str, obj_key: str) -> str:
        with self.lock:
            upload_id = str(uuid.uuid4())
            self.multipart_uploads[upload_id] = {
                "bucket": bucket_name,
                "key": obj_key,
                "parts": {},
            }
            return upload_id

    def upload_part(self, upload_id: str, part_number: int, data: bytes):
        with self.lock:
            if upload_id not in self.multipart_uploads:
                raise ValueError("Invalid upload ID")
            upload_info = self.multipart_uploads[upload_id]
            chunk_id = f"{upload_info['bucket']}_{upload_info['key']}_{upload_id}_{part_number}"
        self._write_chunk_replicas(chunk_id, data)
        with self.lock:
            self.multipart_uploads[upload_id]["parts"][part_number] = (chunk_id, len(data))

    def complete_multipart_upload(self, upload_id: str) -> str:
        with self.lock:
            if upload_id not in self.multipart_uploads:
                raise ValueError("Invalid upload ID")
            upload_info = self.multipart_uploads.pop(upload_id)
        metadata = ObjectMetadata(upload_info["key"], upload_id)
        sorted_parts = sorted(upload_info["parts"].items())
        metadata.chunks = [part[1][0] for part in sorted_parts]
        metadata.size = sum(part[1][1] for part in sorted_parts)
        self.metadata_store.put_object_metadata(upload_info["bucket"], upload_info["key"], metadata)
        return upload_id

    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        return self.metadata_store.list_objects(bucket_name, prefix)

    def compact_storage(self):
        active_chunks = self.metadata_store.get_all_active_chunks()
        for server in self.chunk_servers:
            server.compact(active_chunks)

    def repair_pass(self, byte_budget: Optional[int] = None) -> Dict[str, Any]:
        """One throttled rebuild sweep (improvement #1, FOLLOW-UPS.md #3):
        re-replicates every under-replicated active chunk it finds until the
        per-sweep byte budget is spent, so background repair cannot saturate
        the network during peak traffic. With byte_budget=None the sweep is
        unbounded. Returns the repaired chunk ids and bytes written."""
        repaired: List[str] = []
        spent = 0
        for chunk_id in sorted(self.metadata_store.get_all_active_chunks()):
            replicas = self._get_replicas(chunk_id)
            holders = [r for r in replicas if not r.is_down and r.has_chunk(chunk_id)]
            missing = [r for r in replicas if not r.is_down and not r.has_chunk(chunk_id)]
            if not holders or not missing:
                continue
            data = holders[0].read_chunk(chunk_id)
            if byte_budget is not None and spent + len(data) > byte_budget:
                break
            missing[0].repair_chunk(chunk_id, data)
            spent += len(data)
            repaired.append(chunk_id)
        return {"repaired": repaired, "bytes_written": spent}

    def collect_garbage(self, keep_latest: Optional[int] = None) -> List[str]:
        """Version-retention GC (improvement #3): prunes superseded versions
        per the keep-latest-N policy, then compacts every container so the
        pruned chunks' space is actually reclaimed. Returns the pruned
        chunks. The newest version of each object always survives, so a
        trailing delete marker keeps the object deleted."""
        keep = keep_latest if keep_latest is not None else self.retention_keep_latest
        if keep is None:
            raise ValueError("No retention policy: pass keep_latest or configure retention_keep_latest")
        pruned = self.metadata_store.prune_versions(max(1, keep))
        self.compact_storage()
        return pruned
