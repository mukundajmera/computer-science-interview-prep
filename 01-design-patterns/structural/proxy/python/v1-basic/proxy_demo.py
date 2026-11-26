"""
Proxy Pattern - Python Implementations
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Set
from dataclasses import dataclass
import time


# ============ V1: Virtual Proxy ============

class Image(ABC):
    @abstractmethod
    def display(self) -> None: pass
    @abstractmethod
    def get_dimensions(self) -> tuple: pass


class RealImage(Image):
    def __init__(self, filename: str):
        self.filename = filename
        self._load_from_disk()
    
    def _load_from_disk(self):
        print(f"Loading image: {self.filename}")
        time.sleep(0.5)  # Simulate loading
        self.width, self.height = 1920, 1080
    
    def display(self): print(f"Displaying: {self.filename}")
    def get_dimensions(self): return (self.width, self.height)


class ProxyImage(Image):
    def __init__(self, filename: str):
        self.filename = filename
        self._real: Optional[RealImage] = None
    
    def _get_real(self) -> RealImage:
        if not self._real:
            self._real = RealImage(self.filename)
        return self._real
    
    def display(self): self._get_real().display()
    def get_dimensions(self): return self._get_real().get_dimensions()


# ============ V2: Protection Proxy ============

@dataclass
class User:
    username: str
    roles: Set[str]
    
    def has_role(self, role: str) -> bool:
        return role in self.roles


class Document(ABC):
    @abstractmethod
    def read(self) -> str: pass
    @abstractmethod
    def write(self, content: str) -> None: pass


class RealDocument(Document):
    def __init__(self, name: str):
        self.name = name
        self.content = f"Content of {name}"
    
    def read(self) -> str: return self.content
    def write(self, content: str): self.content = content


class ProtectedDocument(Document):
    def __init__(self, doc: RealDocument, user: User):
        self._doc = doc
        self._user = user
    
    def read(self) -> str:
        if self._user.has_role("reader") or self._user.has_role("admin"):
            return self._doc.read()
        raise PermissionError("No read access")
    
    def write(self, content: str):
        if self._user.has_role("writer") or self._user.has_role("admin"):
            self._doc.write(content)
        else:
            raise PermissionError("No write access")


# ============ V3: Caching Proxy ============

class DataService(ABC):
    @abstractmethod
    def fetch(self, key: str) -> str: pass


class DatabaseService(DataService):
    def __init__(self):
        self._data = {"user:1": "Alice", "user:2": "Bob"}
    
    def fetch(self, key: str) -> str:
        print(f"[DB] Fetching: {key}")
        time.sleep(0.3)
        return self._data.get(key, "")


class CachingProxy(DataService):
    def __init__(self, service: DataService, ttl: float = 60):
        self._service = service
        self._cache: Dict[str, tuple] = {}
        self._ttl = ttl
        self.hits = 0
        self.misses = 0
    
    def fetch(self, key: str) -> str:
        if key in self._cache:
            value, expire = self._cache[key]
            if time.time() < expire:
                self.hits += 1
                print(f"[CACHE] Hit: {key}")
                return value
        
        self.misses += 1
        print(f"[CACHE] Miss: {key}")
        value = self._service.fetch(key)
        self._cache[key] = (value, time.time() + self._ttl)
        return value
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total else 0


if __name__ == "__main__":
    # Virtual Proxy
    print("=== Virtual Proxy ===")
    proxy = ProxyImage("photo.jpg")
    print("Proxy created, image not loaded yet")
    proxy.display()  # Loads now
    
    # Protection Proxy
    print("\n=== Protection Proxy ===")
    doc = RealDocument("secret.txt")
    admin = User("admin", {"admin"})
    guest = User("guest", set())
    
    admin_proxy = ProtectedDocument(doc, admin)
    print(admin_proxy.read())  # Works
    
    guest_proxy = ProtectedDocument(doc, guest)
    try:
        guest_proxy.read()  # Fails
    except PermissionError as e:
        print(f"Error: {e}")
    
    # Caching Proxy
    print("\n=== Caching Proxy ===")
    cached = CachingProxy(DatabaseService())
    cached.fetch("user:1")  # Miss
    cached.fetch("user:1")  # Hit
    print(f"Hit rate: {cached.hit_rate:.1f}%")
