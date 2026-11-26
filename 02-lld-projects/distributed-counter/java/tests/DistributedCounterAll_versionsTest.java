import org.junit.Test;
import static org.junit.Assert.assertEquals;

public class DistributedCounterAll_versionsTest {

    private DistributedCounter getCounter() {
        return new DistributedCounter();
    }

    @Test
    public void testInitialValue() {
        DistributedCounter counter = getCounter();
        long val = counter.get();
        assertEquals(0, val);
    }
    
    @Test
    public void testSingleThreadIncrement() {
        DistributedCounter counter = getCounter();
        for (int i = 0; i < 100; i++) {
            counter.increment();
        }
        assertEquals(100, counter.get());
    }
    
    @Test
    public void testIncrementByValue() {
        DistributedCounter counter = getCounter();
        for (int i = 0; i < 100; i++) {
            counter.increment(5L);
        }
        assertEquals(500, counter.get());
    }
    
    @Test
    public void testMultiThreadIncrement() throws InterruptedException {
        DistributedCounter counter = getCounter();
        Thread[] threads = new Thread[10];
        
        for (int i = 0; i < 10; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 1000; j++) {
                    counter.increment();
                }
            });
        }
        
        for (Thread t : threads) { t.start(); }
        for (Thread t : threads) { t.join(); }
        
        assertEquals(10000, counter.get());
    }
    
    @Test
    public void testHighConcurrency() throws InterruptedException {
        DistributedCounter counter = getCounter();
        Thread[] threads = new Thread[50];
        
        for (int i = 0; i < 50; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 200; j++) {
                    counter.increment(1L);
                }
            });
        }
        
        for (Thread t : threads) { t.start(); }
        for (Thread t : threads) { t.join(); }
        
        assertEquals(10000, counter.get());
    }
}
