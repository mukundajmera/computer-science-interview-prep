"""
State Pattern - V1 Basic: Vending Machine
"""
from abc import ABC, abstractmethod

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')



# State Interface
class State(ABC):
    @abstractmethod
    def insert_money(self, vm: "VendingMachine") -> None:
        pass
    
    @abstractmethod
    def select_product(self, vm: "VendingMachine") -> None:
        pass
    
    @abstractmethod
    def dispense(self, vm: "VendingMachine") -> None:
        pass


# Concrete States
class IdleState(State):
    def insert_money(self, vm: "VendingMachine") -> None:
        print(f"Money inserted: ${vm.balance:.2f}")
        vm.set_state(vm.has_money_state)
    
    def select_product(self, vm: "VendingMachine") -> None:
        print("Please insert money first")
    
    def dispense(self, vm: "VendingMachine") -> None:
        print("Please insert money and select product")


class HasMoneyState(State):
    def insert_money(self, vm: "VendingMachine") -> None:
        print(f"Total balance: ${vm.balance:.2f}")
    
    def select_product(self, vm: "VendingMachine") -> None:
        if vm.balance >= 1.50:
            print("Product selected")
            vm.set_state(vm.dispensing_state)
            vm.dispense()
        else:
            print(f"Insufficient balance. Need $1.50, have ${vm.balance:.2f}")
    
    def dispense(self, vm: "VendingMachine") -> None:
        print("Please select a product first")


class DispensingState(State):
    def insert_money(self, vm: "VendingMachine") -> None:
        print("Please wait, dispensing...")
    
    def select_product(self, vm: "VendingMachine") -> None:
        print("Please wait, dispensing...")
    
    def dispense(self, vm: "VendingMachine") -> None:
        print("Product dispensed!")
        vm.balance = 0
        vm.set_state(vm.idle_state)


# Context
class VendingMachine:
    def __init__(self):
        self.idle_state = IdleState()
        self.has_money_state = HasMoneyState()
        self.dispensing_state = DispensingState()
        self._state = self.idle_state
        self.balance = 0.0
    
    def set_state(self, state: State) -> None:
        print(f"State: {state.__class__.__name__}")
        self._state = state
    
    def insert_money(self, amount: float) -> None:
        self.balance += amount
        self._state.insert_money(self)
    
    def select_product(self) -> None:
        self._state.select_product(self)
    
    def dispense(self) -> None:
        self._state.dispense(self)


if __name__ == "__main__":
    vm = VendingMachine()
    
    print("=== Vending Machine ===\n")
    
    # Try without money
    vm.select_product()
    
    # Insert money
    print()
    vm.insert_money(1.00)
    vm.select_product()  # Not enough
    
    # Add more money
    print()
    vm.insert_money(0.50)
    vm.select_product()  # Now enough - dispenses
    
    # Back to idle
    print()
    vm.select_product()  # Need money again
