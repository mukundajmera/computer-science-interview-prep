"""
Vending Machine System - V1 Basic Demo

Demonstrates the basic vending machine functionality.
"""
from coin import Coin
from vending_machine import VendingMachine


def main():
    print("===========================================")
    print("   Vending Machine System - V1 Basic Demo")
    print("===========================================\n")
    
    # Create vending machine
    machine = VendingMachine()
    
    # Setup products
    setup_products(machine)
    
    # Setup coin inventory for change
    setup_coin_inventory(machine)
    
    # Display initial status
    machine.display_status()
    
    # Demo 1: Successful purchase with change
    print("\n--- Demo 1: Purchase Chips with Change ---")
    machine.insert_money(Coin.DOLLAR)
    machine.insert_money(Coin.DOLLAR)
    machine.select_product("A1")
    machine.dispense()
    
    # Demo 2: Multiple coins, exact change
    print("\n--- Demo 2: Purchase Soda with Exact Change ---")
    machine.insert_money(Coin.DOLLAR)
    machine.insert_money(Coin.QUARTER)
    machine.insert_money(Coin.QUARTER)
    machine.select_product("B1")
    machine.dispense()
    
    # Demo 3: Cancelled transaction
    print("\n--- Demo 3: Cancelled Transaction ---")
    machine.insert_money(Coin.QUARTER)
    machine.insert_money(Coin.QUARTER)
    machine.cancel_transaction()
    
    # Demo 4: Insufficient funds
    print("\n--- Demo 4: Insufficient Funds ---")
    machine.insert_money(Coin.QUARTER)
    machine.select_product("A1")  # Chips cost $1.50, only have $0.25
    
    # Add more money
    machine.insert_money(Coin.DOLLAR)
    machine.insert_money(Coin.QUARTER)
    machine.select_product("A1")  # Now have $1.50
    machine.dispense()
    
    # Demo 5: Out of stock
    print("\n--- Demo 5: Out of Stock ---")
    machine.insert_money(Coin.DOLLAR)
    machine.insert_money(Coin.DOLLAR)
    machine.select_product("C1")  # Candy only had 0 items
    machine.cancel_transaction()
    
    # Final status
    print("\n--- Final Machine Status ---")
    machine.display_status()


def setup_products(machine: VendingMachine):
    """Setup products in the vending machine."""
    machine.add_slot("A1", "Chips", 1.50, 5, 10)
    machine.add_slot("A2", "Pretzels", 1.25, 5, 10)
    machine.add_slot("B1", "Soda", 1.50, 5, 10)
    machine.add_slot("B2", "Water", 1.00, 5, 10)
    machine.add_slot("C1", "Candy Bar", 1.75, 0, 10)  # Out of stock
    machine.add_slot("C2", "Gum", 0.75, 5, 10)


def setup_coin_inventory(machine: VendingMachine):
    """Setup coin inventory for change."""
    machine.add_coins_to_inventory(Coin.QUARTER, 20)
    machine.add_coins_to_inventory(Coin.DIME, 20)
    machine.add_coins_to_inventory(Coin.NICKEL, 20)
    machine.add_coins_to_inventory(Coin.PENNY, 20)


if __name__ == "__main__":
    main()
