# Restaurant Management System - V1 Basic
# Core entities: Table, MenuItem, Order, Bill

from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional


class TableStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"


class OrderStatus(Enum):
    PLACED = "placed"
    PREPARING = "preparing"
    READY = "ready"
    SERVED = "served"
    BILLED = "billed"
    COMPLETED = "completed"


class MenuCategory(Enum):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"


class Table:
    def __init__(self, table_id: str, capacity: int):
        self.id = table_id
        self.capacity = capacity
        self.status = TableStatus.AVAILABLE
        self.current_order: Optional['Order'] = None

    def can_accommodate(self, party_size: int) -> bool:
        return self.status == TableStatus.AVAILABLE and self.capacity >= party_size

    def __str__(self):
        return f"Table[{self.id}, capacity={self.capacity}, status={self.status.value}]"


class MenuItem:
    def __init__(self, item_id: str, name: str, price: float, category: MenuCategory):
        self.id = item_id
        self.name = name
        self.price = price
        self.category = category
        self.available = True

    def __str__(self):
        return f"{self.name} - ${self.price:.2f} ({self.category.value})"


class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int, notes: Optional[str] = None):
        self.menu_item = menu_item
        self.quantity = quantity
        self.notes = notes

    def get_subtotal(self) -> float:
        return self.menu_item.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} (${self.get_subtotal():.2f})"


class Order:
    def __init__(self, order_id: str, table: Table):
        self.id = order_id
        self.table = table
        self.items: List[OrderItem] = []
        self.status = OrderStatus.PLACED
        self.created_at = datetime.now()

    def add_item(self, item: OrderItem):
        self.items.append(item)

    def get_total(self) -> float:
        return sum(item.get_subtotal() for item in self.items)

    def __str__(self):
        return f"Order[{self.id}, table={self.table.id}, items={len(self.items)}, total=${self.get_total():.2f}, status={self.status.value}]"


class Bill:
    def __init__(self, bill_id: str, order: Order, tax_rate: float):
        self.id = bill_id
        self.order = order
        self.subtotal = order.get_total()
        self.tax_rate = tax_rate
        self.tax = self.subtotal * tax_rate
        self.tip = 0.0
        self.paid = False

    def get_total(self) -> float:
        return self.subtotal + self.tax + self.tip

    def pay(self):
        self.paid = True
        self.order.status = OrderStatus.BILLED

    def __str__(self):
        return f"Bill[subtotal=${self.subtotal:.2f}, tax=${self.tax:.2f}, tip=${self.tip:.2f}, total=${self.get_total():.2f}, paid={self.paid}]"


class RestaurantService:
    def __init__(self):
        self.tables: Dict[str, Table] = {}
        self.menu_items: Dict[str, MenuItem] = {}
        self.orders: Dict[str, Order] = {}
        self.bills: Dict[str, Bill] = {}
        self._order_counter = 0
        self._bill_counter = 0

    # Table Management
    def add_table(self, table_id: str, capacity: int) -> Table:
        table = Table(table_id, capacity)
        self.tables[table_id] = table
        return table

    def get_table(self, table_id: str) -> Optional[Table]:
        return self.tables.get(table_id)

    def get_available_tables(self, party_size: int) -> List[Table]:
        return [t for t in self.tables.values() if t.can_accommodate(party_size)]

    def seat_party(self, table_id: str, party_size: int) -> bool:
        table = self.tables.get(table_id)
        if table and table.can_accommodate(party_size):
            table.status = TableStatus.OCCUPIED
            return True
        return False

    # Menu Management
    def add_menu_item(self, item_id: str, name: str, price: float, category: MenuCategory) -> MenuItem:
        item = MenuItem(item_id, name, price, category)
        self.menu_items[item_id] = item
        return item

    def get_menu_item(self, item_id: str) -> Optional[MenuItem]:
        return self.menu_items.get(item_id)

    def get_menu_by_category(self, category: MenuCategory) -> List[MenuItem]:
        return [i for i in self.menu_items.values() if i.category == category and i.available]

    # Order Management
    def create_order(self, table_id: str) -> Optional[Order]:
        table = self.tables.get(table_id)
        if not table or table.status != TableStatus.OCCUPIED:
            return None
        self._order_counter += 1
        order_id = f"ORD-{self._order_counter}"
        order = Order(order_id, table)
        self.orders[order_id] = order
        table.current_order = order
        return order

    def add_item_to_order(self, order_id: str, menu_item_id: str, quantity: int, notes: Optional[str] = None) -> bool:
        order = self.orders.get(order_id)
        menu_item = self.menu_items.get(menu_item_id)
        if not order or not menu_item or not menu_item.available:
            return False
        order.add_item(OrderItem(menu_item, quantity, notes))
        return True

    def update_order_status(self, order_id: str, status: OrderStatus):
        order = self.orders.get(order_id)
        if order:
            order.status = status

    # Billing
    def generate_bill(self, order_id: str, tax_rate: float) -> Optional[Bill]:
        order = self.orders.get(order_id)
        if not order or order.status == OrderStatus.BILLED:
            return None
        self._bill_counter += 1
        bill_id = f"BILL-{self._bill_counter}"
        bill = Bill(bill_id, order, tax_rate)
        self.bills[bill_id] = bill
        return bill

    def pay_bill(self, bill_id: str, tip: float) -> bool:
        bill = self.bills.get(bill_id)
        if not bill or bill.paid:
            return False
        bill.tip = tip
        bill.pay()
        
        # Free table
        table = bill.order.table
        table.status = TableStatus.AVAILABLE
        table.current_order = None
        bill.order.status = OrderStatus.COMPLETED
        return True

    def get_bill(self, bill_id: str) -> Optional[Bill]:
        return self.bills.get(bill_id)
