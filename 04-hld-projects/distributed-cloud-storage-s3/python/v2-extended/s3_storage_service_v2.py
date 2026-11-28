"""v2-extended S3 storage service.

Improvements over v1-basic (named per the repo rule v1-basic -> v2-extended):
1. Data-chunks-before-metadata write path (PITFALLS #4): objects are split
   into chunks that are written to a simulated blob-node store FIRST; only
   after every chunk write is acknowledged is the object metadata committed.
   A failure injection hook simulates node write failures; a failed PUT
   leaves no dangling metadata (GET must not see an object whose data never
   landed) and the orphan chunks are tracked for garbage collection.
2. Integrity checking and a scrubber (FOLLOW-UPS #3, bitrot): every chunk
   is stored with a checksum and a replica. GET verifies the checksum and
   raises ChunkIntegrityError on silent corruption; scrub() detects
   corrupted primaries and repairs them from the replica, the simulation
   of the background scrubber daemon.
3. Multipart lifecycle expiry (FOLLOW-UPS #2): see
   multipart_upload_manager_v2.py, which adds a TTL with an injectable
   clock and a sweep that reclaims abandoned uploads and their part data.
"""

import hashlib
import hmac
import time
import uuid
from typing import Dict, List, Optional

DEFAULT_CHUNK_SIZE = 16  # bytes; small so tests exercise multi-chunk objects


class ChunkIntegrityError(Exception):
    """Raised when a stored chunk fails checksum verification (bitrot)."""


class InjectedWriteError(Exception):
    """Raised by the chunk store when failure injection is armed."""


class ChunkRecord:
    def __init__(self, chunk_id: str, data: bytes):
        self.chunk_id = chunk_id
        self.data = data
        self.replica = bytes(data)
        self.checksum = hashlib.md5(data).hexdigest()

    def primary_ok(self) -> bool:
        return hashlib.md5(self.data).hexdigest() == self.checksum


class ChunkStore:
    """Simulated blob-node store: primary copy plus one replica per chunk,
    with a write-failure injection hook and a corruption hook for scrub
    tests."""

    def __init__(self):
        self.chunks: Dict[str, ChunkRecord] = {}
        self._fail_next_writes = 0
        self._skip_writes = 0

    def inject_write_failures(self, count: int, skip: int = 0) -> None:
        """Arm `count` simulated write failures, applied after `skip`
        successful writes (so a failure can strike mid-stream)."""
        self._fail_next_writes = count
        self._skip_writes = skip

    def put(self, data: bytes) -> str:
        if self._skip_writes > 0:
            self._skip_writes -= 1
        elif self._fail_next_writes > 0:
            self._fail_next_writes -= 1
            raise InjectedWriteError("simulated blob-node write failure")
        chunk_id = str(uuid.uuid4())
        self.chunks[chunk_id] = ChunkRecord(chunk_id, data)
        return chunk_id

    def get(self, chunk_id: str) -> bytes:
        record = self.chunks.get(chunk_id)
        if record is None:
            raise ValueError("Chunk not found: " + chunk_id)
        if not record.primary_ok():
            raise ChunkIntegrityError("checksum mismatch on chunk " + chunk_id)
        return record.data

    def corrupt(self, chunk_id: str) -> None:
        """Test hook: flip one byte of the primary copy (bitrot)."""
        record = self.chunks[chunk_id]
        flipped = bytearray(record.data)
        flipped[0] ^= 0xFF
        record.data = bytes(flipped)

    def scrub(self) -> int:
        """Detect corrupted primaries and repair them from the replica.
        Returns the number of chunks repaired."""
        repaired = 0
        for record in self.chunks.values():
            if not record.primary_ok():
                record.data = bytes(record.replica)
                repaired += 1
        return repaired

    def free(self, chunk_ids: List[str]) -> int:
        freed = 0
        for chunk_id in chunk_ids:
            record = self.chunks.pop(chunk_id, None)
            if record is not None:
                freed += len(record.data)
        return freed


