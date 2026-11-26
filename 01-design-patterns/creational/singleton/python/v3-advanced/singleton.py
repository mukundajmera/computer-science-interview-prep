"""
Singleton Pattern - V3 Advanced (Metaclass Singleton)

The most powerful Python Singleton implementation.
Uses metaclass to control class instantiation.

Pros:
- Works with inheritance
- Thread-safe
- Clean separation of concerns
- Can be reused for multiple classes

Cons:
- More complex to understand
- Metaclass conflicts possible with other metaclasses
"""

import threading
from typing import Dict, Any


class SingletonMeta(type):
    """
    Metaclass for creating Singleton classes.
    
    Thread-safe implementation using double-checked locking.
    Any class using this metaclass becomes a Singleton.
    """
    
    _instances: Dict[type, Any] = {}
    _lock: threading.Lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        # Double-checked locking for thread safety
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class Logger(metaclass=SingletonMeta):
    """
    Example: Thread-safe Logger Singleton.
    
    Usage:
        logger = Logger()
        logger.info("Application started")
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self._log_file = None
        self._level = "INFO"
        self._lock = threading.Lock()
        print(f"Logger '{name}' initialized")
    
    def set_level(self, level: str):
        self._level = level.upper()
    
    def _log(self, level: str, message: str):
        with self._lock:
            log_entry = f"[{level}] {self.name}: {message}"
            print(log_entry)
            if self._log_file:
                # In real implementation, write to file
                pass
    
    def debug(self, message: str):
        if self._level in ("DEBUG",):
            self._log("DEBUG", message)
    
    def info(self, message: str):
        if self._level in ("DEBUG", "INFO"):
            self._log("INFO", message)
    
    def warning(self, message: str):
        if self._level in ("DEBUG", "INFO", "WARNING"):
            self._log("WARNING", message)
    
    def error(self, message: str):
        self._log("ERROR", message)


class DatabasePool(metaclass=SingletonMeta):
    """
    Example: Database Connection Pool Singleton.
    
    Manages a pool of database connections.
    Only one pool exists for the entire application.
    """
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._connections = []
        self._available = []
        self._lock = threading.Lock()
        print(f"DatabasePool created with max {max_connections} connections")
    
    def get_connection(self):
        with self._lock:
            if self._available:
                conn = self._available.pop()
                print(f"Reusing connection: {conn}")
                return conn
            elif len(self._connections) < self.max_connections:
                conn = f"Connection-{len(self._connections) + 1}"
                self._connections.append(conn)
                print(f"Created new connection: {conn}")
                return conn
            else:
                raise RuntimeError("No connections available")
    
    def release_connection(self, conn):
        with self._lock:
            if conn in self._connections:
                self._available.append(conn)
                print(f"Released connection: {conn}")


# Decorator-based Singleton (alternative approach)
def singleton(cls):
    """
    Decorator to make a class a Singleton.
    
    Usage:
        @singleton
        class MyClass:
            pass
    """
    instances = {}
    lock = threading.Lock()
    
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


@singleton
class CacheManager:
    """Example using decorator-based Singleton."""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._lock = threading.Lock()
        print("CacheManager initialized")
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        with self._lock:
            self._cache[key] = {"value": value, "ttl": ttl}
    
    def get(self, key: str, default=None):
        return self._cache.get(key, {}).get("value", default)
    
    def delete(self, key: str):
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self):
        with self._lock:
            self._cache.clear()


# Demo
if __name__ == "__main__":
    print("=== Metaclass Singleton Demo ===\n")
    
    # Logger Singleton
    print("--- Logger ---")
    logger1 = Logger("MyApp")
    logger2 = Logger("AnotherName")  # Same instance, name ignored
    
    print(f"Same instance? {logger1 is logger2}")
    logger1.info("Application started")
    logger2.warning("This warning comes from the same logger")
    
    # Database Pool Singleton
    print("\n--- DatabasePool ---")
    pool1 = DatabasePool(max_connections=5)
    pool2 = DatabasePool(max_connections=100)  # Ignored, same instance
    
    print(f"Same instance? {pool1 is pool2}")
    print(f"Max connections: {pool2.max_connections}")  # Still 5
    
    conn = pool1.get_connection()
    pool2.release_connection(conn)
    
    # Decorator-based Singleton
    print("\n--- Decorator Singleton ---")
    cache1 = CacheManager()
    cache2 = CacheManager()
    
    print(f"Same instance? {cache1 is cache2}")
    cache1.set("user:123", {"name": "Alice", "age": 30})
    print(f"cache2.get('user:123'): {cache2.get('user:123')}")
    
    # Thread safety test
    print("\n--- Thread Safety Test ---")
    results = []
    
    def worker(thread_id):
        logger = Logger()
        results.append(id(logger))
        logger.info(f"Thread {thread_id} active")
    
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    print(f"All threads got same instance: {len(set(results)) == 1}")
