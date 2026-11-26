# Restaurant Management System - V3 Optimized
# Full-featured: Tables, Menu, Orders, Billing, Reservations, Waitlist, Kitchen Display

from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
from dataclasses import dataclass, field
import queue
import threading


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
    """Restaurant table with reservation and seating support."""

    def __init__(self, table_id: str, capacity: int):
        self.id = table_id
        self.capacity = capacity
        self.status = TableStatus.AVAILABLE
        self.current_order: Optional['Order'] = None

    def can_accommodate(self, party_size: int) -> bool:
        return self.status == TableStatus.AVAILABLE and self.capacity >= party_size

    def try_reserve(self, party_size: int) -> bool:
        """Attempt to reserve this table. Returns True on success."""
        if self.can_accommodate(party_size):
            self.status = TableStatus.RESERVED
            return True
        return False

    def try_seat(self, party_size: int) -> bool:
        """Attempt to seat a party. Works for available or reserved tables."""
        if self.status in (TableStatus.AVAILABLE, TableStatus.RESERVED) and self.capacity >= party_size:
            self.status = TableStatus.OCCUPIED
            return True
        return False

    def release(self) -> None:
        """Release the table back to available status."""
        self.status = TableStatus.AVAILABLE
        self.current_order = None

    def __str__(self) -> str:
        return f"Table[{self.id}, capacity={self.capacity}, status={self.status.value}]"


class MenuItem:
    def __init__(self, item_id: str, name: str, price: float, category: MenuCategory):
        self.id = item_id
        self.name = name
        self.price = price
        self.category = category
        self.available = True

    def __str__(self) -> str:
        return f"{self.name} - ${self.price:.2f} ({self.category.value})"


class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int, notes: Optional[str] = None):
        self.menu_item = menu_item
        self.quantity = quantity
        self.notes = notes

    def get_subtotal(self) -> float:
        return self.menu_item.price * self.quantity

    def __str__(self) -> str:
        return f"{self.quantity}x {self.menu_item.name} (${self.get_subtotal():.2f})"


class Order:
    def __init__(self, order_id: str, table: Table):
        self.id = order_id
        self.table = table
        self.items: List[OrderItem] = []
        self.status = OrderStatus.PLACED
        self.created_at = datetime.now()

    def add_item(self, item: OrderItem) -> None:
        self.items.append(item)

    def get_total(self) -> float:
        return sum(item.get_subtotal() for item in self.items)

    def __str__(self) -> str:
        return (f"Order[{self.id}, table={self.table.id}, items={len(self.items)}, "
                f"total=${self.get_total():.2f}, status={self.status.value}]")


class Bill:
    """Bill with support for tips and even splitting."""

    def __init__(self, bill_id: str, order: Order, tax_rate: float):
        self.id = bill_id
        self.order = order
        self.subtotal = order.get_total()
        self.tax_rate = tax_rate
        self.tax = self.subtotal * tax_rate
        self.tip = 0.0
        self.paid = False
        self.splits: Dict[int, float] = {}

    def get_total(self) -> float:
        return self.subtotal + self.tax + self.tip

    def split_evenly(self, num_people: int) -> None:
        """Split the total bill evenly among num_people."""
        if num_people <= 0:
            raise ValueError("Number of people must be positive")
        per_person = round(self.get_total() / num_people, 2)
        self.splits = {i: per_person for i in range(num_people)}

    def pay(self) -> None:
        self.paid = True
        self.order.status = OrderStatus.BILLED

    def __str__(self) -> str:
        return (f"Bill[subtotal=${self.subtotal:.2f}, tax=${self.tax:.2f}, "
                f"tip=${self.tip:.2f}, total=${self.get_total():.2f}, paid={self.paid}]")


@dataclass
class WaitlistEntry:
    """An entry on the restaurant waitlist."""
    customer_name: str
    phone: str
    party_size: int
    added_at: datetime = field(default_factory=datetime.now)
    seated: bool = False


@dataclass
class Reservation:
    """A table reservation."""
    customer_name: str
    phone: str
    party_size: int
    reservation_time: datetime
    assigned_table: Optional[Table] = None
    confirmed: bool = False