class ObjectMetadata:
    def __init__(self, key: str, version_id: str, chunk_ids: Optional[List[str]],
                 size: int, is_deleted: bool, etag: Optional[str]):
        self.key = key
        self.version_id = version_id
        self.chunk_ids = chunk_ids if chunk_ids is not None else []
        self.size = size
        self.is_deleted = is_deleted
        self.last_modified = time.time()
        self.etag = etag


class Bucket:
    def __init__(self, name: str):
        self.name = name
        self.objects: Dict[str, List[ObjectMetadata]] = {}  # key -> list of versions


class S3StorageService:
    def __init__(self, chunk_store: Optional[ChunkStore] = None, chunk_size: int = DEFAULT_CHUNK_SIZE):
        if chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        self.buckets: Dict[str, Bucket] = {}
        self.chunk_store = chunk_store if chunk_store is not None else ChunkStore()
        self.chunk_size = chunk_size
        self.secret_access_key = b"test-secret-key"
        self.used_signatures = set()
        # Chunks written before a failed metadata commit, awaiting GC (v2 item 1)
        self.orphan_chunk_ids: List[str] = []

    # --- bucket operations (parity with v1) ---

    def create_bucket(self, bucket_name: str) -> None:
        if bucket_name not in self.buckets:
            self.buckets[bucket_name] = Bucket(bucket_name)

    def delete_bucket(self, bucket_name: str) -> None:
        if bucket_name in self.buckets:
            del self.buckets[bucket_name]

    # --- write path (v2 item 1: chunks first, metadata last) ---

    def _generate_version_id(self) -> str:
        return str(uuid.uuid4())

    def _calculate_md5_etag(self, data: Optional[bytes]) -> Optional[str]:
        if data is None:
            return None
        return hashlib.md5(data).hexdigest()

    def _write_chunks(self, data: bytes) -> List[str]:
        chunk_ids = []
        for offset in range(0, len(data), self.chunk_size):
            chunk_ids.append(self.chunk_store.put(data[offset:offset + self.chunk_size]))
        return chunk_ids

    def put_object(self, bucket_name: str, key: str, data: bytes) -> str:
        if bucket_name not in self.buckets:
            raise ValueError("Bucket not found")
        return self._commit_object(bucket_name, key, data, self._calculate_md5_etag(data))

    def _commit_object(self, bucket_name: str, key: str, data: bytes, etag: Optional[str]) -> str:
        # v2 item 1: write every data chunk and gather acks BEFORE metadata.
        written_before = set(self.chunk_store.chunks.keys())
        try:
            chunk_ids = self._write_chunks(data)
        except InjectedWriteError:
            # No metadata is committed, so no GET can ever see this object;
            # the partial chunks are tracked as orphans for the GC sweep.
            self.orphan_chunk_ids.extend(self.chunk_store.chunks.keys() - written_before)
            raise

        bucket = self.buckets[bucket_name]
        version_id = self._generate_version_id()
        obj = ObjectMetadata(key, version_id, chunk_ids, len(data), False, etag)
        if key not in bucket.objects:
            bucket.objects[key] = []
        bucket.objects[key].append(obj)
        return version_id

    def collect_orphan_chunks(self) -> int:
        """GC sweep for chunks left behind by failed PUTs. Returns bytes freed."""
        freed = self.chunk_store.free(self.orphan_chunk_ids)
        self.orphan_chunk_ids = []
        return freed

    # --- read path (v2 item 2: verified against chunk checksums) ---

    def _read_chunks(self, obj: ObjectMetadata) -> bytes:
        return b"".join(self.chunk_store.get(cid) for cid in obj.chunk_ids)

    def get_object(self, bucket_name: str, key: str, version_id: Optional[str] = None) -> bytes:
        return self.get_object_with_range(bucket_name, key, version_id, -1, -1)

    def get_object_with_range(self, bucket_name: str, key: str, version_id: Optional[str] = None, start: int = -1, end: int = -1) -> bytes:
        if bucket_name not in self.buckets:
            raise ValueError("Bucket not found")

        bucket = self.buckets[bucket_name]
        if key not in bucket.objects or not bucket.objects[key]:
            raise ValueError("Object not found")

        versions = bucket.objects[key]
        obj = None

        if version_id is None:
            obj = versions[-1]
        else:
            for v in versions:
                if v.version_id == version_id:
                    obj = v
                    break

        if obj is None or obj.is_deleted:
            raise ValueError("Object not found or deleted")

        data = self._read_chunks(obj)
        if start < 0 and end < 0:
            return data

        data_len = len(data)
        s = max(0, start)
        e = data_len - 1 if end < 0 else min(data_len - 1, end)

        if s > e or s >= data_len:
            raise ValueError("Invalid byte range")

        return data[s:e + 1]

    # --- deletes (parity with v1) ---

    def delete_object(self, bucket_name: str, key: str, version_id: Optional[str] = None) -> str:
        if bucket_name not in self.buckets:
            raise ValueError("Bucket not found")

        bucket = self.buckets[bucket_name]

        if version_id is None:
            delete_version_id = self._generate_version_id()
            delete_marker = ObjectMetadata(key, delete_version_id, None, 0, True, None)
            if key not in bucket.objects:
                bucket.objects[key] = []
            bucket.objects[key].append(delete_marker)
            return delete_version_id
        else:
            if key in bucket.objects:
                bucket.objects[key] = [v for v in bucket.objects[key] if v.version_id != version_id]
                if not bucket.objects[key]:
                    del bucket.objects[key]
            return version_id

    # --- internal hook for multipart completion (parity with v1) ---

    def put_object_internal(self, bucket_name: str, key: str, data: bytes, etag: str) -> None:
        """Internal use for multipart upload results; same chunks-first path."""
        if bucket_name not in self.buckets:
            raise ValueError("Bucket not found")
        self._commit_object(bucket_name, key, data, etag)

    # --- scrubber (v2 item 2) ---

    def scrub(self) -> int:
        """Run one scrubber pass over the chunk store; returns repairs made."""
        return self.chunk_store.scrub()

    def chunk_ids_for(self, bucket_name: str, key: str, version_id: Optional[str] = None) -> List[str]:
        """Test/debug helper: physical chunk ids backing an object version."""
        bucket = self.buckets[bucket_name]
        versions = bucket.objects[key]
        if version_id is None:
            return list(versions[-1].chunk_ids)
        for v in versions:
            if v.version_id == version_id:
                return list(v.chunk_ids)
        raise ValueError("Version not found")

    # --- presigned URLs (parity with v1) ---

    def generate_presigned_url(self, bucket_name: str, key: str, http_method: str, expiry_millis: int) -> str:
        # Note: This is an educational implementation and is not AWS SigV4 compatible.
        # It does not provide a production security guarantee.
        base_path = f"https://{bucket_name}.s3.amazonaws.com/{key}"
        canonical_request = f"{http_method}\n{base_path}\n{expiry_millis}"
        signature = self._generate_signature(canonical_request, self.secret_access_key)

        return f"{base_path}?expires={expiry_millis}&signature={signature}"

    def verify_presigned_url(self, url: str, http_method: str, current_time_millis: int) -> bool:
        # Note: This is an educational implementation and is not AWS SigV4 compatible.
        # It does not provide a production security guarantee.
        try:
            if "?" not in url:
                return False

            base_path, qs = url.split("?", 1)
            params = dict(p.split("=") for p in qs.split("&") if "=" in p)

            expires = int(params.get("expires", 0))
            signature = params.get("signature")

            if not signature or expires == 0:
                return False

            if current_time_millis > expires:
                return False

            if signature in self.used_signatures:
                return False  # Replay attack

            canonical_request = f"{http_method}\n{base_path}\n{expires}"
            expected_signature = self._generate_signature(canonical_request, self.secret_access_key)

            is_valid = hmac.compare_digest(expected_signature, signature)
            if is_valid:
                self.used_signatures.add(signature)
            return is_valid
        except Exception:
            return False

    def _generate_signature(self, data: str, secret: bytes) -> str:
        return hmac.new(secret, data.encode('utf-8'), hashlib.sha256).hexdigest()
