import java.util.*;

/**
 * Tests for State Pattern implementations.
 */
public class StateTest {

    public static void main(String[] args) {
        StateTest test = new StateTest();
        test.testVendingMachineDispensesAndReturnsToIdle();
        test.testOrderLifecycle();
        test.testShippedOrderRejectsCancellation();
        test.testDocumentRequiresApprovalBeforePublish();
        test.testPublishedDocumentCanArchiveButNotEdit();
        System.out.println("All tests passed.");
    }

    private void assertEquals(Object expected, Object actual, double delta) {
        if (expected instanceof Double && actual instanceof Double) {
            if (Math.abs((Double) expected - (Double) actual) > delta) {
                throw new AssertionError("Expected " + expected + " but got " + actual);
            }
        } else if (!Objects.equals(expected, actual)) {
            throw new AssertionError("Expected " + expected + " but got " + actual);
        }
    }

    private void assertEquals(Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            throw new AssertionError("Expected " + expected + " but got " + actual);
        }
    }

    private void assertTrue(boolean condition) {
        if (!condition) {
            throw new AssertionError("Condition was false");
        }
    }

    private void testVendingMachineDispensesAndReturnsToIdle() {
        VendingMachine machine = new VendingMachine();

        machine.insertMoney(1.00);
        machine.insertMoney(0.50);
        machine.selectProduct();

        assertEquals(0.0, machine.getBalance(), 0.01);
        machine.selectProduct();
        assertEquals(0.0, machine.getBalance(), 0.01);
    }

    private void testOrderLifecycle() {
        Order order = new Order("order-1001");

        order.pay("card");
        order.ship("TRK-1");
        order.deliver();

        assertEquals("DELIVERED", order.getStatus());
        assertEquals("TRK-1", order.getTrackingNumber());
        assertEquals(Arrays.asList("CREATED", "PAID", "SHIPPED", "DELIVERED"), order.getHistory());
    }

    private void testShippedOrderRejectsCancellation() {
        Order order = new Order("order-1002");
        order.pay("wallet");
        order.ship("TRK-2");

        IllegalStateException error = null;
        try {
            order.cancel("buyer changed mind");
            throw new AssertionError("Expected IllegalStateException");
        } catch (IllegalStateException e) {
            error = e;
        }
        assertTrue(error.getMessage().contains("Cannot cancel"));
    }

    private void testDocumentRequiresApprovalBeforePublish() {
        DocumentWorkflow workflow = new DocumentWorkflow("design-doc");

        workflow.submitForReview("alice");
        try {
            workflow.publish("alice");
            throw new AssertionError("Expected IllegalStateException");
        } catch (IllegalStateException e) {
            // expected
        }

        workflow.approve("lead");
        workflow.publish("alice");

        assertEquals("PUBLISHED", workflow.getStatus());
        assertEquals(Collections.singletonList("lead"), workflow.getApprovals());
    }

    private void testPublishedDocumentCanArchiveButNotEdit() {
        DocumentWorkflow workflow = new DocumentWorkflow("api-contract");
        workflow.edit("initial content");
        workflow.submitForReview("alice");
        workflow.approve("lead");
        workflow.publish("alice");

        IllegalStateException error = null;
        try {
            workflow.edit("breaking rewrite");
            throw new AssertionError("Expected IllegalStateException");
        } catch (IllegalStateException e) {
            error = e;
        }
        assertTrue(error.getMessage().contains("published"));

        workflow.archive("superseded");

        assertEquals("ARCHIVED", workflow.getStatus());
        assertEquals("superseded", workflow.getArchiveReason());
    }
}
