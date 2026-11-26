package v3_optimized;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class V3OptimizedTest {

    @BeforeEach
    public void setup() {
        LoggerFactory.reset();
    }

    @AfterEach
    public void teardown() {
        LoggerFactory.getInstance().shutdown();
    }

    @Test
    public void testAsyncBatchFlushing() throws InterruptedException {
        LoggerFactory factory = LoggerFactory.getInstance();
        Logger root = factory.getLogger("root");
        
        root.getAppenders().clear();
        
        InMemoryAppender appender = new InMemoryAppender("Memory");
        root.addAppender(appender);
        root.setLevel(LogLevel.INFO);
        
        int threadCount = 10;
        int logsPerThread = 50;
        
        Thread[] threads = new Thread[threadCount];
        for (int i = 0; i < threadCount; i++) {
            final int threadId = i;
            threads[i] = new Thread(() -> {
                for (int j = 0; j < logsPerThread; j++) {
                    root.info("Thread " + threadId + " batch log " + j);
                }
            });
            threads[i].start();
        }
        
        for (Thread t : threads) {
            t.join();
        }
        
        // Wait for async processing
        Thread.sleep(1500);
        
        assertEquals(threadCount * logsPerThread, appender.getLogs().size(), "All logs should be batch processed asynchronously");
    }
}
