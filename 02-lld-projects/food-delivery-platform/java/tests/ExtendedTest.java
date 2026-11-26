
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.Arrays;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class ExtendedTest {
    @Test
    public void testNearestDriver() {
        Restaurant rest = new Restaurant("R1", new Location(0, 0));
        Driver d1 = new Driver("D1", new Location(0, 10));
        Driver d2 = new Driver("D2", new Location(0, 5));
        
        DispatchStrategy strategy = new NearestDriverStrategy();
        Driver nearest = strategy.dispatch(rest, Arrays.asList(d1, d2));
        
        assertNotNull(nearest);
        assertEquals("D2", nearest.getId());
    }
    
    @Test
    public void testDriverManager() {
        DispatchStrategy strategy = new NearestDriverStrategy();
        DriverManager manager = new DriverManager(strategy);
        
        Driver d1 = new Driver("D1", new Location(0, 5));
        manager.addDriver(d1);
        
        Restaurant rest = new Restaurant("R1", new Location(0, 0));
        Driver assigned = manager.assignDriver(rest);
        
        assertNotNull(assigned);
        assertEquals("D1", assigned.getId());
        assertFalse(assigned.isAvailable());
    }

    @Test
    public void testConcurrentDriverAssignment() throws InterruptedException {
        DispatchStrategy strategy = new NearestDriverStrategy();
        DriverManager manager = new DriverManager(strategy);
        Driver sharedDriver = new Driver("D1", new Location(0, 5));
        manager.addDriver(sharedDriver);
        FoodDeliveryPlatform platform = new FoodDeliveryPlatform(manager);
        
        Restaurant rest = new Restaurant("R1", new Location(0, 0));
        
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
                    boolean success = platform.processOrder(order, rest, true, true);
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
        DispatchStrategy strategy = new NearestDriverStrategy();
        DriverManager manager = new DriverManager(strategy);
        Driver driver = new Driver("D1", new Location(0, 5));
        manager.addDriver(driver);
        FoodDeliveryPlatform platform = new FoodDeliveryPlatform(manager);
        
        Restaurant rest = new Restaurant("R1", new Location(0, 0));
        Order order = new Order("O1", 10.0);
        
        boolean first = platform.processOrder(order, rest, true, true);
        boolean second = platform.processOrder(order, rest, true, true);
        
        assertTrue(first);
        assertFalse(second);
        assertEquals(10.0, order.getFinalTotal());
    }

    @Test
    public void testLateAcceptancePreservesTotal() {
        DispatchStrategy strategy = new NearestDriverStrategy();
        DriverManager manager = new DriverManager(strategy);
        Driver driver = new Driver("D1", new Location(0, 5));
        manager.addDriver(driver);
        FoodDeliveryPlatform platform = new FoodDeliveryPlatform(manager);
        
        Restaurant rest = new Restaurant("R1", new Location(0, 0));
        Order order = new Order("O1", 10.0);
        
        boolean success = platform.processOrder(order, rest, false, true);
        
        assertFalse(success);
        assertEquals(10.0, order.getFinalTotal());
    }

    @Test
    public void testUnavailableStockPreservesTotal() {
        DispatchStrategy strategy = new NearestDriverStrategy();
        DriverManager manager = new DriverManager(strategy);
        Driver driver = new Driver("D1", new Location(0, 5));
        manager.addDriver(driver);
        FoodDeliveryPlatform platform = new FoodDeliveryPlatform(manager);
        
        Restaurant rest = new Restaurant("R1", new Location(0, 0));
        Order order = new Order("O1", 10.0);
        
        boolean success = platform.processOrder(order, rest, true, false);
        
        assertFalse(success);
        assertEquals(10.0, order.getFinalTotal());
    }
}
