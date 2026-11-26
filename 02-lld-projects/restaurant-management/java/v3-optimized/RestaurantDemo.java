// Restaurant Management System - V2 Extended Demo

import java.time.*;

public class RestaurantDemo {
    public static void main(String[] args) {
        RestaurantService restaurant = new RestaurantService();

        // Setup
        setupTables(restaurant);
        setupMenu(restaurant);

        // Make a reservation
        System.out.println("=== Reservation Flow ===");
        LocalDateTime reservationTime = LocalDateTime.now().plusHours(2);
        Reservation reservation = restaurant.makeReservation("John Smith", "555-1234", 4, reservationTime);
        System.out.println("Created: " + reservation);

        // Seat the party (from reservation)
        System.out.println("\n=== Seating Reservation ===");
        String tableId = reservation.getAssignedTable().getId();
        restaurant.seatParty(tableId, 4);
        System.out.println("Seated at table: " + tableId);

        // Create and manage order
        System.out.println("\n=== Order with Modifications ===");
        Order order = restaurant.createOrder(tableId);
        
        // Add items
        OrderItem item1 = restaurant.addItemToOrder(order.getId(), "A1", 2, null);
        OrderItem item2 = restaurant.addItemToOrder(order.getId(), "M2", 3, "medium");
        OrderItem item3 = restaurant.addItemToOrder(order.getId(), "D1", 2, null);
        
        System.out.println("Initial order:");
        for (OrderItem item : order.getItems()) {
            System.out.println("  " + item);
        }
        System.out.println("Total: $" + String.format("%.2f", order.getTotal()));

        // Modify order - reduce quantity
        System.out.println("\n=== Modifying Order ===");
        restaurant.modifyOrderItem(order.getId(), item2.getId(), 2, "medium-rare");
        
        // Cancel an item
        restaurant.cancelOrderItem(order.getId(), item3.getId());
        
        System.out.println("After modifications:");
        for (OrderItem item : order.getItems()) {
            System.out.println("  " + item);
        }
        System.out.println("New total: $" + String.format("%.2f", order.getTotal()));

        // Process order
        restaurant.updateOrderStatus(order.getId(), OrderStatus.PREPARING);
        restaurant.updateOrderStatus(order.getId(), OrderStatus.READY);
        restaurant.updateOrderStatus(order.getId(), OrderStatus.SERVED);

        // Split bill
        System.out.println("\n=== Split Bill ===");
        Bill bill = restaurant.generateBill(order.getId(), 0.08);
        bill.setTip(bill.getSubtotal() * 0.20);
        bill.splitEvenly(4);
        
        System.out.println(bill);
        System.out.println("Split 4 ways:");
        for (var entry : bill.getSplits().entrySet()) {
            System.out.println("  " + entry.getKey() + ": $" + String.format("%.2f", entry.getValue()));
        }

        restaurant.payBill(bill.getId(), bill.getTip());
        System.out.println("\nBill paid. Table " + tableId + " status: " + restaurant.getTable(tableId).getStatus());

        System.out.println("\n=== Demo Complete ===");
    }

    private static void setupTables(RestaurantService restaurant) {
        restaurant.addTable("T1", 2);
        restaurant.addTable("T2", 4);
        restaurant.addTable("T3", 6);
        restaurant.addTable("T4", 4);
    }

    private static void setupMenu(RestaurantService restaurant) {
        restaurant.addMenuItem("A1", "Spring Rolls", 8.99, MenuCategory.APPETIZER);
        restaurant.addMenuItem("A2", "Soup", 6.99, MenuCategory.APPETIZER);
        restaurant.addMenuItem("M1", "Salmon", 24.99, MenuCategory.MAIN_COURSE);
        restaurant.addMenuItem("M2", "Steak", 32.99, MenuCategory.MAIN_COURSE);
        restaurant.addMenuItem("D1", "Cake", 9.99, MenuCategory.DESSERT);
        restaurant.addMenuItem("B1", "Coffee", 3.99, MenuCategory.BEVERAGE);
    }
}
