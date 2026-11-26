// Restaurant Management System - V1 Basic Demo

public class RestaurantDemo {
    public static void main(String[] args) {
        RestaurantService restaurant = new RestaurantService();

        // Setup tables
        System.out.println("=== Setting up Tables ===");
        restaurant.addTable("T1", 2);
        restaurant.addTable("T2", 4);
        restaurant.addTable("T3", 6);
        restaurant.addTable("T4", 4);

        // Setup menu
        System.out.println("\n=== Setting up Menu ===");
        restaurant.addMenuItem("A1", "Spring Rolls", 8.99, MenuCategory.APPETIZER);
        restaurant.addMenuItem("A2", "Soup of the Day", 6.99, MenuCategory.APPETIZER);
        restaurant.addMenuItem("M1", "Grilled Salmon", 24.99, MenuCategory.MAIN_COURSE);
        restaurant.addMenuItem("M2", "Ribeye Steak", 32.99, MenuCategory.MAIN_COURSE);
        restaurant.addMenuItem("M3", "Pasta Primavera", 18.99, MenuCategory.MAIN_COURSE);
        restaurant.addMenuItem("D1", "Chocolate Cake", 9.99, MenuCategory.DESSERT);
        restaurant.addMenuItem("B1", "Coffee", 3.99, MenuCategory.BEVERAGE);

        // Show available tables for party of 4
        System.out.println("\n=== Available Tables for 4 ===");
        for (Table table : restaurant.getAvailableTables(4)) {
            System.out.println(table);
        }

        // Seat a party
        System.out.println("\n=== Seating Party at T2 ===");
        restaurant.seatParty("T2", 4);
        System.out.println("Table T2 status: " + restaurant.getTable("T2").getStatus());

        // Create order
        System.out.println("\n=== Creating Order ===");
        Order order = restaurant.createOrder("T2");
        System.out.println("Created: " + order);

        // Add items to order
        System.out.println("\n=== Adding Items ===");
        restaurant.addItemToOrder(order.getId(), "A1", 2, "extra sauce");
        restaurant.addItemToOrder(order.getId(), "M1", 1, null);
        restaurant.addItemToOrder(order.getId(), "M2", 2, "medium rare");
        restaurant.addItemToOrder(order.getId(), "D1", 2, null);
        restaurant.addItemToOrder(order.getId(), "B1", 4, null);

        System.out.println("Order items:");
        for (OrderItem item : order.getItems()) {
            System.out.println("  " + item);
        }
        System.out.println("Order total: $" + String.format("%.2f", order.getTotal()));

        // Update order status through workflow
        System.out.println("\n=== Order Workflow ===");
        restaurant.updateOrderStatus(order.getId(), OrderStatus.PREPARING);
        System.out.println("Status: " + order.getStatus());
        
        restaurant.updateOrderStatus(order.getId(), OrderStatus.READY);
        System.out.println("Status: " + order.getStatus());
        
        restaurant.updateOrderStatus(order.getId(), OrderStatus.SERVED);
        System.out.println("Status: " + order.getStatus());

        // Generate bill
        System.out.println("\n=== Generating Bill ===");
        Bill bill = restaurant.generateBill(order.getId(), 0.08); // 8% tax
        System.out.println(bill);

        // Pay bill with tip
        System.out.println("\n=== Paying Bill ===");
        double tipAmount = bill.getSubtotal() * 0.20; // 20% tip
        restaurant.payBill(bill.getId(), tipAmount);
        System.out.println("Final bill: " + bill);
        System.out.println("Table T2 status: " + restaurant.getTable("T2").getStatus());

        System.out.println("\n=== Demo Complete ===");
    }
}
