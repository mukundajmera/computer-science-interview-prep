package v3_optimized;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Arrays;

import static org.junit.jupiter.api.Assertions.*;

public class V2ExtendedTest {

    @BeforeEach
    public void setup() {
        LoggerFactory.reset();
    }

    @AfterEach
    public void teardown() {
        LoggerFactory.getInstance().shutdown();
    }

    @Test
    public void testCompositeAppender() throws InterruptedException {
        LoggerFactory factory = LoggerFactory.getInstance();
        Logger logger = factory.getLogger("test");
        logger.getAppenders().clear();
        
        InMemoryAppender a1 = new InMemoryAppender("A1");
        InMemoryAppender a2 = new InMemoryAppender("A2");
        CompositeAppender composite = new CompositeAppender("Comp", Arrays.asList(a1, a2));
        
        logger.addAppender(composite);
        logger.setLevel(LogLevel.INFO);
        
        logger.info("Test message");
        Thread.sleep(100);
        
        assertEquals(1, a1.getLogs().size());
        assertEquals(1, a2.getLogs().size());
    }

    @Test
    public void testRollingFileAppender() throws InterruptedException {
        LoggerFactory factory = LoggerFactory.getInstance();
        Logger logger = factory.getLogger("test");
        logger.getAppenders().clear();
        
        String path = "test_rolling.log";
        File f1 = new File(path);
        File f2 = new File(path + ".1");
        if(f1.exists()) f1.delete();
        if(f2.exists()) f2.delete();
        
        RollingFileAppender rfa = new RollingFileAppender("RFA", path, 100, 2, null);
        logger.addAppender(rfa);
        logger.setLevel(LogLevel.INFO);
        
        for(int i=0; i<10; i++) {
            logger.info("A somewhat long test message to force rolling " + "A somewhat long test message to force rolling " + i);
        }
        Thread.sleep(500);
        
        assertTrue(new File(path).exists());
        assertTrue(new File(path + ".1").exists());
        
        if(f1.exists()) f1.delete();
        if(f2.exists()) f2.delete();
    }
}