class KitchenDisplay:
    """Thread-safe kitchen order queue for preparing and tracking orders."""

    def __init__(self) -> None:
        self._pending_queue: queue.Queue[Order] = queue.Queue()
        self._pending_list: List[Order] = []
        self._in_progress: Dict[str, Order] = {}
        self._ready: Dict[str, Order] = {}
        self._lock = threading.Lock()

    def submit(self, order: Order) -> None:
        with self._lock:
            self._pending_list.append(order)
        self._pending_queue.put(order)

    def take_next_order(self, timeout: float = 5.0) -> Optional[Order]:
        """Take the next pending order and mark it as in-progress."""
        try:
            order = self._pending_queue.get(timeout=timeout)
            order.status = OrderStatus.PREPARING
            with self._lock:
                self._pending_list.remove(order)
                self._in_progress[order.id] = order
            return order
        except queue.Empty:
            return None

    def mark_ready(self, order_id: str) -> None:
        """Move an in-progress order to the ready queue."""
        with self._lock:
            order = self._in_progress.pop(order_id, None)
            if order:
                order.status = OrderStatus.READY
                self._ready[order.id] = order

    def get_pending_orders(self) -> List[Order]:
        with self._lock:
            return list(self._pending_list)

    def get_in_progress_orders(self) -> List[Order]:
        with self._lock:
            return list(self._in_progress.values())

    def get_ready_orders(self) -> List[Order]:
        with self._lock:
            return list(self._ready.values())


class RestaurantService:
    """Full-featured restaurant management service."""

    def __init__(self) -> None:
        self.tables: Dict[str, Table] = {}
        self.menu_items: Dict[str, MenuItem] = {}
        self.orders: Dict[str, Order] = {}
        self.bills: Dict[str, Bill] = {}
        self._order_counter = 0
        self._bill_counter = 0
        self._waitlist: deque[WaitlistEntry] = deque()
        self._reservations: List[Reservation] = []
        self._kitchen: KitchenDisplay = KitchenDisplay()

    # --- Table Management ---

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
        if table:
            return table.try_seat(party_size)
        return False

    # --- Reservation & Waitlist ---

    def make_reservation(self, customer_name: str, phone: str,
                         party_size: int, reservation_time: datetime) -> Optional[Reservation]:
        """Reserve the first available table that fits the party."""
        reservation = Reservation(customer_name, phone, party_size, reservation_time)
        for table in self.tables.values():
            if table.can_accommodate(party_size):
                table.try_reserve(party_size)
                reservation.assigned_table = table
                reservation.confirmed = True
                self._reservations.append(reservation)
                return reservation
        return None

    def add_to_waitlist(self, customer_name: str, phone: str, party_size: int) -> WaitlistEntry:
        entry = WaitlistEntry(customer_name, phone, party_size)
        self._waitlist.append(entry)
        return entry

    def get_waitlist(self) -> List[WaitlistEntry]:
        return [e for e in self._waitlist if not e.seated]

    def get_next_from_waitlist(self, available_capacity: int) -> Optional[WaitlistEntry]:
        """Seat the next waitlist entry that fits the given capacity."""
        for entry in self._waitlist:
            if not entry.seated and entry.party_size <= available_capacity:
                entry.seated = True
                return entry
        return None

    # --- Menu Management ---

    def add_menu_item(self, item_id: str, name: str, price: float,
                      category: MenuCategory) -> MenuItem:
        item = MenuItem(item_id, name, price, category)
        self.menu_items[item_id] = item
        return item

    def get_menu_item(self, item_id: str) -> Optional[MenuItem]:
        return self.menu_items.get(item_id)

    def get_menu_by_category(self, category: MenuCategory) -> List[MenuItem]:
        return [i for i in self.menu_items.values()
                if i.category == category and i.available]

    # --- Order Management ---

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

    def add_item_to_order(self, order_id: str, menu_item_id: str,
                          quantity: int, notes: Optional[str] = None) -> bool:
        order = self.orders.get(order_id)
        menu_item = self.menu_items.get(menu_item_id)
        if not order or not menu_item or not menu_item.available:
            return False
        order.add_item(OrderItem(menu_item, quantity, notes))
        return True

    def update_order_status(self, order_id: str, status: OrderStatus) -> None:
        order = self.orders.get(order_id)
        if order:
            order.status = status

    def submit_order_to_kitchen(self, order_id: str) -> None:
        """Submit a placed order to the kitchen display."""
        order = self.orders.get(order_id)
        if order:
            self._kitchen.submit(order)

    def get_kitchen_display(self) -> KitchenDisplay:
        return self._kitchen

    # --- Billing ---

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
        table.release()
        bill.order.status = OrderStatus.COMPLETED
        return True

    def get_bill(self, bill_id: str) -> Optional[Bill]:
        return self.bills.get(bill_id)
