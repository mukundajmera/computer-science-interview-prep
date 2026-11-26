import threading
import hashlib
from typing import Set

class FingerprintStore:
    def __init__(self) -> None:
        self.fingerprints: Set[str] = set()
        self.bloom_filter: Set[str] = set()
        self.lock = threading.Lock()

    def add(self, fingerprint: str) -> bool:
        with self.lock:
            bloom_hash = hashlib.md5(fingerprint.encode('utf-8')).hexdigest()[:4]
            if bloom_hash in self.bloom_filter:
                if fingerprint in self.fingerprints:
                    return False
                self.fingerprints.add(fingerprint)
                return True
            
            self.bloom_filter.add(bloom_hash)
            self.fingerprints.add(fingerprint)
            return True
