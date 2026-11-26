# Code Walkthrough: Food Delivery Platform

## Entry APIs
The core entry points for interacting with the system across versions are:
- `Cart.addItem(MenuItem)` / `Cart.add_item(item)`: Add an item to a user's cart.
- `Order.transitionState(expected, next)` / `Order.transition_state(expected, next)`: Update the state of an order.
- `DriverManager.assignDriver(Restaurant)` / `DriverManager.assign_driver(restaurant)`: Dispatch an available driver for an order.
- `PricingStrategy.calculatePrice(...)` / `PricingStrategy.calculate_price(...)`: Determine dynamic pricing for an order.

## Version Delta Table

| Feature Domain       | v1-basic                        | v2-extended                     | v3-optimized                             |
| -------------------- | ------------------------------- | ------------------------------- | ---------------------------------------- |
| **Order Management** | Sequential state enum updates   | Trigger dispatch on PREPARING   | Thread-safe atomic state transitions     |
| **Driver Dispatch**  | None                            | NearestDriverStrategy (Euclidean)| Optimistic locking / Concurrency control |
| **Pricing**          | Fixed menu item totals          | Standard delivery fee           | SurgePricingStrategy based on supply     |
| **Concurrency**      | Unsafe concurrent updates       | Basic object locks              | AtomicReference / threading.Lock         |

## v1: Basic Operations
In v1, we focus on the fundamental structures. The `Cart` allows adding items from a `Menu`. When `checkout()` is called, an `Order` is generated in the `CREATED` state. The order can be manually moved through `ACCEPTED`, `PREPARING`, `OUT_FOR_DELIVERY`, and `DELIVERED`.

## v2: Driver Dispatch
v2 introduces spatial concepts. We define a `Location` class with coordinates. The `DriverManager` keeps track of active drivers. When an order reaches the `PREPARING` or `ACCEPTED` state, the `DispatchStrategy` is invoked. A `NearestDriverStrategy` calculates the Euclidean distance or uses a simple geohash distance approximation to find the closest available driver.

## v3: Optimized & Pricing
v3 adds dynamic pricing. A `PricingStrategy` interface is introduced. Implementations like `SurgePricingStrategy` take into account factors like the ratio of active orders to available drivers to calculate a multiplier. Furthermore, state transitions in `Order` are made thread-safe to handle concurrent updates from restaurants and drivers.
