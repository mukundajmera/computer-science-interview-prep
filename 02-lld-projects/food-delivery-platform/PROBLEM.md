# Food Delivery Platform

## Problem Statement

Design and implement the core components of a Food Delivery Platform (e.g., UberEats, DoorDash, Swiggy). The system should handle the lifecycle of an order from menu browsing to delivery, while efficiently dispatching drivers and dynamically adjusting prices based on demand.

### Core Requirements

1.  **Menu Management**: Restaurants should be able to define menus with items, prices, and availability.
2.  **Cart & Checkout**: Users can add items to their cart from a specific restaurant and proceed to checkout.
3.  **Order State Machine**: Orders must transition through a strict state machine including reservation, payment, restaurant acceptance, and courier dispatch. Duplicate requests and failures must release inventory/payment/courier at most once.
4.  **Driver Dispatch**: When an order is ready (or about to be ready), the system should dispatch a driver based on nearest distance or geohash proximity. One courier with barrier-start competing orders accepts at most one active assignment.
5.  **Dynamic Pricing**: The platform should apply dynamic pricing (surge pricing) based on demand, driver availability, or time of day. Cancel/late acceptance and unavailable stock preserve exact order totals.

*Note*: Version-specific APIs and deterministic fixture inputs/expected outputs are fixed before implementation; no production/security promise is inferred.

### Expected Deliverables

-   **v1-basic**: Basic menu, cart, and simple order creation with a manual state machine.
-   **v2-extended**: Driver dispatch logic based on spatial proximity (e.g., nearest distance calculation).
-   **v3-optimized**: Dynamic pricing strategies, concurrent state machine updates, and advanced dispatching using strategies.
