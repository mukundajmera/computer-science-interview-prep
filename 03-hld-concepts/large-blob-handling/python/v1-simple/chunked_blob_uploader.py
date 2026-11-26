import hashlib
import uuid
from typing import Dict, List, Optional


class UploadSession:
    def __init__(self, session_id: str, blob_id: str, total_chunks: int, total_size: int, expected_sha256: str):
        self.session_id = session_id
        self.blob_id = blob_id
        self.total_chunks = total_chunks
        self.total_size = total_size
        self.expected_sha256 = expected_sha256
        self.chunks: Dict[int, bytes] = {}
        self.is_completed = False

    def add_chunk(self, chunk_index: int, data: bytes):
        if self.is_completed:
            raise ValueError("Session already completed")
        if chunk_index < 0 or chunk_index >= self.total_chunks:
            raise ValueError("Invalid chunk index")
        self.chunks[chunk_index] = data

    def get_missing_chunks(self) -> List[int]:
        return [i for i in range(self.total_chunks) if i not in self.chunks]

    def has_all_chunks(self) -> bool:
        return len(self.chunks) == self.total_chunks

    def assemble(self) -> bytes:
        if not self.has_all_chunks():
            raise ValueError("Cannot assemble, missing chunks")
        assembled = bytearray()
        for i in range(self.total_chunks):
            assembled.extend(self.chunks[i])
        self.is_completed = True
        return bytes(assembled)


class ChunkedBlobUploader:
    def __init__(self):
        self.sessions: Dict[str, UploadSession] = {}
        self.completed_blobs: Dict[str, bytes] = {}

    def initiate_session(self, blob_id: str, total_chunks: int, total_size: int, expected_sha256: str) -> str:
        session_id = str(uuid.uuid4())
        session = UploadSession(session_id, blob_id, total_chunks, total_size, expected_sha256)
        self.sessions[session_id] = session
        return session_id

    def upload_chunk(self, session_id: str, chunk_index: int, data: bytes):
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Invalid session ID")
        session.add_chunk(chunk_index, data)

    def get_missing_chunks(self, session_id: str) -> List[int]:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Invalid session ID")
        return session.get_missing_chunks()

    def complete_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Invalid session ID")
        if not session.has_all_chunks():
            return False

        assembled = session.assemble()
        actual_sha256 = self.compute_sha256(assembled)

        if actual_sha256 != session.expected_sha256:
            raise ValueError("Checksum mismatch")

        self.completed_blobs[session.blob_id] = assembled
        del self.sessions[session_id]
        return True

    def get_blob(self, blob_id: str) -> Optional[bytes]:
        return self.completed_blobs.get(blob_id)

    @staticmethod
    def compute_sha256(data: bytes) -> str:
        sha256 = hashlib.sha256()
        sha256.update(data)
        return sha256.hexdigest()
