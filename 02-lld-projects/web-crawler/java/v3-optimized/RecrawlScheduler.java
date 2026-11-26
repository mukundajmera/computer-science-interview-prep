package v3_optimized;

import java.util.HashMap;
import java.util.Map;

public class RecrawlScheduler {
    private static class Schedule {
        long nextCrawlTime;
        long intervalMs;
        
        Schedule(long nextCrawlTime, long intervalMs) {
            this.nextCrawlTime = nextCrawlTime;
            this.intervalMs = intervalMs;
        }
    }

    private final Map<String, Schedule> schedule = new HashMap<>();

    public synchronized void scheduleRecrawl(String url, long intervalMs) {
        schedule.put(url, new Schedule(System.currentTimeMillis() + intervalMs, intervalMs));
    }

    public synchronized boolean isReady(String url) {
        Schedule s = schedule.get(url);
        if (s != null) {
            return System.currentTimeMillis() >= s.nextCrawlTime;
        }
        return false;
    }
}
