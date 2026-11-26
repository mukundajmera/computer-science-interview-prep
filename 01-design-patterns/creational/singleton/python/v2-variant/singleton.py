"""
Singleton Pattern - V2 Pythonic (Module-Level Singleton)

The most Pythonic way to implement Singleton.
In Python, modules are singletons by nature - they're only loaded once.

Pros:
- Very simple and Pythonic
- Thread-safe (module loading is thread-safe)
- No extra classes needed

Cons:
- Less familiar to developers from other languages
- Cannot use inheritance patterns

Usage:
    from singleton_module import config
    config.set_debug(True)
"""

import threading


class _Configuration:
    """Private class - not meant to be instantiated directly."""
    
    def __init__(self):
        self._settings = {}
        self._debug = False
        self._lock = threading.Lock()
        print("Configuration singleton created")
    
    def set(self, key: str, value):
        with self._lock:
            self._settings[key] = value
    
    def get(self, key: str, default=None):
        return self._settings.get(key, default)
    
    def set_debug(self, enabled: bool):
        self._debug = enabled
        print(f"Debug mode: {'enabled' if enabled else 'disabled'}")
    
    def is_debug(self):
        return self._debug
    
    def load_from_file(self, filepath: str):
        """Simulate loading config from file."""
        print(f"Loading configuration from: {filepath}")
        # In real implementation, parse file and update _settings
        self._settings['loaded_from'] = filepath


# Module-level singleton instance - created once when module is imported
config = _Configuration()


# Alternative: Thread-safe Singleton with Lock
class ThreadSafeSingleton:
    """Thread-safe Singleton using double-checked locking."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        # Double-checked locking pattern
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print("Creating ThreadSafeSingleton instance")
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.data = {}
        self._initialized = True


# Demo
if __name__ == "__main__":
    print("=== Module-Level Singleton Demo ===")
    
    # The 'config' instance is already created when module is imported
    config.set("database.host", "localhost")
    config.set("database.port", 5432)
    config.set_debug(True)
    
    print(f"database.host: {config.get('database.host')}")
    print(f"database.port: {config.get('database.port')}")
    
    # Demonstrate it's the same instance
    from singleton import config as config2
    print(f"\nSame instance? {config is config2}")
    print(f"config2 sees same settings: {config2.get('database.host')}")
    
    print("\n=== Thread-Safe Singleton Demo ===")
    
    def create_instance(thread_id):
        instance = ThreadSafeSingleton()
        print(f"Thread {thread_id}: instance id = {id(instance)}")
        return instance
    
    threads = []
    for i in range(5):
        t = threading.Thread(target=create_instance, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("All threads got the same instance!")
