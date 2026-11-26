package tests;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import v1simple.DistributedLock;
import v1simple.DistributedLock.LockServer;

public class DistributedLockTest {

    @Test
    public void testAcquireAndRelease() {
        LockServer server = new LockServer();
        DistributedLock lock = new DistributedLock(server, "res1", 5000, 2000);

        Long token = lock.acquire(false, null);
        assertNotNull(token);
        assertTrue(token > 0);

        DistributedLock lock2 = new DistributedLock(server, "res1", 5000, 2000);
        Long token2 = lock2.acquire(false, null);
        assertNull(token2);

        assertTrue(lock.release());

        Long token3 = lock2.acquire(false, null);
        assertNotNull(token3);
        assertTrue(token3 > token);

        assertTrue(lock2.release());
    }

    @Test
    public void testLockExpiration() throws InterruptedException {
        LockServer server = new LockServer();
        Long token = server.acquire("res1", "client1", 500);
        assertNotNull(token);

        Long token2 = server.acquire("res1", "client2", 1000);
        assertNull(token2);

        Thread.sleep(600);

        Long token3 = server.acquire("res1", "client2", 1000);
        assertNotNull(token3);
        assertTrue(token3 > token);
    }

    @Test
    public void testFencingTokenMonotonicity() {
        LockServer server = new LockServer();
        Long prevToken = server.acquire("res1", "client1", 1000);
        assertNotNull(prevToken);

        for (int i = 0; i < 5; i++) {
            Long currentToken = server.acquire("res" + i, "client" + i, 1000);
            assertNotNull(currentToken);
            assertTrue(currentToken > prevToken);
            prevToken = currentToken;
        }
    }

    @Test
    public void testHeartbeatRenewal() throws InterruptedException {
        LockServer server = new LockServer();
        DistributedLock lock = new DistributedLock(server, "res1", 1000, 300);

        Long token = lock.acquire(false, null);
        assertNotNull(token);

        Thread.sleep(1500);

        DistributedLock lock2 = new DistributedLock(server, "res1", 1000, 300);
        Long token2 = lock2.acquire(false, null);
        assertNull(token2);

        assertEquals(token, lock.getToken());
        lock.release();
    }

    @Test
    public void testOnlyOwnerCanReleaseAndRenew() {
        LockServer server = new LockServer();
        String c1 = "client1";
        String c2 = "client2";

        Long token = server.acquire("res1", c1, 5000);
        assertNotNull(token);

        assertFalse(server.release("res1", c2, token));
        assertFalse(server.renew("res1", c2, 5000, token));

        assertFalse(server.release("res1", c1, token + 1));
        assertFalse(server.renew("res1", c1, 5000, token + 1));

        assertTrue(server.renew("res1", c1, 5000, token));
        assertTrue(server.release("res1", c1, token));
    }
}
