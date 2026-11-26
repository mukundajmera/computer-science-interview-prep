package v3_optimized;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import v3_optimized.*;

import static org.junit.jupiter.api.Assertions.*;

public class LoggingFrameworkTest {

    @BeforeEach
    public void setup() {
        LoggerFactory.reset();
    }

    @AfterEach
    public void teardown() {
        LoggerFactory.getInstance().shutdown();
    }

    @Test
    public void testLogLevelFiltering() throws InterruptedException {
        LoggerFactory factory = LoggerFactory.getInstance();
        Logger root = factory.getLogger("root");
        
        InMemoryAppender appender = new InMemoryAppender("Memory");
        // Clear default console appender for clean test
        root.getAppenders().clear();
        root.addAppender(appender);
        
        root.setLevel(LogLevel.INFO);
        
        root.debug("Debug msg"); // Should be ignored
        root.info("Info msg");   // Should be logged
        root.error("Error msg"); // Should be logged
        
        // Wait for async processor
        Thread.sleep(100);
        
        assertEquals(2, appender.getLogs().size());
        assertEquals(LogLevel.INFO, appender.getLogs().get(0).getLevel());
        assertEquals(LogLevel.ERROR, appender.getLogs().get(1).getLevel());
    }

    @Test
    public void testHierarchicalLevelInheritance() throws InterruptedException {
        LoggerFactory factory = LoggerFactory.getInstance();
        Logger root = factory.getLogger("root");
        root.setLevel(LogLevel.ERROR);
        
        Logger parent = factory.getLogger("com.myapp");
        parent.setLevel(LogLevel.DEBUG);
        
        Logger child = factory.getLogger("com.myapp.service");
        // Child inherits from parent (DEBUG)
        
        assertEquals(LogLevel.ERROR, root.getEffectiveLevel());
        assertEquals(LogLevel.DEBUG, parent.getEffectiveLevel());
        assertEquals(LogLevel.DEBUG, child.getEffectiveLevel());
        
        InMemoryAppender appender = new InMemoryAppender("Memory");
        child.addAppender(appender);
        child.setAdditive(false); // don't go to root appenders
        
        child.trace("Trace msg"); // ignored
        child.info("Info msg");   // logged
        
        Thread.sleep(100);
        
        assertEquals(1, appender.getLogs().size());
        assertEquals("Info msg", appender.getLogs().get(0).getMessage());
    }

    @Test
    public void testAppenderAdditivity() throws InterruptedException {
        LoggerFactory factory = LoggerFactory.getInstance();
        
        Logger parent = factory.getLogger("com.parent");
        InMemoryAppender parentAppender = new InMemoryAppender("ParentMemory");
        parent.addAppender(parentAppender);
        
        Logger child = factory.getLogger("com.parent.child");
        InMemoryAppender childAppender = new InMemoryAppender("ChildMemory");
        child.addAppender(childAppender);
        
        // Additivity is true by default
        child.info("Hello Additivity");
        
        Thread.sleep(100);
        
        assertEquals(1, childAppender.getLogs().size());
        assertEquals(1, parentAppender.getLogs().size());
        
        // Turn off additivity
        child.setAdditive(false);
        child.info("No more parents");
        
        Thread.sleep(100);
        
        assertEquals(2, childAppender.getLogs().size());
        assertEquals(1, parentAppender.getLogs().size()); // Parent didn't get second message
    }

    @Test
    public void testMultiThreadedAsyncLogFlushing() throws InterruptedException {
        LoggerFactory factory = LoggerFactory.getInstance();
        Logger root = factory.getLogger("root");
        
        // Clear root appenders to avoid console spam
        root.getAppenders().clear();
        
        InMemoryAppender appender = new InMemoryAppender("Memory");
        root.addAppender(appender);
        root.setLevel(LogLevel.INFO);
        
        int threadCount = 10;
        int logsPerThread = 100;
        
        Thread[] threads = new Thread[threadCount];
        for (int i = 0; i < threadCount; i++) {
            final int threadId = i;
            threads[i] = new Thread(() -> {
                for (int j = 0; j < logsPerThread; j++) {
                    root.info("Thread " + threadId + " log " + j);
                }
            });
            threads[i].start();
        }
        
        for (Thread t : threads) {
            t.join();
        }
        
        // Allow time for async processor to flush all messages
        Thread.sleep(500);
        
        assertEquals(threadCount * logsPerThread, appender.getLogs().size(), "All logs should be processed asynchronously");
    }
}
