"""
URL Shortener Service - V1 Basic

Core URL shortening service implementation in Python.
This version provides basic functionality without caching or scaling.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List
from abc import ABC, abstractmethod
import re
from urllib.parse import urlparse


@dataclass
class CreateUrlRequest:
    """Request DTO for creating a short URL."""
    long_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None
    
    def has_custom_alias(self) -> bool:
        return self.custom_alias is not None and len(self.custom_alias) > 0


@dataclass
class CreateUrlResponse:
    """Response DTO for short URL creation."""
    short_code: str
    short_url: str
    long_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class UrlStats:
    """URL statistics DTO."""
    short_code: str
    long_url: str
    click_count: int
    created_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class UrlEntity:
    """Domain entity representing a shortened URL."""
    short_code: str
    long_url: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None
    is_custom: bool = False
    click_count: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if this URL has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def increment_click_count(self):
        """Increment click count for analytics."""
        self.click_count += 1


class UrlShorteningService(ABC):
    """Abstract interface for URL shortening operations."""
    
    @abstractmethod
    def create_short_url(self, request: CreateUrlRequest) -> CreateUrlResponse:
        """Creates a short URL for the given long URL."""
        pass
    
    @abstractmethod
    def get_original_url(self, short_code: str) -> Optional[str]:
        """Retrieves the original URL for a given short code."""
        pass
    
    @abstractmethod
    def get_stats(self, short_code: str) -> Optional[UrlStats]:
        """Gets analytics for a short URL."""
        pass
    
    @abstractmethod
    def delete_url(self, short_code: str) -> bool:
        """Deletes a short URL."""
        pass


class UrlRepository(ABC):
    """Abstract repository interface for URL persistence."""
    
    @abstractmethod
    def save(self, entity: UrlEntity) -> None:
        """Save a URL entity to storage."""
        pass
    
    @abstractmethod
    def find_by_short_code(self, short_code: str) -> Optional[UrlEntity]:
        """Find a URL by its short code."""
        pass
    
    @abstractmethod
    def find_by_long_url(self, long_url: str) -> Optional[UrlEntity]:
        """Find a URL by the original long URL."""
        pass
    
    @abstractmethod
    def delete_by_short_code(self, short_code: str) -> bool:
        """Delete a URL by its short code."""
        pass
    
    @abstractmethod
    def exists_by_short_code(self, short_code: str) -> bool:
        """Check if a short code already exists."""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: str) -> List[UrlEntity]:
        """Find all URLs for a user."""
        pass
    
    @abstractmethod
    def increment_click_count(self, short_code: str) -> None:
        """Increment click count for a URL."""
        pass


class InMemoryUrlRepository(UrlRepository):
    """In-memory implementation for development/testing."""
    
    def __init__(self):
        self._url_store: Dict[str, UrlEntity] = {}
        self._long_url_index: Dict[str, str] = {}
    
    def save(self, entity: UrlEntity) -> None:
        self._url_store[entity.short_code] = entity
        self._long_url_index[entity.long_url] = entity.short_code
    
    def find_by_short_code(self, short_code: str) -> Optional[UrlEntity]:
        return self._url_store.get(short_code)
    
    def find_by_long_url(self, long_url: str) -> Optional[UrlEntity]:
        short_code = self._long_url_index.get(long_url)
        if short_code:
            return self.find_by_short_code(short_code)
        return None
    
    def delete_by_short_code(self, short_code: str) -> bool:
        entity = self._url_store.pop(short_code, None)
        if entity:
            self._long_url_index.pop(entity.long_url, None)
            return True
        return False
    
    def exists_by_short_code(self, short_code: str) -> bool:
        return short_code in self._url_store
    
    def find_by_user_id(self, user_id: str) -> List[UrlEntity]:
        return [
            entity for entity in self._url_store.values()
            if entity.user_id == user_id
        ]
    
    def increment_click_count(self, short_code: str) -> None:
        entity = self._url_store.get(short_code)
        if entity:
            entity.increment_click_count()


class ShortCodeGenerator(ABC):
    """Abstract interface for generating unique short codes."""
    
    @abstractmethod
    def generate(self) -> str:
        """Generate a new unique short code."""
        pass
    
    @abstractmethod
    def is_valid_custom_alias(self, alias: str) -> bool:
        """Validate if a custom alias is acceptable."""
        pass


class CounterBasedGenerator(ShortCodeGenerator):
    """Counter-based short code generator using Base62 encoding."""
    
    BASE62_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    CODE_LENGTH = 7
    
    def __init__(self, start_value: int = 100_000_000):
        self._counter = start_value
    
    def generate(self) -> str:
        self._counter += 1
        return self._encode_base62(self._counter)
    
    def _encode_base62(self, number: int) -> str:
        """Encode a number to base62 string."""
        if number == 0:
            return self.BASE62_CHARS[0]
        
        result = []
        while number > 0:
            result.append(self.BASE62_CHARS[number % 62])
            number //= 62
        
        # Reverse and pad
        code = ''.join(reversed(result))
        return code.rjust(self.CODE_LENGTH, 'a')
    
    def decode_base62(self, code: str) -> int:
        """Decode a base62 string back to number."""
        result = 0
        for char in code:
            result = result * 62 + self.BASE62_CHARS.index(char)
        return result
    
    def is_valid_custom_alias(self, alias: str) -> bool:
        """Validate custom alias format."""
        if not alias or len(alias) < 3 or len(alias) > 20:
            return False
        
        # Allow alphanumeric, hyphens, and underscores
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
        if len(alias) == 1:
            pattern = r'^[a-zA-Z0-9]$'
        elif len(alias) == 2:
            pattern = r'^[a-zA-Z0-9]{2}$'
        
        return bool(re.match(pattern, alias))


# Custom exceptions
class AliasAlreadyExistsError(Exception):
    """Exception for duplicate custom aliases."""
    pass


class UrlExpiredError(Exception):
    """Exception for expired URLs."""
    pass


class UrlNotFoundError(Exception):
    """Exception for URL not found."""
    pass


class BasicUrlShorteningService(UrlShorteningService):
    """Basic implementation of URL shortening service."""
    
    def __init__(self, repository: UrlRepository, 
                 code_generator: ShortCodeGenerator,
                 base_url: str):
        self._repository = repository
        self._code_generator = code_generator
        self._base_url = base_url.rstrip('/')
    
    def create_short_url(self, request: CreateUrlRequest) -> CreateUrlResponse:
        """Create a new short URL."""
        # Validate URL format
        self._validate_url(request.long_url)
        
        is_custom = False
        
        if request.has_custom_alias():
            # Custom alias requested
            alias = request.custom_alias
            
            if not self._code_generator.is_valid_custom_alias(alias):
                raise ValueError("Invalid custom alias format")
            
            if self._repository.exists_by_short_code(alias):
                raise AliasAlreadyExistsError(f"Custom alias already exists: {alias}")
            
            short_code = alias
            is_custom = True
        else:
            # Generate unique code
            short_code = self._code_generator.generate()
            
            # Handle collision
            attempts = 0
            while self._repository.exists_by_short_code(short_code) and attempts < 5:
                short_code = self._code_generator.generate()
                attempts += 1
            
            if self._repository.exists_by_short_code(short_code):
                raise RuntimeError("Failed to generate unique short code")
        
        # Create and save entity
        entity = UrlEntity(
            short_code=short_code,
            long_url=request.long_url,
            expires_at=request.expires_at,
            user_id=request.user_id,
            is_custom=is_custom
        )
        
        self._repository.save(entity)
        
        return CreateUrlResponse(
            short_code=short_code,
            short_url=f"{self._base_url}/{short_code}",
            long_url=request.long_url,
            created_at=entity.created_at,
            expires_at=request.expires_at
        )
    
    def get_original_url(self, short_code: str) -> Optional[str]:
        """Get original URL for redirect."""
        entity = self._repository.find_by_short_code(short_code)
        
        if not entity:
            return None
        
        # Check expiration
        if entity.is_expired():
            raise UrlExpiredError(f"URL has expired: {short_code}")
        
        # Increment click count
        self._repository.increment_click_count(short_code)
        
        return entity.long_url
    
    def get_stats(self, short_code: str) -> Optional[UrlStats]:
        """Get URL statistics."""
        entity = self._repository.find_by_short_code(short_code)
        
        if not entity:
            return None
        
        return UrlStats(
            short_code=entity.short_code,
            long_url=entity.long_url,
            click_count=entity.click_count,
            created_at=entity.created_at,
            expires_at=entity.expires_at
        )
    
    def delete_url(self, short_code: str) -> bool:
        """Delete a short URL."""
        return self._repository.delete_by_short_code(short_code)
    
    def _validate_url(self, url_string: str) -> None:
        """Validate URL format."""
        if not url_string:
            raise ValueError("URL cannot be empty")
        
        try:
            parsed = urlparse(url_string)
            
            if parsed.scheme not in ('http', 'https'):
                raise ValueError("Only HTTP/HTTPS URLs are allowed")
            
            if not parsed.netloc:
                raise ValueError("Invalid URL format")
                
        except Exception as e:
            raise ValueError(f"Invalid URL format: {url_string}") from e
