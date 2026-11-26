"""Shopping Cart Enums and Models."""
from enum import Enum
from typing import Dict

class OrderStatus(Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class Category:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

class Product:
    def __init__(self, id: str, name: str, description: str, price: float, category: Category, weight: float = 0):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.weight = weight
    def __str__(self): return f"{self.name} (${self.price:.2f})"

class CartItem:
    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity
    @property
    def subtotal(self): return self.product.price * self.quantity
    def __str__(self): return f"{self.product.name} x{self.quantity} = ${self.subtotal:.2f}"

class Cart:
    def __init__(self, id: str, user_id: str):
        self.id = id
        self.user_id = user_id
        self._items: Dict[str, CartItem] = {}
    
    def add_item(self, product: Product, qty: int):
        if product.id in self._items:
            self._items[product.id].quantity += qty
        else:
            self._items[product.id] = CartItem(product, qty)
    
    def update_quantity(self, product_id: str, qty: int):
        if product_id in self._items: self._items[product_id].quantity = qty
    
    def remove_item(self, product_id: str): self._items.pop(product_id, None)
    def clear(self): self._items.clear()
    
    @property
    def total(self): return sum(item.subtotal for item in self._items.values())
    
    def display(self):
        print(f"\n=== Cart {self.id} ===")
        for item in self._items.values(): print(item)
        print(f"Total: ${self.total:.2f}")

class ShoppingService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.products = {}
            cls._instance.carts = {}
            cls._instance._cart_counter = 0
        return cls._instance
    
    def add_product(self, p: Product): self.products[p.id] = p
    
    def create_cart(self, user_id: str) -> Cart:
        self._cart_counter += 1
        cart = Cart(f"CART-{self._cart_counter}", user_id)
        self.carts[cart.id] = cart
        return cart
    
    def add_to_cart(self, cart_id: str, product_id: str, qty: int):
        cart = self.carts.get(cart_id)
        product = self.products.get(product_id)
        if cart and product: cart.add_item(product, qty)
    
    def checkout(self, cart_id: str):
        cart = self.carts.get(cart_id)
        if cart:
            print(f"Order placed! Total: ${cart.total:.2f}")
            cart.clear()
