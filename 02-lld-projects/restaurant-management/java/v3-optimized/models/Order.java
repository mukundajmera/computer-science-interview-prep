import enums.OrderStatus;
import java.util.*;

/**
 * Order.java - Restaurant order.
 */
public class Order {
    private final String orderId;
    private final Table table;
    private final List<OrderItem> items;
    private OrderStatus status;

    public Order(String orderId, Table table) {
        this.orderId = orderId;
        this.table = table;
        this.items = new ArrayList<>();
        this.status = OrderStatus.PLACED;
    }

    public void addItem(MenuItem item, int qty) {
        items.add(new OrderItem(item, qty));
    }

    public String getOrderId() {
        return orderId;
    }

    public Table getTable() {
        return table;
    }

    public OrderStatus getStatus() {
        return status;
    }

    public void setStatus(OrderStatus s) {
        this.status = s;
    }

    public double getTotal() {
        return items.stream().mapToDouble(OrderItem::getSubtotal).sum();
    }

    @Override
    public String toString() {
        return String.format("Order %s (Table %d) - $%.2f - %s",
                orderId, table.getTableNumber(), getTotal(), status);
    }
}

class OrderItem {
    private final MenuItem item;
    private final int quantity;

    public OrderItem(MenuItem item, int quantity) {
        this.item = item;
        this.quantity = quantity;
    }

    public double getSubtotal() {
        return item.getPrice() * quantity;
    }
}
