package mediator.v3;

import java.util.*;

/**
 * v3-advanced: Service Broker Event Mediator Pattern.
 * Decouples microservices/subsystems by mediating asynchronous-style domain events
 * (Order, Inventory, Payment, Notification) through a central broker mediator with
 * event auditing and topic routing.
 */
public class ServiceBrokerMediatorDemo {

    public static class Event {
        private final String type;
        private final String source;
        private final Map<String, Object> payload;
        private final long timestamp;

        public Event(String type, String source, Map<String, Object> payload) {
            this.type = Objects.requireNonNull(type);
            this.source = Objects.requireNonNull(source);
            this.payload = payload != null ? Collections.unmodifiableMap(new HashMap<>(payload)) : Collections.emptyMap();
            this.timestamp = System.currentTimeMillis();
        }

        public String getType() {
            return type;
        }

        public String getSource() {
            return source;
        }

        public Map<String, Object> getPayload() {
            return payload;
        }

        public long getTimestamp() {
            return timestamp;
        }

        @Override
        public String toString() {
            return "Event{" + "type='" + type + '\'' + ", source='" + source + '\'' + ", payload=" + payload + '}';
        }
    }

    public interface ServiceParticipant {
        String getName();
        void onEvent(Event event, ServiceBroker broker);
    }

    public static class ServiceBroker {
        private final Map<String, List<ServiceParticipant>> subscribers = new HashMap<>();
        private final List<Event> eventHistory = new ArrayList<>();

        public void subscribe(String eventType, ServiceParticipant participant) {
            subscribers.computeIfAbsent(eventType, k -> new ArrayList<>()).add(participant);
        }

        public void publish(Event event) {
            eventHistory.add(event);
            List<ServiceParticipant> listeners = subscribers.getOrDefault(event.getType(), Collections.emptyList());
            for (ServiceParticipant participant : new ArrayList<>(listeners)) {
                participant.onEvent(event, this);
            }
        }

        public List<Event> getHistory() {
            return Collections.unmodifiableList(eventHistory);
        }

        public int countEventsByType(String eventType) {
            int count = 0;
            for (Event e : eventHistory) {
                if (eventType.equals(e.getType())) {
                    count++;
                }
            }
            return count;
        }
    }

    public static class OrderService implements ServiceParticipant {
        private final List<String> createdOrders = new ArrayList<>();

        @Override
        public String getName() {
            return "OrderService";
        }

        public void createOrder(ServiceBroker broker, String orderId, double amount) {
            createdOrders.add(orderId);
            Map<String, Object> payload = new HashMap<>();
            payload.put("orderId", orderId);
            payload.put("amount", amount);
            broker.publish(new Event("ORDER_CREATED", getName(), payload));
        }

        @Override
        public void onEvent(Event event, ServiceBroker broker) {
            // Can react to payment failure or compensation events if needed
        }

        public List<String> getCreatedOrders() {
            return Collections.unmodifiableList(createdOrders);
        }
    }

    public static class InventoryService implements ServiceParticipant {
        private final Set<String> reservedOrders = new HashSet<>();

        @Override
        public String getName() {
            return "InventoryService";
        }

        @Override
        public void onEvent(Event event, ServiceBroker broker) {
            if ("ORDER_CREATED".equals(event.getType())) {
                String orderId = (String) event.getPayload().get("orderId");
                reservedOrders.add(orderId);
                Map<String, Object> payload = new HashMap<>();
                payload.put("orderId", orderId);
                payload.put("status", "RESERVED");
                broker.publish(new Event("INVENTORY_RESERVED", getName(), payload));
            }
        }

        public Set<String> getReservedOrders() {
            return Collections.unmodifiableSet(reservedOrders);
        }
    }

    public static class PaymentService implements ServiceParticipant {
        private final Set<String> processedPayments = new HashSet<>();

        @Override
        public String getName() {
            return "PaymentService";
        }

        @Override
        public void onEvent(Event event, ServiceBroker broker) {
            if ("INVENTORY_RESERVED".equals(event.getType())) {
                String orderId = (String) event.getPayload().get("orderId");
                processedPayments.add(orderId);
                Map<String, Object> payload = new HashMap<>();
                payload.put("orderId", orderId);
                payload.put("status", "CHARGED");
                broker.publish(new Event("PAYMENT_COMPLETED", getName(), payload));
            }
        }

        public Set<String> getProcessedPayments() {
            return Collections.unmodifiableSet(processedPayments);
        }
    }

    public static class NotificationService implements ServiceParticipant {
        private final List<String> notifications = new ArrayList<>();

        @Override
        public String getName() {
            return "NotificationService";
        }

        @Override
        public void onEvent(Event event, ServiceBroker broker) {
            if ("PAYMENT_COMPLETED".equals(event.getType())) {
                String orderId = (String) event.getPayload().get("orderId");
                notifications.add("Receipt sent for order: " + orderId);
            }
        }

        public List<String> getNotifications() {
            return Collections.unmodifiableList(notifications);
        }
    }

    public static void main(String[] args) {
        ServiceBroker broker = new ServiceBroker();
        OrderService orderService = new OrderService();
        InventoryService inventoryService = new InventoryService();
        PaymentService paymentService = new PaymentService();
        NotificationService notificationService = new NotificationService();

        broker.subscribe("ORDER_CREATED", inventoryService);
        broker.subscribe("INVENTORY_RESERVED", paymentService);
        broker.subscribe("PAYMENT_COMPLETED", notificationService);

        orderService.createOrder(broker, "ORD-9901", 149.99);

        System.out.println("Total events recorded: " + broker.getHistory().size());
        System.out.println("Notifications: " + notificationService.getNotifications());
    }
}
