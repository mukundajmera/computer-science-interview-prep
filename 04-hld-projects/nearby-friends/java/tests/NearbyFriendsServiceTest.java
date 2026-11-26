import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.function.Consumer;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class NearbyFriendsServiceTest {
    private PubSubBus pubSubBus;
    private NearbyFriendsService service;

    @BeforeEach
    public void setup() {
        pubSubBus = new PubSubBus();
        service = new NearbyFriendsService(pubSubBus);
    }

    @Test
    public void testLocationUpdateDispatchesToSubscribedFriends() {
        long now = System.currentTimeMillis();
        // User A coordinates
        service.updateLocation("UserA", 40.7128, -74.0060, now);
        
        List<LocationUpdate> receivedUpdates = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", receivedUpdates::add);

        // Friend B updates location within 5 miles
        // (New York City coordinates, slightly offset)
        service.updateLocation("FriendB", 40.7150, -74.0050, now);

        assertEquals(1, receivedUpdates.size());
        assertEquals("FriendB", receivedUpdates.get(0).getUserId());
    }

    @Test
    public void testFriendsBeyondRadiusExcluded() {
        long now = System.currentTimeMillis();
        // User A coordinates in NY
        service.updateLocation("UserA", 40.7128, -74.0060, now);
        
        List<LocationUpdate> receivedUpdates = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", receivedUpdates::add);

        // Friend B updates location in LA (far away)
        service.updateLocation("FriendB", 34.0522, -118.2437, now);

        assertEquals(0, receivedUpdates.size(), "Should not receive update if beyond 5 miles");
    }

    @Test
    public void testUserInactivityExpirationViaTTL() {
        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);
        
        List<LocationUpdate> receivedUpdates = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", receivedUpdates::add);

        // Friend B updates location, but the timestamp is 11 minutes ago
        long oldTimestamp = now - (11 * 60 * 1000);
        service.updateLocation("FriendB", 40.7150, -74.0050, oldTimestamp);

        assertEquals(0, receivedUpdates.size(), "Should not receive update if beyond 10 minute TTL");
    }

    @Test
    public void testFriendshipSubscriptionManagement() {
        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);
        
        List<LocationUpdate> receivedUpdates = new ArrayList<>();
        
        Consumer<LocationUpdate> handler = service.subscribeToFriend("UserA", "FriendB", receivedUpdates::add);

        service.updateLocation("FriendB", 40.7150, -74.0050, now);
        assertEquals(1, receivedUpdates.size());

        // Unsubscribe
        service.unsubscribeFromFriend("FriendB", handler);
        
        service.updateLocation("FriendB", 40.7150, -74.0050, now);
        assertEquals(1, receivedUpdates.size(), "Should not increase after unsubscribe");
    }

    @Test
    public void testHighThroughputConcurrentPushes() throws InterruptedException {
        int threads = 50;
        int updatesPerThread = 100;
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(threads);
        
        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);
        
        List<LocationUpdate> receivedUpdates = new ArrayList<>();
        Object lock = new Object();
        service.subscribeToFriend("UserA", "FriendB", update -> {
            synchronized (lock) {
                receivedUpdates.add(update);
            }
        });

        for (int i = 0; i < threads; i++) {
            executor.submit(() -> {
                for (int j = 0; j < updatesPerThread; j++) {
                    service.updateLocation("FriendB", 40.7150, -74.0050, System.currentTimeMillis());
                }
                latch.countDown();
            });
        }

        assertTrue(latch.await(5, TimeUnit.SECONDS));
        assertEquals(threads * updatesPerThread, receivedUpdates.size());
        executor.shutdown();
    }
}
