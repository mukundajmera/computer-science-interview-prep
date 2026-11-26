# Food Delivery System (e.g., DoorDash, UberEats, Zomato)

## Problem Statement

Design a Food Delivery System that connects customers, restaurants, and delivery drivers. Customers can view restaurant menus, place orders, and track their delivery status. Restaurants can manage their menus and accept/prepare orders. Drivers can view available orders, accept them, and deliver them to customers. The system should manage order states and notify relevant parties of any changes.

## Functional Requirements

1. **User Management**:
   * Support for three types of users: Customers, Restaurant Owners, and Delivery Drivers.
2. **Restaurant & Menu Management**:
   * Restaurants can add, update, or remove menu items.
   * Customers can search for restaurants and view their menus.
3. **Order Management**:
   * Customers can add items to a cart and place an order.
   * An order transitions through various states (e.g., Placed, Accepted, Preparing, Ready for Pickup, Out for Delivery, Delivered).
   * Restaurants can accept/reject orders and update their status (e.g., Preparing -> Ready).
4. **Delivery Management**:
   * Drivers can view available nearby orders and accept them.
   * Drivers can update the delivery status (e.g., Picked up -> Delivered).
5. **Notifications**:
   * Customers and Restaurants receive notifications when the order state changes.
6. **Pricing & Payments** (Simplified):
   * Calculate total order cost including taxes and delivery fees based on different strategies.

## Non-Functional Requirements

1. **Scalability**: The system should handle a large number of concurrent users, orders, and restaurants, especially during peak hours.
2. **Reliability/Availability**: Ensure zero loss of orders and high availability for core flows.
3. **Consistency**: Order states must be consistent across all users viewing the same order.
4. **Low Latency**: Search and menu retrieval should be fast. Notifications should be delivered in near real-time.
5. **Extensibility**: The system should easily support adding new order states, pricing strategies, or notification types.

## Out of Scope (For typical LLD)
* Real-time GPS tracking implementation (assume location updates are discrete events).
* Complex payment gateway integration (assume a simplified internal payment interface).
* Recommendation systems and complex search algorithms.
