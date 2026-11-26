import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class SimpleProducerConsumerTest {

    @Test
    public void testProduceAndConsume() {
        SimpleProducerConsumer stream = new SimpleProducerConsumer(3);
        String key = "test-key";
        String message = "test-message";
        
        int partition = stream.partitionForKey(key);
        stream.produce(key, message);
        
        assertEquals(message, stream.consume(partition));
        assertEquals(1L, stream.currentOffset(partition));
    }

    @Test
    public void testConsumeEmptyPartitionReturnsNull() {
        SimpleProducerConsumer stream = new SimpleProducerConsumer(3);
        
        assertNull(stream.consume(0));
        assertEquals(0L, stream.currentOffset(0));
    }

    @Test
    public void testInvalidPartitionCountThrowsException() {
        assertThrows(IllegalArgumentException.class, () -> {
            new SimpleProducerConsumer(0);
        });
        assertThrows(IllegalArgumentException.class, () -> {
            new SimpleProducerConsumer(-1);
        });
    }

    @Test
    public void testDifferentKeysMayMapToDifferentPartitions() {
        SimpleProducerConsumer stream = new SimpleProducerConsumer(3);
        
        stream.produce("key1", "msg1");
        stream.produce("key2", "msg2");
        stream.produce("key3", "msg3");
        
        int p1 = stream.partitionForKey("key1");
        int p2 = stream.partitionForKey("key2");
        int p3 = stream.partitionForKey("key3");
        
        assertEquals("msg1", stream.consume(p1));
        assertEquals("msg2", stream.consume(p2));
        assertEquals("msg3", stream.consume(p3));
    }
}
