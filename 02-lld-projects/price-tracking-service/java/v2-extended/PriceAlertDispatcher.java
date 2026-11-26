package v2_extended;

import java.time.Clock;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

interface ChannelAdapter {
    void send(String userId, String message);
}

class EmailAdapter implements ChannelAdapter {
    @Override
    public void send(String userId, String message) {
        System.out.println("Sending Email to " + userId + ": " + message);
    }
}

class SMSAdapter implements ChannelAdapter {
    @Override
    public void send(String userId, String message) {
        System.out.println("Sending SMS to " + userId + ": " + message);
    }
}

class PushAdapter implements ChannelAdapter {
    @Override
    public void send(String userId, String message) {
        System.out.println("Sending PUSH to " + userId + ": " + message);
    }
}

class MockAdapter implements ChannelAdapter {
    @Override
    public void send(String userId, String message) {
        // mock
    }
}

class RateLimitedDispatcher {
    private final Map<Channel, ChannelAdapter> adapters;
    private final int rateLimitWindowSec;
    private final Map<String, Long> lastSent = new ConcurrentHashMap<>();
    private final Clock clock;

    RateLimitedDispatcher(Map<Channel, ChannelAdapter> adapters, int rateLimitWindowSec, Clock clock) {
        this.adapters = adapters;
        this.rateLimitWindowSec = rateLimitWindowSec;
        this.clock = clock;
    }

    public boolean dispatch(String subscriptionId, String userId, Channel channel, String message) {
        long now = clock.instant().getEpochSecond();
        Long last = lastSent.get(subscriptionId);
        
        if (last != null && (now - last) < rateLimitWindowSec) {
            return false;
        }

        ChannelAdapter adapter = adapters.get(channel);
        if (adapter != null) {
            adapter.send(userId, message);
            lastSent.put(subscriptionId, now);
            return true;
        }
        return false;
    }
}
