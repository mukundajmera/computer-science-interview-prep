"""Restaurant Management Python Module - New."""
from enum import Enum
from typing import Dict, List

class OrderStatus(Enum):
    PLACED = "PLACED"
    PREPARING = "PREPARING"
    READY = "READY"
    SERVED = "SERVED"
    PAID = "PAID"

class TableStatus(Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    RESERVED = "RESERVED"
    CLEANING = "CLEANING"

class Table:
    def __init__(self, number: int, capacity: int):
        self.number = number
        self.capacity = capacity
        self.status = TableStatus.AVAILABLE

class MenuItem:
    def __init__(self, id: str, name: str, price: float, category: str):
        self.id = id
        self.name = name
        self.price = price
        self.category = category

class Order:
    def __init__(self, id: str, table: Table):
        self.id = id
        self.table = table
        self.items: List[tuple] = []
        self.status = OrderStatus.PLACED
    
    def add_item(self, item: MenuItem, qty: int): self.items.append((item, qty))
    
    @property
    def total(self): return sum(item.price * qty for item, qty in self.items)

class Restaurant:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tables: Dict[int, Table] = {}
            cls._instance.menu: Dict[str, MenuItem] = {}
            cls._instance.orders: Dict[str, Order] = {}
            cls._instance._order_counter = 0
        return cls._instance
    
    def add_table(self, t: Table): self.tables[t.number] = t
    def add_menu_item(self, m: MenuItem): self.menu[m.id] = m
    
    def assign_table(self, capacity: int):
        for t in self.tables.values():
            if t.status == TableStatus.AVAILABLE and t.capacity >= capacity:
                t.status = TableStatus.OCCUPIED
                return t
        return None
    
    def create_order(self, table: Table) -> Order:
        self._order_counter += 1
        order = Order(f"ORD-{self._order_counter}", table)
        self.orders[order.id] = order
        return order
    
    def complete_order(self, order_id: str):
        order = self.orders.get(order_id)
        if order:
            order.status = OrderStatus.PAID
            order.table.status = TableStatus.CLEANING
            print(f"Order {order_id} completed. Total: ${order.total:.2f}")
