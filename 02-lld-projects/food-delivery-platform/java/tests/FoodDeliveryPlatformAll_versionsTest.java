import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class FoodDeliveryPlatformAll_versionsTest {

    @Test
    public void testConcurrentDriverAssignment() throws InterruptedException {
        FoodDeliveryPlatform platform = new FoodDeliveryPlatform();
        String sharedDriverId = "D1";
        
        int numThreads = 10;
        CyclicBarrier barrier = new CyclicBarrier(numThreads);
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        AtomicInteger successCount = new AtomicInteger(0);

        for (int i = 0; i < numThreads; i++) {
            final String orderId = "O" + i;
            executor.submit(() -> {
                try {
                    Order order = new Order(orderId, 10.0);
                    barrier.await();
                    boolean success = platform.processOrder(order, sharedDriverId, true, true);
                    if (success) {
                        successCount.incrementAndGet();
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }

        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        assertEquals(1, successCount.get(), "Only one order should successfully claim the driver");
    }
    
    @Test
    public void testDuplicateOrderRequests() {
        FoodDeliveryPlatform platform = new FoodDeliveryPlatform();
        String driverId = "D1";
        Order order = new Order("O1", 10.0);
        
        boolean first = platform.processOrder(order, driverId, true, true);
        boolean second = platform.processOrder(order, driverId, true, true);
        
        assertTrue(first);
        assertFalse(second);
        assertEquals(10.0, order.getFinalTotal()); // Preserves exact order total
    }

    @Test
    public void testLateAcceptancePreservesTotal() {
        FoodDeliveryPlatform platform = new FoodDeliveryPlatform();
        String driverId = "D1";
        Order order = new Order("O1", 10.0);
        
        // Late acceptance (restaurant accepts = false)
        boolean success = platform.processOrder(order, driverId, false, true);
        
        assertFalse(success);
        assertEquals(10.0, order.getFinalTotal());
    }

    @Test
    public void testUnavailableStockPreservesTotal() {
        FoodDeliveryPlatform platform = new FoodDeliveryPlatform();
        String driverId = "D1";
        Order order = new Order("O1", 10.0);
        
        // Stock available = false
        boolean success = platform.processOrder(order, driverId, true, false);
        
        assertFalse(success);
        assertEquals(10.0, order.getFinalTotal());
    }
}
