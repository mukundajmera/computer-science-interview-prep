import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class MessageQueueEvolutionSimulatorTest {

    private MessageQueueEvolutionSimulator sim;

    @BeforeEach
    public void setUp() {
        sim = new MessageQueueEvolutionSimulator();
    }

    @Test
    public void testAmqpTopicRoutingAndAck() {
        sim.createExchange("events_tx", "topic");
        sim.createQueue("orders_q");
        sim.createQueue("all_events_q");

        sim.bindQueue("events_tx", "orders_q", "order.*");
        sim.bindQueue("events_tx", "all_events_q", "#");

        sim.publishAmqp("events_tx", "order.created", "Order 123");
        sim.publishAmqp("events_tx", "user.signup", "User Bob");

        // orders_q gets only order.*
        assertEquals(1, sim.getQueueSize("orders_q"));
        // all_events_q gets everything (#)
        assertEquals(2, sim.getQueueSize("all_events_q"));

        // Test consumption
        MessageQueueEvolutionSimulator.Message msg = sim.consumeAmqp("orders_q");
        assertNotNull(msg);
        assertEquals("Order 123", msg.msg);

        // After consumption but before ACK, it should still be in the queue logically (or size doesn't decrease in our simple sim until ACK)
        // Let's ACK it
        MessageQueueEvolutionSimulator.Message ackedMsg = sim.ackAmqp("orders_q");
        assertNotNull(ackedMsg);
        assertEquals("Order 123", ackedMsg.msg);
        assertEquals(0, sim.getQueueSize("orders_q")); // Queue empty
    }

    @Test
    public void testKafkaPartitionAppendAndOffset() {
        sim.createTopicPartitions("clicks", 2);

        int o1 = sim.publishKafka("clicks", 0, "Click A");
        int o2 = sim.publishKafka("clicks", 0, "Click B");

        assertEquals(0, o1);
        assertEquals(1, o2);

        // Consume first
        MessageQueueEvolutionSimulator.KafkaMessage msg1 = sim.consumeKafka("clicks", 0, "cg1");
        assertNotNull(msg1);
        assertEquals("Click A", msg1.msg);

        // Consume again without committing (should get same message)
        MessageQueueEvolutionSimulator.KafkaMessage msg1Again = sim.consumeKafka("clicks", 0, "cg1");
        assertNotNull(msg1Again);
        assertEquals("Click A", msg1Again.msg);

        // Commit and consume next
        sim.commitOffsetKafka("clicks", 0, "cg1", msg1.offset);
        MessageQueueEvolutionSimulator.KafkaMessage msg2 = sim.consumeKafka("clicks", 0, "cg1");
        assertNotNull(msg2);
        assertEquals("Click B", msg2.msg);
    }

    @Test
    public void testKafkaOffsetReplay() {
        sim.createTopicPartitions("metrics", 1);
        for (int i = 0; i < 5; i++) {
            sim.publishKafka("metrics", 0, "Metric " + i);
        }

        // Consume and commit all
        for (int i = 0; i < 5; i++) {
            MessageQueueEvolutionSimulator.KafkaMessage msg = sim.consumeKafka("metrics", 0, "analytics_group");
            assertNotNull(msg);
            sim.commitOffsetKafka("metrics", 0, "analytics_group", msg.offset);
        }

        // Verify exhausted
        assertNull(sim.consumeKafka("metrics", 0, "analytics_group"));

        // Replay from offset 2
        sim.replayKafka("metrics", 0, "analytics_group", 2);
        MessageQueueEvolutionSimulator.KafkaMessage replayMsg = sim.consumeKafka("metrics", 0, "analytics_group");
        assertNotNull(replayMsg);
        assertEquals("Metric 2", replayMsg.msg);
    }

    @Test
    public void testPulsarSegmentRollAndColdTier() {
        String tp = "logs-partition-0";

        // Publish 8 messages. Segment size is 3. 
        // 2 full segments (6 msgs) in tiered storage, 2 msgs in active ledger.
        for (int i = 0; i < 8; i++) {
            sim.publishPulsar(tp, "Log " + i);
        }

        assertEquals(2, sim.getTieredStorageSize(tp));
        assertEquals(2, sim.getActiveLedgerSize(tp));

        // Consume cold data (Segment 0, index 1)
        MessageQueueEvolutionSimulator.PulsarFetchResult cold1 = sim.consumePulsar(tp, 1);
        assertNotNull(cold1);
        assertEquals("S3_TIERED", cold1.source);
        assertEquals("Log 1", cold1.msg);

        // Consume cold data (Segment 1, index 4)
        MessageQueueEvolutionSimulator.PulsarFetchResult cold2 = sim.consumePulsar(tp, 4);
        assertNotNull(cold2);
        assertEquals("S3_TIERED", cold2.source);
        assertEquals("Log 4", cold2.msg);

        // Consume active data (index 7)
        MessageQueueEvolutionSimulator.PulsarFetchResult active = sim.consumePulsar(tp, 7);
        assertNotNull(active);
        assertEquals("ACTIVE_BOOKIE", active.source);
        assertEquals("Log 7", active.msg);
    }
}
