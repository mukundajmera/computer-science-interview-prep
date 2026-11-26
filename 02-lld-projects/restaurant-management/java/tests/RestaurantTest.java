// Restaurant Management System - JUnit Tests

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.time.*;

public class RestaurantTest {

    private RestaurantService restaurant;

    @BeforeEach
    void setUp() {
        restaurant = new RestaurantService();
        // Setup tables
        restaurant.addTable("T1", 2);
        restaurant.addTable("T2", 4);
        restaurant.addTable("T3", 6);
        // Setup menu
        restaurant.addMenuItem("A1", "Appetizer", 10.0, MenuCategory.APPETIZER);
        restaurant.addMenuItem("M1", "Main", 25.0, MenuCategory.MAIN_COURSE);
        restaurant.addMenuItem("D1", "Dessert", 8.0, MenuCategory.DESSERT);
    }

    @Test
    void testTableManagement() {
        Table table = restaurant.getTable("T1");
        assertNotNull(table);
        assertEquals(2, table.getCapacity());
        assertEquals(TableStatus.AVAILABLE, table.getStatus());
    }

    @Test
    void testSeatParty() {
        assertTrue(restaurant.seatParty("T2", 4));
        assertEquals(TableStatus.OCCUPIED, restaurant.getTable("T2").getStatus());
        
        // Cannot seat another party at same table
        assertFalse(restaurant.seatParty("T2", 2));
    }

    @Test
    void testAvailableTables() {
        var available = restaurant.getAvailableTables(4);
        assertEquals(2, available.size()); // T2 and T3 can fit 4
        
        restaurant.seatParty("T2", 4);
        available = restaurant.getAvailableTables(4);
        assertEquals(1, available.size()); // Only T3 now
    }

    @Test
    void testMenuItems() {
        MenuItem item = restaurant.getMenuItem("M1");
        assertNotNull(item);
        assertEquals("Main", item.getName());
        assertEquals(25.0, item.getPrice());
        assertTrue(item.isAvailable());
    }

    @Test
    void testCreateOrder() {
        // Cannot create order for unseated table
        assertNull(restaurant.createOrder("T1"));
        
        // Seat and create order
        restaurant.seatParty("T1", 2);
        Order order = restaurant.createOrder("T1");
        assertNotNull(order);
        assertEquals(OrderStatus.PLACED, order.getStatus());
    }

    @Test
    void testAddItemsToOrder() {
        restaurant.seatParty("T1", 2);
        Order order = restaurant.createOrder("T1");
        
        assertNotNull(restaurant.addItemToOrder(order.getId(), "A1", 2, null));
        assertNotNull(restaurant.addItemToOrder(order.getId(), "M1", 2, "no salt"));
        
        assertEquals(2, order.getItems().size());
        assertEquals(70.0, order.getTotal()); // 2*10 + 2*25 = 70
    }

    @Test
    void testOrderWorkflow() {
        restaurant.seatParty("T1", 2);
        Order order = restaurant.createOrder("T1");
        restaurant.addItemToOrder(order.getId(), "M1", 1, null);
        
        assertEquals(OrderStatus.PLACED, order.getStatus());
        
        restaurant.updateOrderStatus(order.getId(), OrderStatus.PREPARING);
        assertEquals(OrderStatus.PREPARING, order.getStatus());
        
        restaurant.updateOrderStatus(order.getId(), OrderStatus.READY);
        assertEquals(OrderStatus.READY, order.getStatus());
        
        restaurant.updateOrderStatus(order.getId(), OrderStatus.SERVED);
        assertEquals(OrderStatus.SERVED, order.getStatus());
    }

    @Test
    void testBillGeneration() {
        restaurant.seatParty("T1", 2);
        Order order = restaurant.createOrder("T1");
        restaurant.addItemToOrder(order.getId(), "M1", 2, null);
        restaurant.updateOrderStatus(order.getId(), OrderStatus.SERVED);
        
        Bill bill = restaurant.generateBill(order.getId(), 0.10); // 10% tax
        assertNotNull(bill);
        assertEquals(50.0, bill.getSubtotal()); // 2 * 25
        assertEquals(5.0, bill.getTax()); // 10% of 50
        assertEquals(55.0, bill.getTotal()); // Before tip
    }

    @Test
    void testBillPayment() {
        restaurant.seatParty("T1", 2);
        Order order = restaurant.createOrder("T1");
        restaurant.addItemToOrder(order.getId(), "M1", 2, null);
        restaurant.updateOrderStatus(order.getId(), OrderStatus.SERVED);
        
        Bill bill = restaurant.generateBill(order.getId(), 0.10);
        assertTrue(restaurant.payBill(bill.getId(), 10.0)); // $10 tip
        
        assertTrue(bill.isPaid());
        assertEquals(10.0, bill.getTip());
        assertEquals(65.0, bill.getTotal()); // 50 + 5 + 10
        assertEquals(TableStatus.AVAILABLE, restaurant.getTable("T1").getStatus());
    }

    @Test
    void testReservation() {
        LocalDateTime time = LocalDateTime.now().plusHours(2);
        Reservation res = restaurant.makeReservation("John", "555-1234", 4, time);
        
        assertNotNull(res);
        assertEquals("John", res.getCustomerName());
        assertTrue(res.isConfirmed());
        assertNotNull(res.getAssignedTable());
    }

    @Test
    void testWaitlist() {
        WaitlistEntry entry = restaurant.addToWaitlist("Jane", "555-5678", 2);
        assertNotNull(entry);
        assertFalse(entry.isSeated());
        
        assertEquals(1, restaurant.getWaitlist().size());
        
        WaitlistEntry next = restaurant.getNextFromWaitlist(2);
        assertNotNull(next);
        assertEquals("Jane", next.getCustomerName());
        assertTrue(next.isSeated());
    }

    @Test
    void testKitchenDisplay() throws InterruptedException {
        restaurant.seatParty("T1", 2);
        Order order = restaurant.createOrder("T1");
        restaurant.addItemToOrder(order.getId(), "M1", 1, null);
        restaurant.submitOrderToKitchen(order.getId());
        
        KitchenDisplay kitchen = restaurant.getKitchenDisplay();
        assertEquals(1, kitchen.getPendingOrders().size());
        
        Order takenOrder = kitchen.takeNextOrder();
        assertEquals(order.getId(), takenOrder.getId());
        assertEquals(OrderStatus.PREPARING, order.getStatus());
        assertEquals(1, kitchen.getInProgressOrders().size());
        
        kitchen.markReady(order.getId());
        assertEquals(OrderStatus.READY, order.getStatus());
        assertEquals(1, kitchen.getReadyOrders().size());
    }

    @Test
    void testSplitBill() {
        restaurant.seatParty("T2", 4);
        Order order = restaurant.createOrder("T2");
        restaurant.addItemToOrder(order.getId(), "M1", 4, null);
        
        Bill bill = restaurant.generateBill(order.getId(), 0.10);
        bill.setTip(20.0);
        bill.splitEvenly(4);
        
        var splits = bill.getSplits();
        assertEquals(4, splits.size());
        double expected = (100.0 + 10.0 + 20.0) / 4; // 32.5 per person
        for (double amount : splits.values()) {
            assertEquals(expected, amount, 0.01);
        }
    }
}
