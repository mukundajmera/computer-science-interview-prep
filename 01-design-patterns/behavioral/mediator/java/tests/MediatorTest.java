import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.ArrayList;
import java.util.List;

import mediator.v1.*;
import mediator.v2.DialogMediatorDemo.*;
import mediator.v3.ServiceBrokerMediatorDemo.*;

public class MediatorTest {

    private static class TestUser extends User {
        List<String> receivedMessages = new ArrayList<>();
        List<String> receivedSenders = new ArrayList<>();

        public TestUser(ChatMediator mediator, String name) {
            super(mediator, name);
        }

        @Override
        public void send(String message) {
            mediator.sendMessage(message, this);
        }

        @Override
        public void receive(String message, String from) {
            receivedMessages.add(message);
            receivedSenders.add(from);
        }
    }

    @Test
    @DisplayName("User broadcasts message to other users via ChatRoom")
    void testUserBroadcastsMessageToOtherUsers() {
        ChatRoom chatRoom = new ChatRoom();
        TestUser alice = new TestUser(chatRoom, "Alice");
        TestUser bob = new TestUser(chatRoom, "Bob");

        chatRoom.addUser(alice);
        chatRoom.addUser(bob);

        alice.send("Hello Bob!");

        assertEquals(1, bob.receivedMessages.size());
        assertEquals("Hello Bob!", bob.receivedMessages.get(0));
        assertEquals("Alice", bob.receivedSenders.get(0));

        assertEquals(0, alice.receivedMessages.size());
    }

    @Test
    @DisplayName("Adding multiple users distributes messages to all other participants")
    void testAddingUsersIncreasesChatParticipants() {
        ChatRoom chatRoom = new ChatRoom();
        TestUser u1 = new TestUser(chatRoom, "U1");
        TestUser u2 = new TestUser(chatRoom, "U2");
        TestUser u3 = new TestUser(chatRoom, "U3");

        chatRoom.addUser(u1);
        chatRoom.addUser(u2);
        chatRoom.addUser(u3);

        u1.send("Group announcement");

        assertEquals(0, u1.receivedMessages.size());
        assertEquals(1, u2.receivedMessages.size());
        assertEquals(1, u3.receivedMessages.size());
    }

    @Test
    @DisplayName("Concrete ChatUser interactions complete without throwing exceptions")
    void testDirectSendDoesNotThrow() {
        ChatMediator mediator = new ChatRoom();
        ChatUser user1 = new ChatUser(mediator, "John");
        ChatUser user2 = new ChatUser(mediator, "Jane");

        mediator.addUser(user1);
        mediator.addUser(user2);

        assertDoesNotThrow(() -> user1.send("Hi Jane"));
        assertDoesNotThrow(() -> user2.send("Hi John"));
    }

    @Test
    @DisplayName("v2 Dialog Mediator coordinates form validation state")
    void testDialogMediatorFormValidation() {
        AuthenticationDialogMediator dialog = new AuthenticationDialogMediator();
        assertFalse(dialog.getSubmitButton().isEnabled());

        dialog.getUsernameBox().setText("alice");
        assertFalse(dialog.getSubmitButton().isEnabled());

        dialog.getPasswordBox().setText("secret");
        assertFalse(dialog.getSubmitButton().isEnabled());

        dialog.getTermsCheckbox().setChecked(true);
        assertTrue(dialog.getSubmitButton().isEnabled());

        dialog.getSubmitButton().click();
        assertTrue(dialog.isSubmitted());

        dialog.getUsernameBox().setText("");
        assertFalse(dialog.getSubmitButton().isEnabled());
    }

    @Test
    @DisplayName("v3 Service Broker Mediator orchestrates multi-service choreography")
    void testServiceBrokerMediatorFlow() {
        ServiceBroker broker = new ServiceBroker();
        OrderService orderService = new OrderService();
        InventoryService inventoryService = new InventoryService();
        PaymentService paymentService = new PaymentService();
        NotificationService notificationService = new NotificationService();

        broker.subscribe("ORDER_CREATED", inventoryService);
        broker.subscribe("INVENTORY_RESERVED", paymentService);
        broker.subscribe("PAYMENT_COMPLETED", notificationService);

        orderService.createOrder(broker, "ORD-404", 199.99);

        assertTrue(orderService.getCreatedOrders().contains("ORD-404"));
        assertTrue(inventoryService.getReservedOrders().contains("ORD-404"));
        assertTrue(paymentService.getProcessedPayments().contains("ORD-404"));
        assertEquals(1, notificationService.getNotifications().size());
        assertTrue(notificationService.getNotifications().get(0).contains("ORD-404"));

        assertEquals(1, broker.countEventsByType("ORDER_CREATED"));
        assertEquals(1, broker.countEventsByType("INVENTORY_RESERVED"));
        assertEquals(1, broker.countEventsByType("PAYMENT_COMPLETED"));
        assertEquals(3, broker.getHistory().size());
    }
}
