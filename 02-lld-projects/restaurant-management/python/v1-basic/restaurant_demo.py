# Restaurant Management System - V1 Basic Demo

from restaurant import (
    RestaurantService, MenuCategory, OrderStatus
)


def main():
    restaurant = RestaurantService()

    # Setup tables
    print("=== Setting up Tables ===")
    restaurant.add_table("T1", 2)
    restaurant.add_table("T2", 4)
    restaurant.add_table("T3", 6)
    restaurant.add_table("T4", 4)

    # Setup menu
    print("\n=== Setting up Menu ===")
    restaurant.add_menu_item("A1", "Spring Rolls", 8.99, MenuCategory.APPETIZER)
    restaurant.add_menu_item("A2", "Soup of the Day", 6.99, MenuCategory.APPETIZER)
    restaurant.add_menu_item("M1", "Grilled Salmon", 24.99, MenuCategory.MAIN_COURSE)
    restaurant.add_menu_item("M2", "Ribeye Steak", 32.99, MenuCategory.MAIN_COURSE)
    restaurant.add_menu_item("D1", "Chocolate Cake", 9.99, MenuCategory.DESSERT)
    restaurant.add_menu_item("B1", "Coffee", 3.99, MenuCategory.BEVERAGE)

    # Show available tables
    print("\n=== Available Tables for 4 ===")
    for table in restaurant.get_available_tables(4):
        print(table)

    # Seat a party
    print("\n=== Seating Party at T2 ===")
    restaurant.seat_party("T2", 4)
    print(f"Table T2 status: {restaurant.get_table('T2').status.value}")

    # Create order
    print("\n=== Creating Order ===")
    order = restaurant.create_order("T2")
    print(f"Created: {order}")

    # Add items
    print("\n=== Adding Items ===")
    restaurant.add_item_to_order(order.id, "A1", 2, "extra sauce")
    restaurant.add_item_to_order(order.id, "M1", 1)
    restaurant.add_item_to_order(order.id, "M2", 2, "medium rare")
    restaurant.add_item_to_order(order.id, "D1", 2)
    restaurant.add_item_to_order(order.id, "B1", 4)

    print("Order items:")
    for item in order.items:
        print(f"  {item}")
    print(f"Order total: ${order.get_total():.2f}")

    # Update order status
    print("\n=== Order Workflow ===")
    restaurant.update_order_status(order.id, OrderStatus.PREPARING)
    print(f"Status: {order.status.value}")
    
    restaurant.update_order_status(order.id, OrderStatus.READY)
    print(f"Status: {order.status.value}")
    
    restaurant.update_order_status(order.id, OrderStatus.SERVED)
    print(f"Status: {order.status.value}")

    # Generate bill
    print("\n=== Generating Bill ===")
    bill = restaurant.generate_bill(order.id, 0.08)
    print(bill)

    # Pay bill
    print("\n=== Paying Bill ===")
    tip_amount = bill.subtotal * 0.20
    restaurant.pay_bill(bill.id, tip_amount)
    print(f"Final bill: {bill}")
    print(f"Table T2 status: {restaurant.get_table('T2').status.value}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
