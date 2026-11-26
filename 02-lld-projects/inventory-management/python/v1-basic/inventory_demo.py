"""Inventory Management demo - v1 basic."""

from inventory import InventoryManager


class PrintAlertListener:
    def on_low_stock(self, warehouse_id: str, product_id: str, current_qty: int) -> None:
        print(f"LOW STOCK: warehouse={warehouse_id} product={product_id} qty={current_qty}")


if __name__ == "__main__":
    manager = InventoryManager()
    manager.add_warehouse("W1")
    manager.add_warehouse("W2")
    manager.register_low_stock_alert("W1", "SKU-1", 3, PrintAlertListener())

    manager.add_stock("W1", "SKU-1", 5)
    manager.remove_stock("W1", "SKU-1", 2)
    manager.transfer_stock("W1", "W2", "SKU-1", 1)
    print(manager.check_availability("SKU-1", 1))
