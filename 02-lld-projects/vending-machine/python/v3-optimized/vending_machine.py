"""
Vending Machine System - V3 Optimized

Thread-safe VendingMachine with concurrent purchase support.
"""
from typing import List, Optional
import threading

from coin import Coin
from product import Product
from slot import Slot
from inventory import Inventory
from vending_machine_state import VendingMachineState, IdleState


class VendingMachine:
    """Thread-safe vending machine class that delegates to state objects.
    
    Thread Safety:
    The transaction lock serializes full purchase sequences
    (insert_money → select_product → dispense/cancel).  insert_money()
    acquires the lock; dispense() and cancel_transaction() release it.
    select_product() runs under the lock already held by insert_money().
    """
    
    def __init__(self, machine_id: str = "VM-001"):
        self._machine_id = machine_id
        self._current_state: VendingMachineState = IdleState()
        self._inventory = Inventory()
        self._current_balance: float = 0.0
        self._selected_slot: Optional[Slot] = None
        self._inserted_coins: List[Coin] = []
        self._transaction_lock = threading.Lock()
        self._lock_owner: Optional[int] = None
    
    # ============ Transaction Lock Helpers ============
    
    def _acquire_transaction(self) -> None:
        """Acquire the transaction lock for the current thread."""
        tid = threading.current_thread().ident
        if self._lock_owner != tid:
            self._transaction_lock.acquire()
            self._lock_owner = tid
    
    def _release_transaction(self) -> None:
        """Release the transaction lock."""
        self._lock_owner = None
        self._transaction_lock.release()
    
    # ============ Public Operations (Delegated to State) ============
    
    def insert_money(self, coin: Coin) -> None:
        """Insert a coin into the machine. Acquires transaction lock."""
        if coin is None:
            raise ValueError("Coin cannot be null")
        self._acquire_transaction()
        self._current_state.insert_money(self, coin)
    
    def select_product(self, slot_code: str) -> None:
        """Select a product by slot code. Must be called after insert_money."""
        if not slot_code:
            raise ValueError("Slot code cannot be null or empty")
        self._acquire_transaction()
        self._current_state.select_product(self, slot_code)
    
    def dispense(self) -> Optional[Product]:
        """Dispense the selected product. Releases transaction lock."""
        self._acquire_transaction()
        try:
            return self._current_state.dispense(self)
        finally:
            self._release_transaction()
    
    def cancel_transaction(self) -> List[Coin]:
        """Cancel the current transaction. Releases transaction lock."""
        self._acquire_transaction()
        try:
            return self._current_state.cancel(self)
        finally:
            self._release_transaction()
    
    # ============ State Management ============
    
    def set_state(self, state: VendingMachineState) -> None:
        """Set the current state."""
        self._current_state = state
    
    @property
    def current_state_name(self) -> str:
        """Get the name of the current state."""
        return self._current_state.get_state_name()
    
    # ============ Balance Management ============
    
    def add_to_balance(self, coin: Coin) -> None:
        """Add a coin to the current balance."""
        self._current_balance += coin.value
        self._inserted_coins.append(coin)
    
    @property
    def balance(self) -> float:
        """Get the current balance."""
        return self._current_balance
    
    def get_inserted_coins(self) -> List[Coin]:
        """Get a copy of the inserted coins."""
        return list(self._inserted_coins)
    
    def reset_transaction(self) -> None:
        """Reset the current transaction."""
        self._current_balance = 0.0
        self._selected_slot = None
        self._inserted_coins.clear()
    
    # ============ Slot Management ============
    
    def set_selected_slot(self, slot: Slot) -> None:
        """Set the selected slot."""
        self._selected_slot = slot
    
    @property
    def selected_slot(self) -> Optional[Slot]:
        """Get the selected slot."""
        return self._selected_slot
    
    # ============ Inventory Access ============
    
    @property
    def inventory(self) -> Inventory:
        """Get the inventory."""
        return self._inventory
    
    def add_slot(self, code: str, product_name: str, price: float,
                 category: Optional[str] = None, quantity: int = 0,
                 max_capacity: int = 10) -> None:
        """Add a product slot to the machine."""
        product = Product(code, product_name, price)
        slot = Slot(code, product, quantity, max_capacity)
        self._inventory.add_slot(slot)
    
    def get_available_products(self) -> List[Product]:
        """Get all available products."""
        return self._inventory.get_available_products()
    
    # ============ Admin Operations ============
    
    def restock_slot(self, slot_code: str, quantity: int) -> None:
        """Restock a slot."""
        slot = self._inventory.get_slot(slot_code)
        if slot is None:
            print(f"Slot not found: {slot_code}")
            return
        added = slot.restock(quantity)
        print(f"Added {added} items to slot {slot_code}")
    
    def add_coins_to_inventory(self, coin: Coin, count: int) -> None:
        """Add coins to the inventory."""
        self._inventory.add_coins(coin, count)
        print(f"Added {count} {coin.name} coins to inventory")
    
    # ============ Display ============
    
    def display_products(self) -> None:
        """Display available products."""
        print("\n=== Available Products ===")
        for slot in self._inventory.get_all_slots():
            status = " [OUT OF STOCK]" if slot.is_empty else ""
            print(f"{slot}{status}")
        print()
    
    def display_status(self) -> None:
        """Display machine status."""
        print("\n=== Vending Machine Status ===")
        print(f"State: {self.current_state_name}")
        print(f"Current Balance: ${self._current_balance:.2f}")
        if self._selected_slot:
            print(f"Selected: {self._selected_slot.product.name}")
        print()
        self.display_products()
        self._inventory.display_coin_stock()
