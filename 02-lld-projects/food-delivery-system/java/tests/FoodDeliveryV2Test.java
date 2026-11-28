package tests;

import v1_basic.models.Courier;
import v1_basic.models.Customer;
import v2_extended.CancelResult;
import v2_extended.OrderV2;
import v2_extended.BaseDeliveryPricing;
import v2_extended.PercentDiscountDecorator;
import v2_extended.FlatDiscountDecorator;
import v2_extended.FoodDeliveryServiceV2;

import java.util.Arrays;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Main-style test runner (this project does not use JUnit; v1's test is
 * a main too). Run: java -cp /tmp/at-053-out tests.FoodDeliveryV2Test
 */
public class FoodDeliveryV2Test {
    public static void main(String[] args) throws InterruptedException {
        testBaseDeliveryPricingParity();
        testCancelBeforePreparationFullRefund();
        testCancelDuringPreparationPenaltyAndCourierFreed();
        testCancelRejectedOutForDelivery();
        testCancelRejectedWhenAlreadyCancelled();
        testTerminalStatesCannotAdvance();
        testPercentDiscountDecorator();
        testStackedDecorators();
        testFlatDiscountFloorsAtZero();
        testIdempotentPlacementReturnsOriginal();
        testDistinctKeysCreateDistinctOrders();
        testConcurrentAssignmentSingleWinner();
        System.out.println("All FoodDeliveryV2 tests passed!");
    }

    private static OrderV2 order30() {
        Customer customer = new Customer("U1", "Test", 0, 0);
        return new OrderV2("O1", customer, 0, 0, 30.0);
    }

    private static void testBaseDeliveryPricingParity() {
        BaseDeliveryPricing strategy = new BaseDeliveryPricing();
        Customer customer = new Customer("U1", "Test", 0, 3);
        OrderV2 order = new OrderV2("O1", customer, 4, 0, 25.0);
        // distance sqrt(4^2 + 3^2) = 5, fee = 5 + 5*2 = 15, same as v1
        double fee = strategy.calculatePrice(order);
        assertCondition(Math.abs(fee - 15.0) < 0.001, "Delivery fee should be 15.0");
    }

    private static void testCancelBeforePreparationFullRefund() {
        OrderV2 order = order30();
        CancelResult result = order.cancel();
        assertCondition(result.isCancelled(), "Cancel from PLACED should succeed");
        assertCondition(Math.abs(result.getRefund() - 30.0) < 0.001, "Refund should be the full 30.0");
        assertCondition("CANCELLED".equals(order.getState()), "State should be CANCELLED");
    }

    private static void testCancelDuringPreparationPenaltyAndCourierFreed() {
        FoodDeliveryServiceV2 service = new FoodDeliveryServiceV2();
        Courier courier = new Courier("C1", "Alice", 1, 1);
        service.addCourier(courier);
        OrderV2 order = order30();
        service.placeOrder("key-1", order);
        assertCondition(service.assignCourier(order), "Courier should be assigned");
        assertCondition("ASSIGNED".equals(order.getState()), "State should be ASSIGNED");

        CancelResult result = order.cancel();
        assertCondition(result.isCancelled(), "Cancel from ASSIGNED should succeed");
        assertCondition(Math.abs(result.getRefund() - 24.0) < 0.001,
            "Refund should be 80% of 30.0 = 24.0");
        assertCondition(courier.isAvailable(), "Cancelled order should free its courier");
    }

    private static void testCancelRejectedOutForDelivery() {
        OrderV2 order = order30();
        order.advance(); // ASSIGNED
        order.advance(); // OUT_FOR_DELIVERY
        CancelResult result = order.cancel();
        assertCondition(!result.isCancelled(), "Cancel from OUT_FOR_DELIVERY should be rejected");
        assertCondition(result.getRefund() == 0.0, "Rejected cancel refunds nothing");
        assertCondition("OUT_FOR_DELIVERY".equals(order.getState()), "State should be unchanged");
    }

