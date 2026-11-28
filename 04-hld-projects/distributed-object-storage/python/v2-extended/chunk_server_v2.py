"""v2 ChunkServer: self-describing container frames plus index rebuild.

Each chunk is stored as a length-prefixed frame (magic + chunk id + size +
payload) instead of v1's raw bytes, so the in-memory index can always be
reconstructed by scanning the container file. This is v2 improvement #2;
see the object_storage_service_v2 module docstring for the full list.
"""
import hashlib
import os
import struct
import threading
from typing import Dict, Tuple

MAGIC = b"CHK1"
_ID_LEN = struct.Struct(">I")
_DATA_LEN = struct.Struct(">Q")


class ChunkServerV2:
    def __init__(self, data_dir: str, server_id: str):
        self.server_id = server_id
        self.data_dir = data_dir
        self.container_file = os.path.join(data_dir, f"{server_id}_container.dat")
        self.lock = threading.RLock()
        self.index: Dict[str, Tuple[int, int, str]] = {}
        self.is_down = False
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.container_file, "ab"):
            pass
        # A restart never trusts memory: the index always comes from a scan.
        self.rebuild_index_from_container()

    def _checksum(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _check_up(self):
        if self.is_down:
            raise RuntimeError(f"Chunk server {self.server_id} is down")

    def _encode_frame(self, chunk_id: str, data: bytes) -> bytes:
        chunk_id_bytes = chunk_id.encode("utf-8")
        return (
            MAGIC
            + _ID_LEN.pack(len(chunk_id_bytes))
            + chunk_id_bytes
            + _DATA_LEN.pack(len(data))
            + data
        )

    def write_chunk(self, chunk_id: str, data: bytes) -> Tuple[int, int, str]:
        self._check_up()
        checksum = self._checksum(data)
        with self.lock:
            if chunk_id in self.index:
                raise ValueError(f"Chunk {chunk_id} already exists")
            frame = self._encode_frame(chunk_id, data)
            with open(self.container_file, "ab") as f:
                frame_offset = f.tell()
                f.write(frame)
            data_offset = frame_offset + len(frame) - len(data)
            self.index[chunk_id] = (data_offset, len(data), checksum)
            return data_offset, len(data), checksum

    def read_chunk(self, chunk_id: str) -> bytes:
        self._check_up()
        with self.lock:
            if chunk_id not in self.index:
                raise KeyError(f"Chunk {chunk_id} not found")
            offset, size, expected_checksum = self.index[chunk_id]
            with open(self.container_file, "rb") as f:
                f.seek(offset)
                data = f.read(size)
            if len(data) != size:
                raise ValueError(f"Incomplete chunk {chunk_id} read")
            if self._checksum(data) != expected_checksum:
                raise ValueError(f"Checksum mismatch for chunk {chunk_id}")
            return data

    def repair_chunk(self, chunk_id: str, data: bytes):
        self._check_up()
        checksum = self._checksum(data)
        with self.lock:
            frame = self._encode_frame(chunk_id, data)
            with open(self.container_file, "ab") as f:
                frame_offset = f.tell()
                f.write(frame)
            self.index[chunk_id] = (frame_offset + len(frame) - len(data), len(data), checksum)

    def has_chunk(self, chunk_id: str) -> bool:
        with self.lock:
            return chunk_id in self.index

    def get_chunk_info(self, chunk_id: str) -> Tuple[int, int, str]:
        with self.lock:
            if chunk_id not in self.index:
                raise KeyError(f"Chunk {chunk_id} not found")
            return self.index[chunk_id]

    def set_down(self, down: bool):
        """Failure injection: simulate the whole server being unreachable."""
        self.is_down = down

    def simulate_chunk_loss(self, chunk_id: str):
        """Failure injection: a disk sector loses this one chunk. The stale
        bytes stay in the container until compaction, like a real partial
        disk failure."""
        with self.lock:
            self.index.pop(chunk_id, None)

    def rebuild_index_from_container(self) -> int:
        """Scans the container file and reconstructs the index from the
        frame headers, answering the FOLLOW-UPS.md probe about local index
        corruption. Stops cleanly at the first torn or corrupt tail frame.
        Returns the number of chunks recovered."""
        with self.lock:
            new_index: Dict[str, Tuple[int, int, str]] = {}
            with open(self.container_file, "rb") as f:
                while True:
                    header = f.read(4 + _ID_LEN.size)
                    if len(header) < 4 + _ID_LEN.size or header[:4] != MAGIC:
                        break
                    (id_len,) = _ID_LEN.unpack(header[4:])
                    chunk_id_bytes = f.read(id_len)
                    len_bytes = f.read(_DATA_LEN.size)
                    if len(chunk_id_bytes) != id_len or len(len_bytes) != _DATA_LEN.size:
                        break
                    (data_len,) = _DATA_LEN.unpack(len_bytes)
                    data_offset = f.tell()
                    data = f.read(data_len)
                    if len(data) != data_len:
                        break
                    chunk_id = chunk_id_bytes.decode("utf-8")
                    new_index[chunk_id] = (data_offset, data_len, self._checksum(data))
            self.index = new_index
            return len(new_index)

    def compact(self, active_chunks: set):
        with self.lock:
            new_container = os.path.join(self.data_dir, f"{self.server_id}_container_new.dat")
            new_index: Dict[str, Tuple[int, int, str]] = {}
            with open(new_container, "wb") as out_f, open(self.container_file, "rb") as in_f:
                for chunk_id, (offset, size, checksum) in self.index.items():
                    if chunk_id in active_chunks:
                        in_f.seek(offset)
                        data = in_f.read(size)
                        frame = self._encode_frame(chunk_id, data)
                        frame_offset = out_f.tell()
                        out_f.write(frame)
                        new_index[chunk_id] = (frame_offset + len(frame) - size, size, checksum)
            os.replace(new_container, self.container_file)
            self.index = new_index
