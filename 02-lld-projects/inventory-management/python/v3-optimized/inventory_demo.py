"""Inventory Management demo - v3 optimized."""

from inventory import InventoryManager


if __name__ == "__main__":
    manager = InventoryManager()
    manager.add_warehouse("W1")
    manager.add_warehouse("W2")
    manager.add_stock("W1", "SKU-42", 20)

    print("transfer:", manager.transfer_stock("W1", "W2", "SKU-42", 6))
    print("availability >= 10:", manager.check_availability("SKU-42", 10))
