/**
 * URL Shortener - V2 Scaled
 * 
 * Analytics processor for click event aggregation.
 * Consumes events from queue and updates statistics.
 */

import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Analytics service interface.
 */
interface AnalyticsService {
    /**
     * Record a click event.
     * @param event The click event
     */
    void recordClick(ClickEvent event);
    
    /**
     * Get total clicks for a URL.
     * @param shortCode The short code
     * @return Total click count
     */
    long getTotalClicks(String shortCode);
    
    /**
     * Get daily clicks for a URL.
     * @param shortCode The short code
     * @param date The date
     * @return Daily click count
     */
    long getDailyClicks(String shortCode, LocalDate date);
    
    /**
     * Get detailed analytics for a URL.
     * @param shortCode The short code
     * @return Analytics data
     */
    UrlAnalytics getAnalytics(String shortCode);
}

/**
 * Analytics data for a URL.
 */
class UrlAnalytics {
    private final String shortCode;
    private final long totalClicks;
    private final Map<String, Long> clicksByDate;
    private final Map<String, Long> clicksByCountry;
    private final Map<String, Long> topReferrers;
    
    public UrlAnalytics(String shortCode, long totalClicks,
                       Map<String, Long> clicksByDate,
                       Map<String, Long> clicksByCountry,
                       Map<String, Long> topReferrers) {
        this.shortCode = shortCode;
        this.totalClicks = totalClicks;
        this.clicksByDate = clicksByDate;
        this.clicksByCountry = clicksByCountry;
        this.topReferrers = topReferrers;
    }
    
    // Getters
    public String getShortCode() { return shortCode; }
    public long getTotalClicks() { return totalClicks; }
    public Map<String, Long> getClicksByDate() { return clicksByDate; }
    public Map<String, Long> getClicksByCountry() { return clicksByCountry; }
    public Map<String, Long> getTopReferrers() { return topReferrers; }
}

/**
 * In-memory analytics service implementation.
 * In production: Use ClickHouse, Druid, or similar OLAP database.
 */
class InMemoryAnalyticsService implements AnalyticsService {
    
    // shortCode -> total clicks
    private final Map<String, AtomicLong> totalClicks = new ConcurrentHashMap<>();
    
    // shortCode:date -> daily clicks
    private final Map<String, AtomicLong> dailyClicks = new ConcurrentHashMap<>();
    
    // shortCode:country -> clicks by country
    private final Map<String, AtomicLong> countryClicks = new ConcurrentHashMap<>();
    
    // shortCode:referrer -> clicks by referrer
    private final Map<String, AtomicLong> referrerClicks = new ConcurrentHashMap<>();
    
    @Override
    public void recordClick(ClickEvent event) {
        String shortCode = event.getShortCode();
        
        // Increment total clicks
        totalClicks.computeIfAbsent(shortCode, k -> new AtomicLong())
                   .incrementAndGet();
        
        // Increment daily clicks
        String dateKey = shortCode + ":" + 
            LocalDate.ofInstant(event.getTimestamp(), ZoneOffset.UTC);
        dailyClicks.computeIfAbsent(dateKey, k -> new AtomicLong())
                   .incrementAndGet();
        
        // Increment country clicks
        if (event.getCountry() != null) {
            String countryKey = shortCode + ":" + event.getCountry();
            countryClicks.computeIfAbsent(countryKey, k -> new AtomicLong())
                        .incrementAndGet();
        }
        
        // Increment referrer clicks
        if (event.getReferrer() != null && !event.getReferrer().isEmpty()) {
            String referrerKey = shortCode + ":" + event.getReferrer();
            referrerClicks.computeIfAbsent(referrerKey, k -> new AtomicLong())
                         .incrementAndGet();
        }
    }
    
    @Override
    public long getTotalClicks(String shortCode) {
        AtomicLong count = totalClicks.get(shortCode);
        return count != null ? count.get() : 0;
    }
    
    @Override
    public long getDailyClicks(String shortCode, LocalDate date) {
        String key = shortCode + ":" + date;
        AtomicLong count = dailyClicks.get(key);
        return count != null ? count.get() : 0;
    }
    
    @Override
    public UrlAnalytics getAnalytics(String shortCode) {
        long total = getTotalClicks(shortCode);
        
        // Aggregate daily clicks
        Map<String, Long> byDate = new java.util.HashMap<>();
        for (Map.Entry<String, AtomicLong> entry : dailyClicks.entrySet()) {
            if (entry.getKey().startsWith(shortCode + ":")) {
                String date = entry.getKey().substring(shortCode.length() + 1);
                byDate.put(date, entry.getValue().get());
            }
        }
        
        // Aggregate country clicks
        Map<String, Long> byCountry = new java.util.HashMap<>();
        for (Map.Entry<String, AtomicLong> entry : countryClicks.entrySet()) {
            if (entry.getKey().startsWith(shortCode + ":")) {
                String country = entry.getKey().substring(shortCode.length() + 1);
                byCountry.put(country, entry.getValue().get());
            }
        }
        
        // Aggregate top referrers
        Map<String, Long> byReferrer = new java.util.HashMap<>();
        for (Map.Entry<String, AtomicLong> entry : referrerClicks.entrySet()) {
            if (entry.getKey().startsWith(shortCode + ":")) {
                String referrer = entry.getKey().substring(shortCode.length() + 1);
                byReferrer.put(referrer, entry.getValue().get());
            }
        }
        
        return new UrlAnalytics(shortCode, total, byDate, byCountry, byReferrer);
    }
}

/**
 * Background worker that processes click events from queue.
 * In production: This would be a Kafka consumer or similar.
 */
class ClickEventProcessor implements Runnable {
    
    private final InMemoryMessageQueue messageQueue;
    private final AnalyticsService analyticsService;
    private final UrlRepository urlRepository;
    private volatile boolean running = true;
    
    public ClickEventProcessor(InMemoryMessageQueue messageQueue,
                               AnalyticsService analyticsService,
                               UrlRepository urlRepository) {
        this.messageQueue = messageQueue;
        this.analyticsService = analyticsService;
        this.urlRepository = urlRepository;
    }
    
    @Override
    public void run() {
        while (running) {
            java.util.List<ClickEvent> events = messageQueue.drain();
            
            for (ClickEvent event : events) {
                try {
                    // Update analytics
                    analyticsService.recordClick(event);
                    
                    // Update click count in database
                    urlRepository.incrementClickCount(event.getShortCode());
                    
                } catch (Exception e) {
                    System.err.println("Error processing click event: " + e.getMessage());
                    // In production: Send to dead letter queue
                }
            }
            
            // Sleep between batches
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    public void stop() {
        running = false;
    }
}
