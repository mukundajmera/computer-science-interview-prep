
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;

public class MessageQueueV2Test {

    @Test
    void testConsumerGroupOffsets() {
        MessageQueueBroker broker = new MessageQueueBroker();
        broker.createTopic("topic1", 1);
        Producer producer = new Producer(broker);
        
        producer.send("topic1", new Message("m1", "payload1"));
        producer.send("topic1", new Message("m2", "payload2"));
        
        Consumer c1 = new Consumer(broker, "group1", "topic1");
        
        List<Message> msgs = c1.poll();
        assertEquals(1, msgs.size());
        assertEquals("m1", msgs.get(0).getId());
        
        msgs = c1.poll();
        assertEquals(1, msgs.size());
        assertEquals("m2", msgs.get(0).getId());
        
        c1.ack(new Message("m2", "payload2"));
        c1.nack(new Message("m1", "payload1"));
        
        msgs = c1.poll();
        assertEquals(1, msgs.size());
        assertEquals("m1", msgs.get(0).getId());
        
        c1.ack(msgs.get(0));
        
        assertEquals(0, c1.poll().size());
    }

    @Test
    void testLoadBalancing() {
        MessageQueueBroker broker = new MessageQueueBroker();
        broker.createTopic("topic3", 2);
        
        Consumer c1 = new Consumer(broker, "group1", "topic3");
        Consumer c2 = new Consumer(broker, "group1", "topic3");
        
        Producer producer = new Producer(broker);
        producer.send("topic3", new Message("m1", "1"));
        producer.send("topic3", new Message("m2", "2"));
        
        List<Message> m1 = c1.poll();
        List<Message> m2 = c2.poll();
        
        assertEquals(1, m1.size());
        assertEquals(1, m2.size());
    }
}
