import threading
import uuid
import time
from typing import Dict, List, Optional, Tuple, Any
from chunk_server import ChunkServer

class ObjectMetadata:
    def __init__(self, obj_key: str, version_id: str, is_delete_marker: bool = False):
        self.obj_key = obj_key
        self.version_id = version_id
        self.is_delete_marker = is_delete_marker
        self.chunks: List[str] = []
        self.size: int = 0
        self.timestamp: float = time.time()

class MetadataStore:
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
            else:
                return versions[-1]

    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        with self.lock:
            if bucket_name not in self.buckets:
                raise ValueError(f"Bucket {bucket_name} does not exist")
            
            result = []
            for obj_key, versions in self.objects[bucket_name].items():
                if obj_key.startswith(prefix) and versions:
                    latest = versions[-1]
                    if not latest.is_delete_marker:
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

class ObjectStorageService:
    def __init__(self, data_dir: str):
        self.metadata_store = MetadataStore()
        self.chunk_servers: List[ChunkServer] = [
            ChunkServer(data_dir, "server_0"),
            ChunkServer(data_dir, "server_1"),
            ChunkServer(data_dir, "server_2")
        ]
        self.replication_factor = 3
        self.lock = threading.RLock()
        self.multipart_uploads: Dict[str, Dict[str, Any]] = {}

    def create_bucket(self, bucket_name: str):
        self.metadata_store.create_bucket(bucket_name)

    def _get_replicas(self, chunk_id: str) -> List[ChunkServer]:
        hash_val = hash(chunk_id)
        return [self.chunk_servers[(hash_val + i) % len(self.chunk_servers)] for i in range(self.replication_factor)]

    def _write_chunk_replicas(self, chunk_id: str, data: bytes):
        replicas = self._get_replicas(chunk_id)
        success_count = 0
        for replica in replicas:
            try:
                replica.write_chunk(chunk_id, data)
                success_count += 1
            except ValueError as e:
                # Chunk might already exist
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
            valid_replica = None
            
            for replica in replicas:
                try:
                    chunk_data = replica.read_chunk(chunk_id)
                    valid_replica = replica
                    break
                except (KeyError, ValueError):
                    continue
                    
            if chunk_data is None:
                raise RuntimeError(f"Data loss: Chunk {chunk_id} unavailable or corrupt on all replicas")
                
            data.extend(chunk_data)
            
            # Read repair
            for replica in replicas:
                if replica != valid_replica:
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
                "parts": {}
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
            
        version_id = upload_id
        metadata = ObjectMetadata(upload_info["key"], version_id)
        
        sorted_parts = sorted(upload_info["parts"].items())
        metadata.chunks = [part[1][0] for part in sorted_parts]
        metadata.size = sum(part[1][1] for part in sorted_parts)
        
        self.metadata_store.put_object_metadata(upload_info["bucket"], upload_info["key"], metadata)
        return version_id

    def list_objects(self, bucket_name: str, prefix: str = "") -> List[str]:
        return self.metadata_store.list_objects(bucket_name, prefix)

    def compact_storage(self):
        active_chunks = self.metadata_store.get_all_active_chunks()
        for server in self.chunk_servers:
            server.compact(active_chunks)
