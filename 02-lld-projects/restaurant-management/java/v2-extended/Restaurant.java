// Restaurant Management System - V2 Extended
// Adds: Reservations, order modifications, split bills

import java.util.*;
import java.time.*;

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

    public boolean isAvailableAt(LocalDateTime time) {
        return status != TableStatus.OCCUPIED;
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
    private final String id;
    private final MenuItem menuItem;
    private int quantity;
    private String notes;
    private boolean cancelled;

    public OrderItem(String id, MenuItem menuItem, int quantity, String notes) {
        this.id = id;
        this.menuItem = menuItem;
        this.quantity = quantity;
        this.notes = notes;
        this.cancelled = false;
    }

    public String getId() { return id; }
    public MenuItem getMenuItem() { return menuItem; }
    public int getQuantity() { return quantity; }
    public String getNotes() { return notes; }
    public boolean isCancelled() { return cancelled; }

    public void setQuantity(int quantity) { this.quantity = quantity; }
    public void setNotes(String notes) { this.notes = notes; }
    public void cancel() { this.cancelled = true; }

    public double getSubtotal() {
        return cancelled ? 0 : menuItem.getPrice() * quantity;
    }

    @Override
    public String toString() {
        String status = cancelled ? " [CANCELLED]" : "";
        return String.format("%dx %s ($%.2f)%s", quantity, menuItem.getName(), getSubtotal(), status);
    }
}

class Order {
    private final String id;
    private final Table table;
    private final List<OrderItem> items;
    private OrderStatus status;
    private final LocalDateTime createdAt;
    private int itemCounter;

    public Order(String id, Table table) {
        this.id = id;
        this.table = table;
        this.items = new ArrayList<>();
        this.status = OrderStatus.PLACED;
        this.createdAt = LocalDateTime.now();
        this.itemCounter = 0;
    }

    public String getId() { return id; }
    public Table getTable() { return table; }
    public List<OrderItem> getItems() { return new ArrayList<>(items); }
    public OrderStatus getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }

    public OrderItem addItem(MenuItem menuItem, int quantity, String notes) {
        String itemId = id + "-I" + (++itemCounter);
        OrderItem item = new OrderItem(itemId, menuItem, quantity, notes);
        items.add(item);
        return item;
    }

    public OrderItem getItem(String itemId) {
        for (OrderItem item : items) {
            if (item.getId().equals(itemId)) {
                return item;
            }
        }
        return null;
    }

    public void setStatus(OrderStatus status) {
        this.status = status;
    }

    public double getTotal() {
        return items.stream().mapToDouble(OrderItem::getSubtotal).sum();
    }

    public List<OrderItem> getActiveItems() {
        List<OrderItem> active = new ArrayList<>();
        for (OrderItem item : items) {
            if (!item.isCancelled()) {
                active.add(item);
            }
        }
        return active;
    }

    @Override
    public String toString() {
        return String.format("Order[%s, table=%s, items=%d, total=$%.2f, status=%s]",
                id, table.getId(), getActiveItems().size(), getTotal(), status);
    }
}

class Reservation {
    private final String id;
    private final String customerName;
    private final String customerPhone;
    private final int partySize;
    private final LocalDateTime dateTime;
    private Table assignedTable;
    private boolean confirmed;
    private boolean cancelled;

    public Reservation(String id, String customerName, String customerPhone, 
                       int partySize, LocalDateTime dateTime) {
        this.id = id;
        this.customerName = customerName;
        this.customerPhone = customerPhone;
        this.partySize = partySize;
        this.dateTime = dateTime;
        this.confirmed = false;
        this.cancelled = false;
    }

    public String getId() { return id; }
    public String getCustomerName() { return customerName; }
    public String getCustomerPhone() { return customerPhone; }
    public int getPartySize() { return partySize; }
    public LocalDateTime getDateTime() { return dateTime; }
    public Table getAssignedTable() { return assignedTable; }
    public boolean isConfirmed() { return confirmed; }
    public boolean isCancelled() { return cancelled; }

    public void assignTable(Table table) {
        this.assignedTable = table;
        this.confirmed = true;
        table.setStatus(TableStatus.RESERVED);
    }

    public void cancel() {
        this.cancelled = true;
        if (assignedTable != null) {
            assignedTable.setStatus(TableStatus.AVAILABLE);
        }
    }

