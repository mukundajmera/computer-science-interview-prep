"""
Online Shopping Cart - V1 Basic
Core entities for the shopping cart system.
"""

from typing import List, Dict, Optional
from datetime import datetime


class Category:
    """Represents a product category."""
    
    def __init__(self, id: str, name: str, parent: Optional['Category'] = None):
        self.id = id
        self.name = name
        self.parent = parent
    
    def __str__(self) -> str:
        return self.name


class Product:
    """Represents a product."""
    
    def __init__(self, id: str, name: str, description: str, 
                 price: float, category: Optional[Category] = None, weight: float = 0.0):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.weight = weight
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Product):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __str__(self) -> str:
        return f"{self.name} - ${self.price:.2f}"


class CartItem:
    """Represents an item in the cart."""
    
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity
        self.price_at_add = product.price
        self.added_at = datetime.now()
    
    def add_quantity(self, amount: int) -> None:
        self.quantity += amount
    
    def get_subtotal(self) -> float:
        return self.price_at_add * self.quantity
    
    def __str__(self) -> str:
        return f"{self.product.name} x{self.quantity} = ${self.get_subtotal():.2f}"


class Cart:
    """Represents a shopping cart."""
    
    def __init__(self, id: str, user_id: str):
        self.id = id
        self.user_id = user_id
        self._items: Dict[str, CartItem] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_item(self, product: Product, quantity: int) -> None:
        """Add a product to the cart."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if product.id in self._items:
            self._items[product.id].add_quantity(quantity)
        else:
            self._items[product.id] = CartItem(product, quantity)
        
        self._update_timestamp()
    
    def remove_item(self, product_id: str) -> bool:
        """Remove a product from the cart."""
        if product_id in self._items:
            del self._items[product_id]
            self._update_timestamp()
            return True
        return False
    
    def update_quantity(self, product_id: str, quantity: int) -> bool:
        """Update quantity of a product."""
        if product_id not in self._items:
            return False
        
        if quantity <= 0:
            return self.remove_item(product_id)
        
        self._items[product_id].quantity = quantity
        self._update_timestamp()
        return True
    
    def clear(self) -> None:
        """Clear all items from the cart."""
        self._items.clear()
        self._update_timestamp()
    
    def get_items(self) -> List[CartItem]:
        """Get all cart items."""
        return list(self._items.values())
    
    def get_item(self, product_id: str) -> Optional[CartItem]:
        """Get a specific cart item."""
        return self._items.get(product_id)
    
    def get_total_items(self) -> int:
        """Get total number of items (sum of quantities)."""
        return sum(item.quantity for item in self._items.values())
    
    def get_unique_products(self) -> int:
        """Get number of unique products."""
        return len(self._items)
    
    def is_empty(self) -> bool:
        """Check if cart is empty."""
        return len(self._items) == 0
    
    def get_subtotal(self) -> float:
        """Calculate subtotal (before discounts, tax, shipping)."""
        return sum(item.get_subtotal() for item in self._items.values())
    
    def get_total_weight(self) -> float:
        """Calculate total weight."""
        return sum(item.product.weight * item.quantity for item in self._items.values())
    
    def _update_timestamp(self) -> None:
        self.updated_at = datetime.now()
    
    def display(self) -> None:
        """Display cart contents."""
        print(f"\n=== Shopping Cart ===")
        print(f"Cart ID: {self.id}")
        print(f"User: {self.user_id}")
        print("---")
        
        if self.is_empty():
            print("Cart is empty")
        else:
            for item in self._items.values():
                print(item)
            print("---")
            print(f"Subtotal: ${self.get_subtotal():.2f}")
            print(f"Total Items: {self.get_total_items()}")
    
    def __str__(self) -> str:
        return f"Cart[{self.id}] - {self.get_total_items()} items, ${self.get_subtotal():.2f}"


class Inventory:
    """Simple inventory management."""
    
    def __init__(self):
        self._stock: Dict[str, int] = {}
    
    def add_stock(self, product_id: str, quantity: int) -> None:
        self._stock[product_id] = self._stock.get(product_id, 0) + quantity
    
    def get_stock(self, product_id: str) -> int:
        return self._stock.get(product_id, 0)
    
    def check_stock(self, product_id: str, quantity: int) -> bool:
        return self.get_stock(product_id) >= quantity
    
    def deduct_stock(self, product_id: str, quantity: int) -> bool:
        current = self.get_stock(product_id)
        if current >= quantity:
            self._stock[product_id] = current - quantity
            return True
        return False


class ShoppingService:
    """Shopping cart service (Singleton)."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._products: Dict[str, Product] = {}
        self._categories: Dict[str, Category] = {}
        self._carts: Dict[str, Cart] = {}
        self._inventory = Inventory()
        self._cart_counter = 0
        self._initialized = True
    
    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None
    
    # Product management
    def add_category(self, category: Category) -> None:
        self._categories[category.id] = category
    
    def add_product(self, product: Product, initial_stock: int = 0) -> None:
        self._products[product.id] = product
        self._inventory.add_stock(product.id, initial_stock)
    
    def get_product(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)
    
    def search_products(self, query: str) -> List[Product]:
        query_lower = query.lower()
        return [p for p in self._products.values()
                if query_lower in p.name.lower() or query_lower in p.description.lower()]
    
    def get_products_by_category(self, category_id: str) -> List[Product]:
        return [p for p in self._products.values()
                if p.category and p.category.id == category_id]
    
    # Cart management
    def create_cart(self, user_id: str) -> Cart:
        self._cart_counter += 1
        cart_id = f"CART-{self._cart_counter}"
        cart = Cart(cart_id, user_id)
        self._carts[cart_id] = cart
        return cart
    
    def get_cart(self, cart_id: str) -> Optional[Cart]:
        return self._carts.get(cart_id)
    
    def add_to_cart(self, cart_id: str, product_id: str, quantity: int) -> bool:
        cart = self._carts.get(cart_id)
        product = self._products.get(product_id)
        
        if not cart or not product:
            return False
        
        # Check inventory
        existing = cart.get_item(product_id)
        total_required = quantity + (existing.quantity if existing else 0)
        
        if not self._inventory.check_stock(product_id, total_required):
            print(f"Insufficient stock for {product.name}")
            return False
        
        cart.add_item(product, quantity)
        return True
    
    def remove_from_cart(self, cart_id: str, product_id: str) -> bool:
        cart = self._carts.get(cart_id)
        if not cart:
            return False
        return cart.remove_item(product_id)
    
    def update_cart_quantity(self, cart_id: str, product_id: str, quantity: int) -> bool:
        cart = self._carts.get(cart_id)
        if not cart:
            return False
        
        if quantity > 0 and not self._inventory.check_stock(product_id, quantity):
            print("Insufficient stock")
            return False
        
        return cart.update_quantity(product_id, quantity)
    
    # Checkout
    def checkout(self, cart_id: str) -> bool:
        cart = self._carts.get(cart_id)
        if not cart or cart.is_empty():
            print("Cart is empty or not found")
            return False
        
        # Verify and deduct inventory
        for item in cart.get_items():
            if not self._inventory.deduct_stock(item.product.id, item.quantity):
                print(f"Checkout failed: insufficient stock for {item.product.name}")
                return False
        
        total = cart.get_subtotal()
        cart.clear()
        
        print(f"Checkout successful! Total: ${total:.2f}")
        return True
    
    @property
    def inventory(self) -> Inventory:
        return self._inventory
