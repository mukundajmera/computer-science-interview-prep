import time
import threading
from typing import Optional, Dict
from dataclasses import dataclass
from base62 import encode

@dataclass
class PasteMetadata:
    id: int
    short_link: str
    created_at: float
    expires_at: Optional[float]


class TokenBucket:
    def __init__(self, capacity: int, fill_rate: float):
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.tokens = float(capacity)
        self.last_fill = time.time()
        self.lock = threading.Lock()

    def consume(self) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_fill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.fill_rate)
            self.last_fill = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False


class PastebinService:
    def __init__(self, capacity: int = 10, fill_rate: float = 1.0):
        self.metadata_store: Dict[str, PasteMetadata] = {}
        self.blob_store: Dict[str, str] = {}
        self.rate_limiters: Dict[str, TokenBucket] = {}
        
        self.capacity = capacity
        self.fill_rate = fill_rate
        self.next_id = 1000000000  # Start with a large ID to get 6-7 char Base62
        
        self.lock = threading.RLock()

    def _get_limiter(self, ip_address: str) -> TokenBucket:
        with self.lock:
            if ip_address not in self.rate_limiters:
                self.rate_limiters[ip_address] = TokenBucket(self.capacity, self.fill_rate)
            return self.rate_limiters[ip_address]

    def create_paste(self, content: str, ip_address: str, ttl_seconds: Optional[int] = None) -> Optional[str]:
        limiter = self._get_limiter(ip_address)
        if not limiter.consume():
            return None  # Rate limit exceeded

        with self.lock:
            paste_id = self.next_id
            self.next_id += 1
            
            short_link = encode(paste_id)
            # Pad to 7 characters if needed (for realism)
            while len(short_link) < 7:
                short_link = "0" + short_link

            now = time.time()
            expires_at = now + ttl_seconds if ttl_seconds is not None else None
            
            metadata = PasteMetadata(
                id=paste_id,
                short_link=short_link,
                created_at=now,
                expires_at=expires_at
            )
            
            self.metadata_store[short_link] = metadata
            self.blob_store[short_link] = content
            
            return short_link

    def get_paste(self, short_link: str) -> Optional[str]:
        with self.lock:
            if short_link not in self.metadata_store:
                return None
            
            metadata = self.metadata_store[short_link]
            if metadata.expires_at is not None and time.time() > metadata.expires_at:
                # Active TTL validation on read
                self._delete_paste(short_link)
                return None
            
            return self.blob_store.get(short_link)

    def _delete_paste(self, short_link: str):
        self.metadata_store.pop(short_link, None)
        self.blob_store.pop(short_link, None)

    def sweep_expired_pastes(self):
        """Batch TTL cleanup sweep."""
        now = time.time()
        expired_links = []
        with self.lock:
            for short_link, metadata in self.metadata_store.items():
                if metadata.expires_at is not None and now > metadata.expires_at:
                    expired_links.append(short_link)
            
            for short_link in expired_links:
                self._delete_paste(short_link)
        return len(expired_links)
