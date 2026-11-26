import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.ArrayList;

import static org.junit.jupiter.api.Assertions.*;

class MessageQueueTest {
    private MessageQueueBroker broker;

    @BeforeEach
    void setUp() {
        broker = new MessageQueueBroker();
        broker.createTopic("test_topic", 3);
    }

    @Test
    void testMultiPartitionPublishSubscribe() {
        Producer producer = new Producer(broker);
        producer.send("test_topic", new Message("1", "Msg1"));
        producer.send("test_topic", new Message("2", "Msg2"));
        producer.send("test_topic", new Message("3", "Msg3"));

        Consumer consumer = new Consumer(broker, "group1", "test_topic");
        List<Message> polled = consumer.pollAndCommit();
        assertEquals(3, polled.size());
        
        // Verify round-robin assignment by checking partition sizes
        Topic topic = broker.getTopic("test_topic");
        assertEquals(1, topic.getPartitions().get(0).size());
        assertEquals(1, topic.getPartitions().get(1).size());
        assertEquals(1, topic.getPartitions().get(2).size());
    }

    @Test
    void testConsumerGroupOffsetIndependence() {
        Producer producer = new Producer(broker);
        producer.send("test_topic", new Message("1", "Msg1"));

        Consumer consumerG1 = new Consumer(broker, "group1", "test_topic");
        Consumer consumerG2 = new Consumer(broker, "group2", "test_topic");

        List<Message> polledG1 = consumerG1.pollAndCommit();
        assertEquals(1, polledG1.size());

        List<Message> polledG2 = consumerG2.pollAndCommit();
        assertEquals(1, polledG2.size());
        
        List<Message> polledG1Again = consumerG1.pollAndCommit();
        assertEquals(0, polledG1Again.size()); // G1 already consumed
    }

    @Test
    void testSubscriberDAGExecutionOrder() throws InterruptedException {
        SubscriberDAG dag = new SubscriberDAG();
        List<String> executionOrder = new ArrayList<>();

        dag.addSubscriber("A", () -> executionOrder.add("A"));
        dag.addSubscriber("B", () -> executionOrder.add("B"));
        dag.addSubscriber("C", () -> executionOrder.add("C"));

        // A -> B -> C
        dag.addDependency("A", "B");
        dag.addDependency("B", "C");

        dag.execute();

        assertEquals(List.of("A", "B", "C"), executionOrder);
    }

    @Test
    void testRetryAndDLQBehavior() {
        RetryPolicy policy = new RetryPolicy(2, 10);
        Message badMessage = new Message("error", "Bad payload");

        boolean success = policy.execute(() -> {
            throw new RuntimeException("Simulated failure");
        }, badMessage);

        assertFalse(success);
        assertEquals(1, policy.getDeadLetterQueue().size());
        assertEquals(badMessage, policy.getDeadLetterQueue().peek());
    }
}
