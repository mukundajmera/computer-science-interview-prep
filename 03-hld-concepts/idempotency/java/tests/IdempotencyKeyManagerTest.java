import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class IdempotencyKeyManagerTest {

    private IdempotencyKeyManager manager;

    @BeforeEach
    public void setUp() {
        manager = new IdempotencyKeyManager(100); // 100ms TTL for testing
    }

    @Test
    public void testNewRequestAndCompletion() {
        String key = "key1";
        String payload = "payload1";

        IdempotencyKeyManager.Record record = manager.beginRequest(key, payload);
        assertEquals(IdempotencyKeyManager.Status.IN_PROGRESS, record.status);
        assertNull(record.response);

        manager.completeRequest(key, "response1");

        IdempotencyKeyManager.Record record2 = manager.beginRequest(key, payload);
        assertEquals(IdempotencyKeyManager.Status.COMPLETED, record2.status);
        assertEquals("response1", record2.response);
    }

    @Test
    public void testConflictOnDifferentPayload() {
        String key = "key2";
        manager.beginRequest(key, "payloadA");

        assertThrows(IdempotencyKeyManager.ConflictException.class, () -> {
            manager.beginRequest(key, "payloadB");
        });
    }

    @Test
    public void testFailedRequest() {
        String key = "key3";
        manager.beginRequest(key, "payload3");
        manager.failRequest(key);

        IdempotencyKeyManager.Record record = manager.beginRequest(key, "payload3");
        assertEquals(IdempotencyKeyManager.Status.FAILED, record.status);
    }

    @Test
    public void testExpiredRequestReplaced() throws InterruptedException {
        String key = "key4";
        manager.beginRequest(key, "payload4");

        Thread.sleep(150); // wait for TTL to expire

        // After expiration, a new request with the same key should succeed and be IN_PROGRESS
        // even with a different payload (as the previous is forgotten).
        IdempotencyKeyManager.Record record = manager.beginRequest(key, "payload5");
        assertEquals(IdempotencyKeyManager.Status.IN_PROGRESS, record.status);
    }

    @Test
    public void testCleanup() throws InterruptedException {
        manager.beginRequest("key5", "payload5");
        Thread.sleep(150);
        manager.cleanup(); // manual cleanup

        // Key should be gone, we can start fresh
        IdempotencyKeyManager.Record record = manager.beginRequest("key5", "payload6");
        assertEquals(IdempotencyKeyManager.Status.IN_PROGRESS, record.status);
    }

    @Test
    public void testInProgressConcurrentRejection() {
        String key = "key6";
        manager.beginRequest(key, "payload6");

        // A subsequent call with the same payload before completion should throw InProgressException
        assertThrows(IdempotencyKeyManager.InProgressException.class, () -> {
            manager.beginRequest(key, "payload6");
        });
    }
}
