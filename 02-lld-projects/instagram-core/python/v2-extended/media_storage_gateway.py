import uuid
from typing import Dict, Optional

class MediaStorageGateway:
    def __init__(self):
        self.storage: Dict[str, bytes] = {}

    def put(self, media_bytes: bytes) -> str:
        media_key = str(uuid.uuid4())
        self.storage[media_key] = media_bytes
        return media_key

    def get(self, media_key: str) -> Optional[bytes]:
        return self.storage.get(media_key)