    private static void testCancelRejectedWhenAlreadyCancelled() {
        OrderV2 order = order30();
        order.cancel();
        CancelResult second = order.cancel();
        assertCondition(!second.isCancelled(), "Second cancel should be rejected");
    }

    private static void testTerminalStatesCannotAdvance() {
        OrderV2 delivered = order30();
        delivered.advance();
        delivered.advance();
        delivered.advance(); // DELIVERED
        assertThrowsIllegalState(delivered::advance, "DELIVERED cannot advance");

        OrderV2 cancelled = order30();
        cancelled.cancel();
        assertThrowsIllegalState(cancelled::advance, "CANCELLED cannot advance");
    }

    private static void testPercentDiscountDecorator() {
        Customer customer = new Customer("U1", "Test", 0, 3);
        OrderV2 order = new OrderV2("O1", customer, 4, 0, 25.0);
        double price = new PercentDiscountDecorator(new BaseDeliveryPricing(), 10.0)
            .calculatePrice(order);
        // 15.0 base fee, 10% off = 13.5
        assertCondition(Math.abs(price - 13.5) < 0.001, "10% off 15.0 should be 13.5");
    }

    private static void testStackedDecorators() {
        Customer customer = new Customer("U1", "Test", 0, 3);
        OrderV2 order = new OrderV2("O1", customer, 4, 0, 25.0);
        // Flat $3 off, then 10% off the remainder: (15 - 3) * 0.9 = 10.8
        double price = new PercentDiscountDecorator(
            new FlatDiscountDecorator(new BaseDeliveryPricing(), 3.0), 10.0)
            .calculatePrice(order);
        assertCondition(Math.abs(price - 10.8) < 0.001, "Stacked discount should be 10.8");
    }

    private static void testFlatDiscountFloorsAtZero() {
        Customer customer = new Customer("U1", "Test", 0, 3);
        OrderV2 order = new OrderV2("O1", customer, 4, 0, 25.0);
        double price = new FlatDiscountDecorator(new BaseDeliveryPricing(), 50.0)
            .calculatePrice(order);
        assertCondition(price == 0.0, "Discount bigger than the fee should floor at 0, got " + price);
    }

    private static void testIdempotentPlacementReturnsOriginal() {
        FoodDeliveryServiceV2 service = new FoodDeliveryServiceV2();
        OrderV2 first = service.placeOrder("key-1", order30());
        OrderV2 second = service.placeOrder("key-1", order30());
        assertCondition(first == second, "Retry with the same key must return the original order");
        assertCondition(service.orderCount() == 1, "Duplicate key must not create a second order");
    }

    private static void testDistinctKeysCreateDistinctOrders() {
        FoodDeliveryServiceV2 service = new FoodDeliveryServiceV2();
        OrderV2 a = service.placeOrder("key-1", order30());
        OrderV2 b = service.placeOrder("key-2", order30());
        assertCondition(a != b, "Distinct keys create distinct orders");
        assertCondition(service.orderCount() == 2, "Two keys means two orders");
    }

    private static void testConcurrentAssignmentSingleWinner() throws InterruptedException {
        FoodDeliveryServiceV2 service = new FoodDeliveryServiceV2();
        service.addCourier(new Courier("C1", "Alice", 1, 1));
        OrderV2 order = order30();
        service.placeOrder("key-1", order);

        AtomicInteger wins = new AtomicInteger(0);
        Runnable tryAssign = () -> {
            if (service.assignCourier(order)) {
                wins.incrementAndGet();
            }
        };
        Thread t1 = new Thread(tryAssign);
        Thread t2 = new Thread(tryAssign);
        t1.start();
        t2.start();
        t1.join();
        t2.join();

        assertCondition(wins.get() == 1, "Exactly one concurrent assignment may win, got " + wins.get());
        assertCondition(order.getCourier() != null, "Order should have a courier");
    }

    private static void assertThrowsIllegalState(Runnable action, String message) {
        try {
            action.run();
            throw new AssertionError("Test failed: " + message);
        } catch (IllegalStateException expected) {
            // expected
        }
    }

    private static void assertCondition(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError("Test failed: " + message);
        }
    }
}
