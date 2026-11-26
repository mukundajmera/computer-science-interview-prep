// Restaurant Management System - V1 Basic
// Core entities: Table, MenuItem, Order, Bill

import java.util.*;
import java.time.LocalDateTime;

enum TableStatus {
    AVAILABLE, OCCUPIED, RESERVED
}

enum OrderStatus {
    PLACED, PREPARING, READY, SERVED, BILLED, COMPLETED
}

enum MenuCategory {
    APPETIZER, MAIN_COURSE, DESSERT, BEVERAGE
}

class Table {
    private final String id;
    private final int capacity;
    private TableStatus status;
    private Order currentOrder;

    public Table(String id, int capacity) {
        this.id = id;
        this.capacity = capacity;
        this.status = TableStatus.AVAILABLE;
    }

    public String getId() { return id; }
    public int getCapacity() { return capacity; }
    public TableStatus getStatus() { return status; }
    public Order getCurrentOrder() { return currentOrder; }

    public void setStatus(TableStatus status) { this.status = status; }
    public void setCurrentOrder(Order order) { this.currentOrder = order; }

    public boolean canAccommodate(int partySize) {
        return status == TableStatus.AVAILABLE && capacity >= partySize;
    }

    @Override
    public String toString() {
        return String.format("Table[%s, capacity=%d, status=%s]", id, capacity, status);
    }
}

class MenuItem {
    private final String id;
    private final String name;
    private final double price;
    private final MenuCategory category;
    private boolean available;

    public MenuItem(String id, String name, double price, MenuCategory category) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.category = category;
        this.available = true;
    }

    public String getId() { return id; }
    public String getName() { return name; }
    public double getPrice() { return price; }
    public MenuCategory getCategory() { return category; }
    public boolean isAvailable() { return available; }
    public void setAvailable(boolean available) { this.available = available; }

    @Override
    public String toString() {
        return String.format("%s - $%.2f (%s)", name, price, category);
    }
}

class OrderItem {
    private final MenuItem menuItem;
    private final int quantity;
    private final String notes;

    public OrderItem(MenuItem menuItem, int quantity, String notes) {
        this.menuItem = menuItem;
        this.quantity = quantity;
        this.notes = notes;
    }

    public MenuItem getMenuItem() { return menuItem; }
    public int getQuantity() { return quantity; }
    public String getNotes() { return notes; }

    public double getSubtotal() {
        return menuItem.getPrice() * quantity;
    }

    @Override
    public String toString() {
        return String.format("%dx %s ($%.2f)", quantity, menuItem.getName(), getSubtotal());
    }
}

class Order {
    private final String id;
    private final Table table;
    private final List<OrderItem> items;
    private OrderStatus status;
    private final LocalDateTime createdAt;

    public Order(String id, Table table) {
        this.id = id;
        this.table = table;
        this.items = new ArrayList<>();
        this.status = OrderStatus.PLACED;
        this.createdAt = LocalDateTime.now();
    }

    public String getId() { return id; }
    public Table getTable() { return table; }
    public List<OrderItem> getItems() { return new ArrayList<>(items); }
    public OrderStatus getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }

    public void addItem(OrderItem item) {
        items.add(item);
    }

    public void setStatus(OrderStatus status) {
        this.status = status;
    }

    public double getTotal() {
        return items.stream().mapToDouble(OrderItem::getSubtotal).sum();
    }

    @Override
    public String toString() {
        return String.format("Order[%s, table=%s, items=%d, total=$%.2f, status=%s]",
                id, table.getId(), items.size(), getTotal(), status);
    }
}

class Bill {
    private final String id;
    private final Order order;
    private final double subtotal;
    private final double taxRate;
    private final double tax;
    private double tip;
    private boolean paid;

    public Bill(String id, Order order, double taxRate) {
        this.id = id;
        this.order = order;
        this.subtotal = order.getTotal();
        this.taxRate = taxRate;
        this.tax = subtotal * taxRate;
        this.tip = 0;
        this.paid = false;
    }

    public String getId() { return id; }
    public Order getOrder() { return order; }
    public double getSubtotal() { return subtotal; }
    public double getTax() { return tax; }
    public double getTip() { return tip; }
    public boolean isPaid() { return paid; }

