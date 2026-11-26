import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class CounterTest {

    @Test
    public void testInitialValue() {
        Counter counter = new Counter();
        long val = counter.get();
        assertEquals(0, val);
    }
    
    @Test
    public void testSingleThreadIncrement() {
        Counter counter = new Counter();
        for (int i = 0; i < 100; i++) {
            counter.increment();
        }
        assertEquals(100, counter.get());
    }
    
    @Test
    public void testIncrementByValue() {
        Counter counter = new Counter();
        for (int i = 0; i < 100; i++) {
            counter.increment(5);
        }
        assertEquals(500, counter.get());
    }
    
    @Test
    public void testMultiThreadIncrement() throws InterruptedException {
        Counter counter = new Counter();
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
        Counter counter = new Counter();
        Thread[] threads = new Thread[50];
        
        for (int i = 0; i < 50; i++) {
            threads[i] = new Thread(() -> {
                for (int j = 0; j < 200; j++) {
                    counter.increment(1);
                }
            });
        }
        
        for (Thread t : threads) { t.start(); }
        for (Thread t : threads) { t.join(); }
        
        assertEquals(10000, counter.get());
    }
}
