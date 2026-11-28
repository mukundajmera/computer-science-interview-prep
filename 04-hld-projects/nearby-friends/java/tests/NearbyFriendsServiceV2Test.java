import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class NearbyFriendsServiceV2Test {

    // ------------------------------------------------------------------
    // v1 parity tests: same scenarios as NearbyFriendsServiceTest, run
    // against v2.
    // ------------------------------------------------------------------

    @Test
    public void testLocationUpdateDispatched() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);

        List<LocationUpdateV2> received = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", received::add);

        service.updateLocation("FriendB", 40.7150, -74.0050, now);

        assertEquals(1, received.size());
        assertEquals("FriendB", received.get(0).getUserId());
    }

    @Test
    public void testDistanceCutoff() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);

        List<LocationUpdateV2> received = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", received::add);

        // LA coordinates (very far from NY)
        service.updateLocation("FriendB", 34.0522, -118.2437, now);

        assertEquals(0, received.size());
    }

    @Test
    public void testUserTtlExpiry() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);

        List<LocationUpdateV2> received = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", received::add);

        // Update is 11 minutes old
        service.updateLocation("FriendB", 40.7150, -74.0050, now - 11 * 60 * 1000L);

        assertEquals(0, received.size());
    }

    @Test
    public void testSubscribeUnsubscribeFriend() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);

        List<LocationUpdateV2> received = new ArrayList<>();
        Consumer<LocationUpdateV2> handler = service.subscribeToFriend("UserA", "FriendB", received::add);

        service.updateLocation("FriendB", 40.7150, -74.0050, now);
        assertEquals(1, received.size());

        service.unsubscribeFromFriend("FriendB", handler);
        service.updateLocation("FriendB", 40.7150, -74.0050, now);
        assertEquals(1, received.size()); // Should not increase
    }

    @Test
    public void testOfflineFriendNotNotified() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        // User A doesn't have an active location in cache

        List<LocationUpdateV2> received = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", received::add);

        service.updateLocation("FriendB", 40.7150, -74.0050, now);

        assertEquals(0, received.size());
    }

    // ------------------------------------------------------------------
    // v2-only tests: one or more per improvement.
    // ------------------------------------------------------------------

    // Improvement #1: offline-to-online initial state (FOLLOW-UPS.md #2).

    @Test
    public void testInitialStateDeliveredOnSubscribe() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);
        service.updateLocation("FriendB", 40.7150, -74.0050, now);

        List<LocationUpdateV2> received = new ArrayList<>();
        // FriendB already has a fresh in-range location before UserA subscribes.
        service.subscribeToFriend("UserA", "FriendB", received::add);

        assertEquals(1, received.size(), "subscriber gets the last known location immediately");
        assertEquals("FriendB", received.get(0).getUserId());

        service.updateLocation("FriendB", 40.7152, -74.0052, System.currentTimeMillis());
        assertEquals(2, received.size(), "live updates keep flowing after the snapshot");
    }

    @Test
    public void testInitialStateNotDeliveredWhenOutOfRange() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);
        service.updateLocation("FriendB", 34.0522, -118.2437, now); // LA

        List<LocationUpdateV2> received = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", received::add);

        assertEquals(0, received.size());
    }

    @Test
    public void testInitialStateNotDeliveredWhenStale() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);
        service.updateLocation("FriendB", 40.7150, -74.0050, now - 11 * 60 * 1000L); // 11 min old

        List<LocationUpdateV2> received = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", received::add);

        assertEquals(0, received.size());
    }

    // Improvement #2: fan-out metrics and throttling (FOLLOW-UPS.md #3,
    // PITFALLS.md #3).

    @Test
    public void testPublishCountMetric() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("FriendB", 40.7150, -74.0050, now);
        service.updateLocation("FriendB", 40.7151, -74.0051, now + 1000);
        service.updateLocation("FriendB", 40.7152, -74.0052, now + 2000);
        service.updateLocation("FriendC", 40.7150, -74.0050, now);

        assertEquals(3, bus.getPublishCount("FriendB"));
        assertEquals(1, bus.getPublishCount("FriendC"));
        assertEquals(0, bus.getPublishCount("Nobody"));
    }

    @Test
    public void testThrottleDropsBurstUpdates() throws InterruptedException {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus, 250);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);

        List<LocationUpdateV2> received = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", received::add);

        service.updateLocation("FriendB", 40.7150, -74.0050, now + 1000);  // delivered (first)
        service.updateLocation("FriendB", 40.7151, -74.0051, now + 2000);  // dropped (inside interval)
        Thread.sleep(300);
        service.updateLocation("FriendB", 40.7152, -74.0052, now + 3000);  // delivered (interval passed)

        assertEquals(2, received.size());
        assertEquals(40.7150, received.get(0).getLatitude(), 0.000001);
        assertEquals(40.7152, received.get(1).getLatitude(), 0.000001);
    }

    @Test
    public void testNoThrottleByDefault() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);

        List<LocationUpdateV2> received = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", received::add);

        service.updateLocation("FriendB", 40.7150, -74.0050, now + 1000);
        service.updateLocation("FriendB", 40.7151, -74.0051, now + 2000);

        assertEquals(2, received.size(), "v1 behavior: every update is delivered");
    }

    // Improvement #3: out-of-order rejection and input validation
    // (FOLLOW-UPS.md #4).

    @Test
    public void testOutOfOrderUpdateIgnored() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        service.updateLocation("UserA", 40.7128, -74.0060, now);

        List<LocationUpdateV2> received = new ArrayList<>();
        service.subscribeToFriend("UserA", "FriendB", received::add);

        service.updateLocation("FriendB", 40.7150, -74.0050, now);
        // A delayed duplicate from before the reconnect storm must not regress.
        service.updateLocation("FriendB", 34.0522, -118.2437, now - 30_000);

        LocationUpdateV2 stored = service.getUserLocation("FriendB");
        assertEquals(40.7150, stored.getLatitude(), 0.000001, "newer position is kept");
        assertEquals(1, received.size(), "stale update is not fanned out");
    }

    @Test
    public void testInvalidCoordinatesRejected() {
        PubSubBusV2 bus = new PubSubBusV2();
        NearbyFriendsServiceV2 service = new NearbyFriendsServiceV2(bus);

        long now = System.currentTimeMillis();
        assertThrows(IllegalArgumentException.class,
                () -> service.updateLocation("UserA", 91.0, -74.0060, now));
        assertThrows(IllegalArgumentException.class,
                () -> service.updateLocation("UserA", 40.7128, -181.0, now));
        assertThrows(IllegalArgumentException.class,
                () -> service.updateLocation("UserA", Double.NaN, -74.0060, now));

        assertNull(service.getUserLocation("UserA"), "invalid updates never stored");
    }
}