    public void setTip(double tip) { this.tip = tip; }

    public double getTotal() {
        return subtotal + tax + tip;
    }

    public void pay() {
        this.paid = true;
        order.setStatus(OrderStatus.BILLED);
    }

    @Override
    public String toString() {
        return String.format("Bill[subtotal=$%.2f, tax=$%.2f, tip=$%.2f, total=$%.2f, paid=%s]",
                subtotal, tax, tip, getTotal(), paid);
    }
}

class RestaurantService {
    private final Map<String, Table> tables;
    private final Map<String, MenuItem> menuItems;
    private final Map<String, Order> orders;
    private final Map<String, Bill> bills;
    private int orderCounter;
    private int billCounter;

    public RestaurantService() {
        this.tables = new HashMap<>();
        this.menuItems = new HashMap<>();
        this.orders = new HashMap<>();
        this.bills = new HashMap<>();
        this.orderCounter = 0;
        this.billCounter = 0;
    }

    // Table Management
    public Table addTable(String id, int capacity) {
        Table table = new Table(id, capacity);
        tables.put(id, table);
        return table;
    }

    public Table getTable(String id) {
        return tables.get(id);
    }

    public List<Table> getAvailableTables(int partySize) {
        List<Table> available = new ArrayList<>();
        for (Table table : tables.values()) {
            if (table.canAccommodate(partySize)) {
                available.add(table);
            }
        }
        return available;
    }

    public boolean seatParty(String tableId, int partySize) {
        Table table = tables.get(tableId);
        if (table != null && table.canAccommodate(partySize)) {
            table.setStatus(TableStatus.OCCUPIED);
            return true;
        }
        return false;
    }

    // Menu Management
    public MenuItem addMenuItem(String id, String name, double price, MenuCategory category) {
        MenuItem item = new MenuItem(id, name, price, category);
        menuItems.put(id, item);
        return item;
    }

    public MenuItem getMenuItem(String id) {
        return menuItems.get(id);
    }

    public List<MenuItem> getMenuByCategory(MenuCategory category) {
        List<MenuItem> items = new ArrayList<>();
        for (MenuItem item : menuItems.values()) {
            if (item.getCategory() == category && item.isAvailable()) {
                items.add(item);
            }
        }
        return items;
    }

    // Order Management
    public Order createOrder(String tableId) {
        Table table = tables.get(tableId);
        if (table == null || table.getStatus() != TableStatus.OCCUPIED) {
            return null;
        }
        String orderId = "ORD-" + (++orderCounter);
        Order order = new Order(orderId, table);
        orders.put(orderId, order);
        table.setCurrentOrder(order);
        return order;
    }

    public boolean addItemToOrder(String orderId, String menuItemId, int quantity, String notes) {
        Order order = orders.get(orderId);
        MenuItem menuItem = menuItems.get(menuItemId);
        if (order == null || menuItem == null || !menuItem.isAvailable()) {
            return false;
        }
        order.addItem(new OrderItem(menuItem, quantity, notes));
        return true;
    }

    public void updateOrderStatus(String orderId, OrderStatus status) {
        Order order = orders.get(orderId);
        if (order != null) {
            order.setStatus(status);
        }
    }

    // Billing
    public Bill generateBill(String orderId, double taxRate) {
        Order order = orders.get(orderId);
        if (order == null || order.getStatus() == OrderStatus.BILLED) {
            return null;
        }
        String billId = "BILL-" + (++billCounter);
        Bill bill = new Bill(billId, order, taxRate);
        bills.put(billId, bill);
        return bill;
    }

    public boolean payBill(String billId, double tip) {
        Bill bill = bills.get(billId);
        if (bill == null || bill.isPaid()) {
            return false;
        }
        bill.setTip(tip);
        bill.pay();
        
        // Free up the table
        Table table = bill.getOrder().getTable();
        table.setStatus(TableStatus.AVAILABLE);
        table.setCurrentOrder(null);
        bill.getOrder().setStatus(OrderStatus.COMPLETED);
        return true;
    }

    public Bill getBill(String billId) {
        return bills.get(billId);
    }
}
