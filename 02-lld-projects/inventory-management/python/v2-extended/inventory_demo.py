"""Inventory Management demo - v2 extended."""

from inventory import InventoryManager


if __name__ == "__main__":
    manager = InventoryManager()
    manager.add_warehouse("W1")
    manager.add_stock("W1", "SKU-1", 10)

    reservation = manager.reserve_stock("W1", "SKU-1", 4)
    print(f"reservation={reservation}")
    print(manager.availability_snapshot("SKU-1"))

    if reservation:
        manager.commit_reservation(reservation.reservation_id)
    print(manager.availability_snapshot("SKU-1"))
