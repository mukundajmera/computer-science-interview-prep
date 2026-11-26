"""
Vending Machine System - V1 Basic

Main VendingMachine class implementing State pattern.
"""
from typing import List, Optional

from coin import Coin
from product import Product
from slot import Slot
from inventory import Inventory
from vending_machine_state import VendingMachineState, IdleState


class VendingMachine:
    """Main vending machine class that delegates to state objects."""
    
    def __init__(self):
        self._current_state: VendingMachineState = IdleState()
        self._inventory = Inventory()
        self._current_balance: float = 0.0
        self._selected_slot: Optional[Slot] = None
        self._inserted_coins: List[Coin] = []
    
    # ============ Public Operations (Delegated to State) ============
    
    def insert_money(self, coin: Coin) -> None:
        """Insert a coin into the machine."""
        if coin is None:
            raise ValueError("Coin cannot be null")
        self._current_state.insert_money(self, coin)
    
    def select_product(self, slot_code: str) -> None:
        """Select a product by slot code."""
        if not slot_code:
            raise ValueError("Slot code cannot be null or empty")
        self._current_state.select_product(self, slot_code)
    
    def dispense(self) -> Optional[Product]:
        """Dispense the selected product."""
        return self._current_state.dispense(self)
    
    def cancel_transaction(self) -> List[Coin]:
        """Cancel the current transaction."""
        return self._current_state.cancel(self)
    
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
                 quantity: int, max_capacity: int) -> None:
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
