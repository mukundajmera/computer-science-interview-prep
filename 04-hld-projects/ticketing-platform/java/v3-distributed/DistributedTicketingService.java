/**
 * Ticketing Platform - V3 Distributed
 * Skeleton for multi-region event partitioning and booking orchestration.
 */

import java.util.Arrays;
import java.util.List;
import java.util.Map;

public class DistributedTicketingService {

    public static class RegionPlan {
        private final String eventId;
        private final String primaryRegion;
        private final List<String> readRegions;

        public RegionPlan(String eventId, String primaryRegion, List<String> readRegions) {
            this.eventId = eventId;
            this.primaryRegion = primaryRegion;
            this.readRegions = readRegions;
        }

        public String getEventId() { return eventId; }
        public String getPrimaryRegion() { return primaryRegion; }
        public List<String> getReadRegions() { return readRegions; }
    }

    public interface RegionRouter {
        String routeReadRegion(String userRegion, String eventId);
        String routeWriteRegion(String eventId);
    }

    public interface BookingOrchestrator {
        String createBooking(String region, String eventId, String holdId, String paymentToken, String idempotencyKey);
        void reconcile(String bookingId);
    }

    public interface MetricsSink {
        void record(String metricName, double value, Map<String, String> tags);
    }

    public interface GlobalEventRepository {
        List<Map<String, String>> search(String region, String city, int page, int pageSize);
    }

    private final RegionRouter router;
    private final BookingOrchestrator orchestrator;
    private final GlobalEventRepository eventRepo;

    public DistributedTicketingService(RegionRouter router, BookingOrchestrator orchestrator, GlobalEventRepository eventRepo) {
        this.router = router;
        this.orchestrator = orchestrator;
        this.eventRepo = eventRepo;
    }

    public List<Map<String, String>> searchEventsGlobal(String userRegion, String city, int page, int pageSize) {
        String region = router.routeReadRegion(userRegion, "*");
        return eventRepo.search(region, city, page, pageSize);
    }

    public String createBookingGlobal(String eventId, String holdId, String paymentToken, String idempotencyKey) {
        String region = router.routeWriteRegion(eventId);
        return orchestrator.createBooking(region, eventId, holdId, paymentToken, idempotencyKey);
    }

    public RegionPlan getRegionPlan(String eventId) {
        String primary = router.routeWriteRegion(eventId);
        return new RegionPlan(eventId, primary, Arrays.asList(primary, "eu-west-1", "ap-northeast-1"));
    }
}
