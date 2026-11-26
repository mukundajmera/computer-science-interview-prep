from models import Customer, Restaurant, RestaurantOwner, Driver, MenuItem, OrderItem
from service import Order
from strategies import StandardPricingStrategy


def main():
    # 1. Setup Data
    res = Restaurant("Pizza Palace")
    cust = Customer("C1", "Alice")
    owner = RestaurantOwner("O1", "Bob", res)
    driver = Driver("D1", "Charlie")

    pizza = MenuItem("M1", "Pepperoni Pizza", 15.0)

    # 2. Create Order
    order = Order("ORD-1", cust, res, StandardPricingStrategy())
    order.add_item(OrderItem(pizza, 2))

    print(f"Total Cost: ${order.get_total():.2f}")

    # 3. Register Observers
    order.add_observer(cust)
    order.add_observer(owner)
    order.add_observer(driver)

    # 4. Simulate Flow
    print("--- Restaurant Accepts Order ---")
    order.next_state()  # PREPARING

    print("--- Food is Ready ---")
    order.next_state()  # READY_FOR_PICKUP

    print("--- Driver Accepts ---")
    if order.assign_driver(driver):
        print("Driver assigned successfully.")

    print("--- Driver Picks Up ---")
    order.next_state()  # OUT_FOR_DELIVERY

    print("--- Driver Delivers ---")
    order.next_state()  # DELIVERED


if __name__ == "__main__":
    main()