    @Override
    public String toString() {
        return String.format("Reservation[%s, %s, party=%d, at=%s, table=%s, confirmed=%s]",
                id, customerName, partySize, dateTime, 
                assignedTable != null ? assignedTable.getId() : "unassigned", confirmed);
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
    private final Map<String, Double> splits;

    public Bill(String id, Order order, double taxRate) {
        this.id = id;
        this.order = order;
        this.subtotal = order.getTotal();
        this.taxRate = taxRate;
        this.tax = subtotal * taxRate;
        this.tip = 0;
        this.paid = false;
        this.splits = new HashMap<>();
    }

    public String getId() { return id; }
    public Order getOrder() { return order; }
    public double getSubtotal() { return subtotal; }
    public double getTax() { return tax; }
    public double getTip() { return tip; }
    public boolean isPaid() { return paid; }
    public Map<String, Double> getSplits() { return new HashMap<>(splits); }

    public void setTip(double tip) { this.tip = tip; }

    public double getTotal() {
        return subtotal + tax + tip;
    }

    public void splitEvenly(int ways) {
        double perPerson = getTotal() / ways;
        for (int i = 1; i <= ways; i++) {
            splits.put("Person " + i, perPerson);
        }
    }

    public void splitByAmount(String person, double amount) {
        splits.put(person, amount);
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
    private final Map<String, Reservation> reservations;
    private int orderCounter;
    private int billCounter;
    private int reservationCounter;

    public RestaurantService() {
        this.tables = new HashMap<>();
        this.menuItems = new HashMap<>();
        this.orders = new HashMap<>();
        this.bills = new HashMap<>();
        this.reservations = new HashMap<>();
        this.orderCounter = 0;
        this.billCounter = 0;
        this.reservationCounter = 0;
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
        if (table != null && (table.getStatus() == TableStatus.AVAILABLE || 
                              table.getStatus() == TableStatus.RESERVED) && 
            table.getCapacity() >= partySize) {
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

    // Reservation Management
    public Reservation makeReservation(String name, String phone, int partySize, LocalDateTime dateTime) {
        String id = "RES-" + (++reservationCounter);
        Reservation reservation = new Reservation(id, name, phone, partySize, dateTime);
        
        // Find available table
        for (Table table : tables.values()) {
            if (table.getCapacity() >= partySize && table.isAvailableAt(dateTime)) {
                reservation.assignTable(table);
                break;
            }
        }
        
        reservations.put(id, reservation);
        return reservation;
    }

    public Reservation getReservation(String id) {
        return reservations.get(id);
    }

    public void cancelReservation(String id) {
        Reservation reservation = reservations.get(id);
        if (reservation != null) {
            reservation.cancel();
        }
    }

    public List<Reservation> getReservationsForDate(LocalDate date) {
        List<Reservation> result = new ArrayList<>();
        for (Reservation res : reservations.values()) {
            if (res.getDateTime().toLocalDate().equals(date) && !res.isCancelled()) {
                result.add(res);
            }
        }
        return result;
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

    public OrderItem addItemToOrder(String orderId, String menuItemId, int quantity, String notes) {
        Order order = orders.get(orderId);
        MenuItem menuItem = menuItems.get(menuItemId);
        if (order == null || menuItem == null || !menuItem.isAvailable()) {
            return null;
        }
        return order.addItem(menuItem, quantity, notes);
    }

    public boolean modifyOrderItem(String orderId, String itemId, int newQuantity, String newNotes) {
        Order order = orders.get(orderId);
        if (order == null || order.getStatus() != OrderStatus.PLACED) {
            return false;
        }
        OrderItem item = order.getItem(itemId);
        if (item == null) {
            return false;
        }
        if (newQuantity <= 0) {
            item.cancel();
        } else {
            item.setQuantity(newQuantity);
            if (newNotes != null) {
                item.setNotes(newNotes);
            }
        }
        return true;
    }

    public boolean cancelOrderItem(String orderId, String itemId) {
        return modifyOrderItem(orderId, itemId, 0, null);
    }

    public void updateOrderStatus(String orderId, OrderStatus status) {
        Order order = orders.get(orderId);
        if (order != null) {
            order.setStatus(status);
        }
    }

    public Order getOrder(String orderId) {
        return orders.get(orderId);
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
