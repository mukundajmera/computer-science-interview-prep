"""
URL Shortener - V2 Scaled

Enhanced URL shortening service with caching layer.
Adds Redis caching and async analytics processing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
import threading
import queue
import time


@dataclass
class ClickEvent:
    """Click event for analytics processing."""
    short_code: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    ip_hash: Optional[str] = None
    country: Optional[str] = None


class UrlCache(ABC):
    """Cache interface for URL lookups."""
    
    @abstractmethod
    def get(self, short_code: str) -> Optional[str]:
        """Get URL from cache."""
        pass
    
    @abstractmethod
    def put(self, short_code: str, long_url: str, ttl_seconds: int) -> None:
        """Put URL in cache with TTL."""
        pass
    
    @abstractmethod
    def evict(self, short_code: str) -> None:
        """Remove URL from cache."""
        pass
    
    @abstractmethod
    def exists(self, short_code: str) -> bool:
        """Check if key exists in cache."""
        pass


class MessageQueue(ABC):
    """Message queue interface for async processing."""
    
    @abstractmethod
    def publish_click_event(self, event: ClickEvent) -> None:
        """Publish a click event for async processing."""
        pass


class InMemoryUrlCache(UrlCache):
    """In-memory cache implementation for testing."""
    
    def __init__(self):
        self._store: Dict[str, tuple] = {}  # (value, expires_at)
        self._lock = threading.Lock()
    
    def get(self, short_code: str) -> Optional[str]:
        with self._lock:
            entry = self._store.get(short_code)
            if entry is None:
                return None
            
            value, expires_at = entry
            if time.time() > expires_at:
                del self._store[short_code]
                return None
            
            return value
    
    def put(self, short_code: str, long_url: str, ttl_seconds: int) -> None:
        with self._lock:
            expires_at = time.time() + ttl_seconds
            self._store[short_code] = (long_url, expires_at)
    
    def evict(self, short_code: str) -> None:
        with self._lock:
            self._store.pop(short_code, None)
    
    def exists(self, short_code: str) -> bool:
        return self.get(short_code) is not None


class InMemoryMessageQueue(MessageQueue):
    """In-memory message queue for testing."""
    
    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
    
    def publish_click_event(self, event: ClickEvent) -> None:
        self._queue.put(event)
    
    def drain(self) -> List[ClickEvent]:
        """Get all pending events."""
        events = []
        while True:
            try:
                event = self._queue.get_nowait()
                events.append(event)
            except queue.Empty:
                break
        return events


class CachedUrlShorteningService:
    """
    Scaled URL shortening service with caching.
    Wraps the basic service with cache-aside pattern.
    """
    
    DEFAULT_CACHE_TTL = 86400  # 24 hours
    
    def __init__(self, repository, code_generator, cache: UrlCache,
                 message_queue: MessageQueue, base_url: str):
        self._repository = repository
        self._code_generator = code_generator
        self._cache = cache
        self._message_queue = message_queue
        self._base_url = base_url.rstrip('/')
    
    def create_short_url(self, request) -> dict:
        """Create a new short URL with cache population."""
        from url_shortening_service import UrlEntity
        
        # Validate URL
        self._validate_url(request.long_url)
        
        is_custom = False
        
        if request.has_custom_alias():
            alias = request.custom_alias
            
            if not self._code_generator.is_valid_custom_alias(alias):
                raise ValueError("Invalid custom alias format")
            
            # Check cache first, then database
            if self._cache.exists(alias) or self._repository.exists_by_short_code(alias):
                raise AliasAlreadyExistsError(f"Custom alias already exists: {alias}")
            
            short_code = alias
            is_custom = True
        else:
            short_code = self._code_generator.generate()
            
            attempts = 0
            while ((self._cache.exists(short_code) or 
                    self._repository.exists_by_short_code(short_code)) and 
                   attempts < 5):
                short_code = self._code_generator.generate()
                attempts += 1
        
        # Create and save entity
        entity = UrlEntity(
            short_code=short_code,
            long_url=request.long_url,
            expires_at=request.expires_at,
            user_id=request.user_id,
            is_custom=is_custom
        )
        
        self._repository.save(entity)
        
        # Pre-populate cache (write-through)
        self._cache.put(short_code, request.long_url, self.DEFAULT_CACHE_TTL)
        
        return {
            'short_code': short_code,
            'short_url': f"{self._base_url}/{short_code}",
            'long_url': request.long_url,
            'created_at': entity.created_at,
            'expires_at': request.expires_at
        }
    
    def get_original_url(self, short_code: str) -> Optional[str]:
        """Get original URL with cache-aside pattern."""
        # Try cache first
        cached = self._cache.get(short_code)
        
        if cached:
            # Cache hit - publish analytics asynchronously
            self._publish_click_event(short_code)
            return cached
        
        # Cache miss - query database
        entity = self._repository.find_by_short_code(short_code)
        
        if not entity:
            return None
        
        # Check expiration
        if entity.is_expired():
            self._cache.evict(short_code)
            raise UrlExpiredError(f"URL has expired: {short_code}")
        
        # Populate cache
        self._cache.put(short_code, entity.long_url, self.DEFAULT_CACHE_TTL)
        
        # Publish analytics
        self._publish_click_event(short_code)
        
        return entity.long_url
    
    def get_stats(self, short_code: str) -> Optional[dict]:
        """Get URL statistics."""
        entity = self._repository.find_by_short_code(short_code)
        
        if not entity:
            return None
        
        return {
            'short_code': entity.short_code,
            'long_url': entity.long_url,
            'click_count': entity.click_count,
            'created_at': entity.created_at,
            'expires_at': entity.expires_at
        }
    
    def delete_url(self, short_code: str) -> bool:
        """Delete URL and invalidate cache."""
        deleted = self._repository.delete_by_short_code(short_code)
        
        if deleted:
            self._cache.evict(short_code)
        
        return deleted
    
    def _publish_click_event(self, short_code: str):
        """Publish click event for async processing."""
        event = ClickEvent(short_code=short_code)
        
        try:
            self._message_queue.publish_click_event(event)
        except Exception as e:
            # Log but don't fail the redirect
            print(f"Failed to publish click event: {e}")
    
    def _validate_url(self, url_string: str) -> None:
        """Validate URL format."""
        from urllib.parse import urlparse
        
        if not url_string:
            raise ValueError("URL cannot be empty")
        
        parsed = urlparse(url_string)
        
        if parsed.scheme not in ('http', 'https'):
            raise ValueError("Only HTTP/HTTPS URLs are allowed")
        
        if not parsed.netloc:
            raise ValueError("Invalid URL format")


class AliasAlreadyExistsError(Exception):
    pass


class UrlExpiredError(Exception):
    pass
