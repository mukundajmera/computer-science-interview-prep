
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

public class MessageQueueV3Test {

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
    void testSubscriberDagDependencies() {
        MessageQueueBroker broker = new MessageQueueBroker();
        broker.createTopic("topic2", 1);
        
        SubscriberDAG dag = broker.getDag("topic2");
        dag.addDependency("groupA", "groupB"); // groupB depends on groupA
        
        Producer producer = new Producer(broker);
        producer.send("topic2", new Message("m1", "data"));
        
        Consumer cA = new Consumer(broker, "groupA", "topic2");
        Consumer cB = new Consumer(broker, "groupB", "topic2");
        
        List<Message> msgsB = cB.poll();
        assertEquals(0, msgsB.size());
        
        List<Message> msgsA = cA.poll();
        assertEquals(1, msgsA.size());
        assertEquals("m1", msgsA.get(0).getId());
        
        msgsB = cB.poll();
        assertEquals(0, msgsB.size());
        
        cA.ack(msgsA.get(0));
        
        msgsB = cB.poll();
        assertEquals(1, msgsB.size());
        assertEquals("m1", msgsB.get(0).getId());
    }

    @Test
    void testDlqRetryPolicy() {
        RetryPolicy policy = new RetryPolicy(2, 10, 100, 2.0);
        AtomicInteger failCount = new AtomicInteger(0);
        
        Runnable failingAction = () -> {
            failCount.incrementAndGet();
            throw new RuntimeException("error");
        };
        
        Message msg = new Message("m1", "test");
        boolean success = policy.execute(failingAction, msg);
        
        assertFalse(success);
        assertEquals(3, failCount.get());
        assertEquals(1, policy.getDeadLetterQueue().size());
        assertEquals("m1", policy.getDeadLetterQueue().get(0).getId());
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

    @Test
    void testRegexSubscription() {
        MessageQueueBroker broker = new MessageQueueBroker();
        broker.createTopic("test_a", 1);
        broker.createTopic("test_b", 1);
        
        Producer producer = new Producer(broker);
        producer.send("test_a", new Message("m1", "a"));
        producer.send("test_b", new Message("m2", "b"));
        
        Consumer c = new Consumer(broker, "group1", "test_.*");
        
        List<Message> msgs = c.poll();
        assertEquals(2, msgs.size());
        boolean hasM1 = msgs.stream().anyMatch(m -> m.getId().equals("m1"));
        boolean hasM2 = msgs.stream().anyMatch(m -> m.getId().equals("m2"));
        assertTrue(hasM1);
        assertTrue(hasM2);
    }
}
