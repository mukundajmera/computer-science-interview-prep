"""
Vending Machine System - V3 Optimized

State pattern interfaces and implementations for vending machine states.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

from coin import Coin
from product import Product

if TYPE_CHECKING:
    from vending_machine import VendingMachine


class VendingMachineState(ABC):
    """Abstract base class for vending machine states."""
    
    @abstractmethod
    def insert_money(self, machine: 'VendingMachine', coin: Coin) -> None:
        pass
    
    @abstractmethod
    def select_product(self, machine: 'VendingMachine', slot_code: str) -> None:
        pass
    
    @abstractmethod
    def dispense(self, machine: 'VendingMachine') -> Optional[Product]:
        pass
    
    @abstractmethod
    def cancel(self, machine: 'VendingMachine') -> List[Coin]:
        pass
    
    @abstractmethod
    def get_state_name(self) -> str:
        pass


class IdleState(VendingMachineState):
    """Idle state - machine is waiting for customer interaction."""
    
    def insert_money(self, machine: 'VendingMachine', coin: Coin) -> None:
        machine.add_to_balance(coin)
        print(f"Inserted: {coin}. Balance: ${machine.balance:.2f}")
        machine.set_state(HasMoneyState())
    
    def select_product(self, machine: 'VendingMachine', slot_code: str) -> None:
        print("Please insert money first.")
    
    def dispense(self, machine: 'VendingMachine') -> Optional[Product]:
        print("Please insert money and select a product first.")
        return None
    
    def cancel(self, machine: 'VendingMachine') -> List[Coin]:
        print("No transaction to cancel.")
        return []
    
    def get_state_name(self) -> str:
        return "IDLE"


class HasMoneyState(VendingMachineState):
    """Has money state - customer has inserted money but not selected product."""
    
    def insert_money(self, machine: 'VendingMachine', coin: Coin) -> None:
        machine.add_to_balance(coin)
        print(f"Inserted: {coin}. Balance: ${machine.balance:.2f}")
    
    def select_product(self, machine: 'VendingMachine', slot_code: str) -> None:
        slot = machine.inventory.get_slot(slot_code)
        
        if slot is None:
            print(f"Invalid slot code: {slot_code}")
            return
        
        if slot.is_empty:
            print(f"Sorry, {slot.product.name} is out of stock.")
            return
        
        if machine.balance < slot.product.price:
            print(f"Insufficient balance. {slot.product.name} costs ${slot.product.price:.2f}. "
                  f"Your balance: ${machine.balance:.2f}")
            return
        
        # Check if we can make change
        change_needed = machine.balance - slot.product.price
        if change_needed > 0 and not machine.inventory.can_make_change(change_needed):
            print("Sorry, cannot provide exact change. Please use exact amount or cancel.")
            return
        
        machine.set_selected_slot(slot)
        print(f"Selected: {slot.product.name}. Press dispense to complete purchase.")
        machine.set_state(ProductSelectedState())
    
    def dispense(self, machine: 'VendingMachine') -> Optional[Product]:
        print("Please select a product first.")
        return None
    
    def cancel(self, machine: 'VendingMachine') -> List[Coin]:
        refund = machine.get_inserted_coins()
        print(f"Transaction cancelled. Returning: {len(refund)} coin(s)")
        machine.reset_transaction()
        machine.set_state(IdleState())
        return refund
    
    def get_state_name(self) -> str:
        return "HAS_MONEY"


class ProductSelectedState(VendingMachineState):
    """Product selected state - customer has selected a product."""
    
    def insert_money(self, machine: 'VendingMachine', coin: Coin) -> None:
        machine.add_to_balance(coin)
        print(f"Inserted: {coin}. Balance: ${machine.balance:.2f}")
    
    def select_product(self, machine: 'VendingMachine', slot_code: str) -> None:
        # Allow changing selection
        slot = machine.inventory.get_slot(slot_code)
        
        if slot is None:
            print(f"Invalid slot code: {slot_code}")
            return
        
        if slot.is_empty:
            print(f"Sorry, {slot.product.name} is out of stock.")
            return
        
        if machine.balance < slot.product.price:
            print(f"Insufficient balance for {slot.product.name}")
            return
        
        machine.set_selected_slot(slot)
        print(f"Changed selection to: {slot.product.name}")
    
    def dispense(self, machine: 'VendingMachine') -> Optional[Product]:
        slot = machine.selected_slot
        product = slot.product
        
        # Dispense product
        dispensed = slot.dispense_one()
        if dispensed is None:
            print("Error: Product out of stock.")
            machine.set_state(HasMoneyState())
            return None
        
        # Add inserted coins to inventory
        machine.inventory.add_coins_list(machine.get_inserted_coins())
        
        # Calculate and return change
        change_amount = machine.balance - product.price
        if change_amount > 0:
            change = machine.inventory.get_change(change_amount)
            print(f"Dispensing: {product.name}")
            print(f"Returning change: ${change_amount:.2f} ({len(change)} coin(s))")
        else:
            print(f"Dispensing: {product.name}")
            print("No change required.")
        
        machine.reset_transaction()
        machine.set_state(IdleState())
        
        return dispensed
    
    def cancel(self, machine: 'VendingMachine') -> List[Coin]:
        refund = machine.get_inserted_coins()
        print(f"Transaction cancelled. Returning: {len(refund)} coin(s)")
        machine.reset_transaction()
        machine.set_state(IdleState())
        return refund
    
    def get_state_name(self) -> str:
        return "PRODUCT_SELECTED"
