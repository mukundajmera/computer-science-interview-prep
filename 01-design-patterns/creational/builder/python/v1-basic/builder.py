"""
Builder Pattern - V1 Basic (Fluent Builder)

Python implementation using inner class and fluent interface.
"""

from typing import List, Optional
from dataclasses import dataclass, field


# Product class - using dataclass for immutability
@dataclass(frozen=True)
class Pizza:
    """Immutable Pizza product."""
    size: str
    crust: str
    sauce: str
    toppings: tuple  # Tuple for immutability
    extra_cheese: bool
    gluten_free: bool
    
    def __str__(self) -> str:
        return (
            f"Pizza [{self.size}, {self.crust} crust, {self.sauce} sauce, "
            f"toppings={list(self.toppings)}, extraCheese={self.extra_cheese}, "
            f"glutenFree={self.gluten_free}]"
        )
    
    class Builder:
        """Fluent builder for Pizza."""
        
        def __init__(self, size: str):
            """Size is required."""
            self._size = size
            self._crust = "regular"
            self._sauce = "tomato"
            self._toppings: List[str] = []
            self._extra_cheese = False
            self._gluten_free = False
        
        def crust(self, crust: str) -> 'Pizza.Builder':
            self._crust = crust
            return self
        
        def sauce(self, sauce: str) -> 'Pizza.Builder':
            self._sauce = sauce
            return self
        
        def add_topping(self, topping: str) -> 'Pizza.Builder':
            self._toppings.append(topping)
            return self
        
        def extra_cheese(self) -> 'Pizza.Builder':
            self._extra_cheese = True
            return self
        
        def gluten_free(self) -> 'Pizza.Builder':
            self._gluten_free = True
            return self
        
        def build(self) -> 'Pizza':
            """Build and return immutable Pizza."""
            if not self._size:
                raise ValueError("Size is required")
            
            return Pizza(
                size=self._size,
                crust=self._crust,
                sauce=self._sauce,
                toppings=tuple(self._toppings),
                extra_cheese=self._extra_cheese,
                gluten_free=self._gluten_free
            )


@dataclass(frozen=True)
class Computer:
    """Immutable Computer product."""
    cpu: str
    ram: int
    storage: int
    gpu: str
    bluetooth: bool
    wifi: bool
    
    def __str__(self) -> str:
        return (
            f"Computer [CPU={self.cpu}, RAM={self.ram}GB, Storage={self.storage}GB, "
            f"GPU={self.gpu}, BT={self.bluetooth}, WiFi={self.wifi}]"
        )
    
    class Builder:
        """Fluent builder for Computer."""
        
        def __init__(self, cpu: str, ram: int):
            """CPU and RAM are required."""
            self._cpu = cpu
            self._ram = ram
            self._storage = 256
            self._gpu = "Integrated"
            self._bluetooth = True
            self._wifi = True
        
        def storage(self, gb: int) -> 'Computer.Builder':
            self._storage = gb
            return self
        
        def gpu(self, gpu: str) -> 'Computer.Builder':
            self._gpu = gpu
            return self
        
        def no_bluetooth(self) -> 'Computer.Builder':
            self._bluetooth = False
            return self
        
        def no_wifi(self) -> 'Computer.Builder':
            self._wifi = False
            return self
        
        def build(self) -> 'Computer':
            """Build and return immutable Computer."""
            if self._ram < 4:
                raise ValueError("Minimum 4GB RAM required")
            
            return Computer(
                cpu=self._cpu,
                ram=self._ram,
                storage=self._storage,
                gpu=self._gpu,
                bluetooth=self._bluetooth,
                wifi=self._wifi
            )


# Alternative: Pythonic approach using **kwargs
class HttpRequest:
    """
    Alternative Pythonic builder using method chaining.
    """
    
    def __init__(self, url: str):
        self.url = url
        self.method = "GET"
        self.headers = {}
        self.body = None
        self.timeout = 30
    
    def post(self) -> 'HttpRequest':
        self.method = "POST"
        return self
    
    def put(self) -> 'HttpRequest':
        self.method = "PUT"
        return self
    
    def delete(self) -> 'HttpRequest':
        self.method = "DELETE"
        return self
    
    def with_header(self, key: str, value: str) -> 'HttpRequest':
        self.headers[key] = value
        return self
    
    def with_json(self, data: dict) -> 'HttpRequest':
        self.headers["Content-Type"] = "application/json"
        self.body = data
        return self
    
    def with_timeout(self, seconds: int) -> 'HttpRequest':
        self.timeout = seconds
        return self
    
    def build(self) -> 'HttpRequest':
        """Validate and return."""
        if not self.url:
            raise ValueError("URL is required")
        return self
    
    def __str__(self) -> str:
        return f"HttpRequest [{self.method} {self.url}, headers={self.headers}, timeout={self.timeout}s]"


# Demo
if __name__ == "__main__":
    print("=== Builder Pattern Demo ===\n")
    
    print("--- Building Pizzas ---\n")
    
    # Simple pizza
    margherita = Pizza.Builder("medium").build()
    print(f"Margherita: {margherita}")
    
    # Customized pizza
    meat = (Pizza.Builder("large")
            .crust("thick")
            .sauce("bbq")
            .add_topping("pepperoni")
            .add_topping("sausage")
            .add_topping("bacon")
            .extra_cheese()
            .build())
    print(f"Meat Lovers: {meat}")
    
    # Healthy pizza
    veggie = (Pizza.Builder("small")
              .crust("thin")
              .gluten_free()
              .add_topping("spinach")
              .add_topping("tomatoes")
              .add_topping("mushrooms")
              .build())
    print(f"Veggie: {veggie}")
    
    print("\n--- Building Computers ---\n")
    
    # Basic computer
    basic = Computer.Builder("Intel i5", 8).build()
    print(f"Basic: {basic}")
    
    # Gaming computer
    gaming = (Computer.Builder("Intel i9", 32)
              .storage(2000)
              .gpu("RTX 4090")
              .build())
    print(f"Gaming: {gaming}")
    
    # Server
    server = (Computer.Builder("AMD EPYC", 128)
              .storage(8000)
              .no_bluetooth()
              .no_wifi()
              .build())
    print(f"Server: {server}")
    
    print("\n--- Building HTTP Requests ---\n")
    
    # GET request
    get_request = (HttpRequest("https://api.example.com/users")
                   .with_header("Authorization", "Bearer token123")
                   .with_timeout(10)
                   .build())
    print(f"GET: {get_request}")
    
    # POST request
    post_request = (HttpRequest("https://api.example.com/users")
                    .post()
                    .with_json({"name": "Alice", "email": "alice@example.com"})
                    .with_header("X-API-Key", "secret")
                    .build())
    print(f"POST: {post_request}")
