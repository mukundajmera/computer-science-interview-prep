import hashlib
from typing import Set

class ContentDeduplicator:
    def __init__(self) -> None:
        self.seen_hashes: Set[str] = set()

    def is_duplicate(self, content: str) -> bool:
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)
        return False
