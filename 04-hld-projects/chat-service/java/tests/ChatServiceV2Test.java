package chatservice.v2;

import org.junit.jupiter.api.Test;
import java.util.UUID;
import java.util.List;
import java.time.Instant;

import static org.junit.jupiter.api.Assertions.*;

class ChatServiceV2Test {

    // Simple cache for testing
    static class MockCache implements Cache {
        private final java.util.Map<String, String> data = new java.util.HashMap<>();

        @Override
        public String get(String key) {
            return data.get(key);
        }

        @Override
        public void set(String key, String value, int ttlSeconds) {
            data.put(key, value);
        }

        @Override
        public void delete(String key) {
            data.remove(key);
        }

        @Override
        public void publish(String channel, String message) {
            // Not tested here
        }

        @Override
        public void subscribe(String channel, CacheSubscriber subscriber) {
            // Not tested here
        }
    }

    @Test
    void testRedisPresenceService() {
        Cache cache = new MockCache();
        RedisPresenceService presenceService = new RedisPresenceService(cache);
        
        UUID userId = UUID.randomUUID();
        String deviceId = "device-1";
        String wsServerId = "server-1";
        
        presenceService.setOnline(userId, deviceId, wsServerId);
        
        UserPresence presence = presenceService.getPresence(userId);
        assertNotNull(presence);
        assertEquals(UserPresence.Status.ONLINE, presence.getStatus());
        
        presenceService.setOffline(userId, deviceId);
        presence = presenceService.getPresence(userId);
        assertEquals(UserPresence.Status.OFFLINE, presence.getStatus());
    }
}
