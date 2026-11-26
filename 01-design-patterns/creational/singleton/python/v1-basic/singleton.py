"""
Singleton Pattern - V1 Basic (Using __new__)

The most common Python Singleton implementation.
Uses __new__ to control instance creation.

Pros:
- Simple and straightforward
- Thread-safe for most use cases

Cons:
- __init__ is called every time getInstance/() is called
- Not truly thread-safe under race conditions
"""


class Singleton:
    """Basic Singleton using __new__ method."""
    
    _instances = {}
    
    def __new__(cls):
        if cls not in cls._instances:
            print("Creating new Singleton instance")
            instance = super().__new__(cls)
            cls._instances[cls] = instance
            instance._initialized = False
        return cls._instances[cls]
    
    def __init__(self):
        # Prevent re-initialization
        if self._initialized:
            return
        
        print("Initializing Singleton")
        self.value = None
        self._initialized = True
    
    def set_value(self, value):
        self.value = value
    
    def get_value(self):
        return self.value


class DatabaseConnection(Singleton):
    """Example: Database connection as Singleton."""
    
    def __init__(self):
        if getattr(self, '_db_initialized', False):
            return
        
        super().__init__()
        self.host = "localhost"
        self.port = 5432
        self.connected = False
        self._db_initialized = True
        print(f"Database connection configured: {self.host}:{self.port}")
    
    def connect(self):
        if not self.connected:
            print(f"Connecting to {self.host}:{self.port}")
            self.connected = True
        else:
            print("Already connected")
    
    def disconnect(self):
        if self.connected:
            print("Disconnecting...")
            self.connected = False
    
    def execute_query(self, query: str):
        if self.connected:
            print(f"Executing: {query}")
            return f"Result of: {query}"
        else:
            raise RuntimeError("Not connected to database")


# Demo
if __name__ == "__main__":
    print("=== Basic Singleton Demo ===")
    
    s1 = Singleton()
    s2 = Singleton()
    
    print(f"s1 id: {id(s1)}")
    print(f"s2 id: {id(s2)}")
    print(f"Same instance? {s1 is s2}")
    
    s1.set_value("Hello")
    print(f"s2.get_value(): {s2.get_value()}")  # Same instance!
    
    print("\n=== Database Connection Demo ===")
    
    db1 = DatabaseConnection()
    db2 = DatabaseConnection()
    
    print(f"Same instance? {db1 is db2}")
    
    db1.connect()
    print(f"db2.connected: {db2.connected}")  # True, same instance
    
    db1.execute_query("SELECT * FROM users")
    db2.disconnect()
