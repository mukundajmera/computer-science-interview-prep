import hashlib
import os
import threading
from typing import Dict, Tuple

class ChunkServer:
    def __init__(self, data_dir: str, server_id: str):
        self.server_id = server_id
        self.data_dir = data_dir
        self.container_file = os.path.join(data_dir, f"{server_id}_container.dat")
        self.lock = threading.RLock()
        self.index: Dict[str, Tuple[int, int, str]] = {}
        
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.container_file, 'ab') as f:
            pass

    def write_chunk(self, chunk_id: str, data: bytes) -> Tuple[int, int, str]:
        checksum = hashlib.sha256(data).hexdigest()
        with self.lock:
            if chunk_id in self.index:
                raise ValueError(f"Chunk {chunk_id} already exists")
                
            with open(self.container_file, 'ab') as f:
                offset = f.tell()
                f.write(data)
                
            self.index[chunk_id] = (offset, len(data), checksum)
            return offset, len(data), checksum
            
    def read_chunk(self, chunk_id: str) -> bytes:
        with self.lock:
            if chunk_id not in self.index:
                raise KeyError(f"Chunk {chunk_id} not found")
                
            offset, size, expected_checksum = self.index[chunk_id]
            with open(self.container_file, 'rb') as f:
                f.seek(offset)
                data = f.read(size)
                
            if len(data) != size:
                raise ValueError(f"Incomplete chunk {chunk_id} read")
                
            actual_checksum = hashlib.sha256(data).hexdigest()
            if actual_checksum != expected_checksum:
                raise ValueError(f"Checksum mismatch for chunk {chunk_id}")
                
            return data

    def repair_chunk(self, chunk_id: str, data: bytes):
        with self.lock:
            checksum = hashlib.sha256(data).hexdigest()
            with open(self.container_file, 'ab') as f:
                offset = f.tell()
                f.write(data)
            self.index[chunk_id] = (offset, len(data), checksum)

    def get_chunk_info(self, chunk_id: str) -> Tuple[int, int, str]:
        with self.lock:
            if chunk_id not in self.index:
                raise KeyError(f"Chunk {chunk_id} not found")
            return self.index[chunk_id]

    def compact(self, active_chunks: set):
        with self.lock:
            new_container = os.path.join(self.data_dir, f"{self.server_id}_container_new.dat")
            new_index = {}
            with open(new_container, 'wb') as out_f:
                with open(self.container_file, 'rb') as in_f:
                    for chunk_id, (offset, size, checksum) in self.index.items():
                        if chunk_id in active_chunks:
                            in_f.seek(offset)
                            data = in_f.read(size)
                            new_offset = out_f.tell()
                            out_f.write(data)
                            new_index[chunk_id] = (new_offset, size, checksum)
                            
            os.replace(new_container, self.container_file)
            self.index = new_index
