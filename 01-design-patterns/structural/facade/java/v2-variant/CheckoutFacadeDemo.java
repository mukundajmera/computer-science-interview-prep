/**
 * Facade Pattern - V2 Variant: E-commerce Checkout.
 *
 * The facade hides inventory, payment, shipping, and notification subsystems
 * behind one checkout operation.
 */

import java.util.HashMap;
import java.util.Map;

class OrderConfirmation {
    private final String orderId;
    private final String paymentId;
    private final String shipmentId;
    private final double total;

    public OrderConfirmation(String orderId, String paymentId, String shipmentId, double total) {
        this.orderId = orderId;
        this.paymentId = paymentId;
        this.shipmentId = shipmentId;
        this.total = total;
    }

    public String getOrderId() { return orderId; }
    public String getPaymentId() { return paymentId; }
    public String getShipmentId() { return shipmentId; }
    public double getTotal() { return total; }
}

class InventoryService {
    private final Map<String, Integer> stockByItem;

    public InventoryService(Map<String, Integer> stockByItem) {
        this.stockByItem = new HashMap<>(stockByItem);
    }

    public int available(String itemId) {
        return stockByItem.getOrDefault(itemId, 0);
    }

    public void reserve(String itemId, int quantity) {
        if (available(itemId) < quantity) {
            throw new IllegalArgumentException("Insufficient stock for " + itemId);
        }
        stockByItem.put(itemId, available(itemId) - quantity);
    }
}

class CheckoutPaymentService {
    public String charge(double amount, String cardToken) {
        if (cardToken == null || cardToken.isBlank()) {
            throw new IllegalArgumentException("cardToken is required");
        }
        return "pay-" + Math.round(amount * 100);
    }
}

class ShippingService {
    private static final double SHIPPING_FEE = 5.00;

    public double quote(String address) {
        if (address == null || address.isBlank()) {
            throw new IllegalArgumentException("address is required");
        }
        return SHIPPING_FEE;
    }

    public String createShipment(String itemId, int quantity, String address) {
        if (address == null || address.isBlank()) {
            throw new IllegalArgumentException("address is required");
        }
        return "ship-" + itemId + "-" + quantity;
    }
}

class NotificationService {
    public String sendConfirmation(String email, String orderId) {
        if (email == null || !email.contains("@")) {
            throw new IllegalArgumentException("valid email is required");
        }
        return "sent:" + email + ":" + orderId;
    }
}

class CheckoutFacade {
    private final InventoryService inventory;
    private final CheckoutPaymentService payment;
    private final ShippingService shipping;
    private final NotificationService notifications;

    public CheckoutFacade(
            InventoryService inventory,
            CheckoutPaymentService payment,
            ShippingService shipping,
            NotificationService notifications) {
        this.inventory = inventory;
        this.payment = payment;
        this.shipping = shipping;
        this.notifications = notifications;
    }

    public OrderConfirmation placeOrder(
            String itemId,
            int quantity,
            double unitPrice,
            String cardToken,
            String address,
            String email) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("quantity must be positive");
        }

        inventory.reserve(itemId, quantity);
        double total = unitPrice * quantity + shipping.quote(address);
        String paymentId = payment.charge(total, cardToken);
        String shipmentId = shipping.createShipment(itemId, quantity, address);
        String orderId = "order-" + itemId + "-" + quantity;
        notifications.sendConfirmation(email, orderId);
        return new OrderConfirmation(orderId, paymentId, shipmentId, total);
    }
}

public class CheckoutFacadeDemo {
    public static void main(String[] args) {
        CheckoutFacade checkout = new CheckoutFacade(
            new InventoryService(Map.of("book", 3)),
            new CheckoutPaymentService(),
            new ShippingService(),
            new NotificationService()
        );

        OrderConfirmation confirmation = checkout.placeOrder(
            "book",
            1,
            20.00,
            "tok_123",
            "10 Main St",
            "reader@example.com"
        );
        System.out.println("Order placed: " + confirmation.getOrderId());
    }
}
