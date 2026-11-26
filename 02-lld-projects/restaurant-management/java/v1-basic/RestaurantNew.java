import enums.*;
import models.*;
import java.util.*;

/**
 * RestaurantNew.java - Singleton restaurant system.
 */
public class RestaurantNew {
    private static RestaurantNew instance;
    private final Map<Integer, Table> tables;
    private final Map<String, MenuItem> menu;
    private final Map<String, Order> orders;
    private int orderCounter;

    private RestaurantNew() {
        tables = new HashMap<>();
        menu = new HashMap<>();
        orders = new HashMap<>();
        orderCounter = 0;
    }

    public static synchronized RestaurantNew getInstance() {
        if (instance == null)
            instance = new RestaurantNew();
        return instance;
    }

    public void addTable(Table t) {
        tables.put(t.getTableNumber(), t);
    }

    public void addMenuItem(MenuItem m) {
        menu.put(m.getId(), m);
    }

    public Table assignTable(int capacity) {
        for (Table t : tables.values()) {
            if (t.getStatus() == TableStatus.AVAILABLE && t.getCapacity() >= capacity) {
                t.setStatus(TableStatus.OCCUPIED);
                return t;
            }
        }
        return null;
    }

    public Order createOrder(Table table) {
        String id = "ORD-" + (++orderCounter);
        Order order = new Order(id, table);
        orders.put(id, order);
        return order;
    }

    public void addToOrder(String orderId, String menuItemId, int qty) {
        Order order = orders.get(orderId);
        MenuItem item = menu.get(menuItemId);
        if (order != null && item != null)
            order.addItem(item, qty);
    }

    public void completeOrder(String orderId) {
        Order order = orders.get(orderId);
        if (order != null) {
            order.setStatus(OrderStatus.PAID);
            order.getTable().setStatus(TableStatus.CLEANING);
            System.out.printf("Order %s completed. Total: $%.2f%n", orderId, order.getTotal());
        }
    }
}
