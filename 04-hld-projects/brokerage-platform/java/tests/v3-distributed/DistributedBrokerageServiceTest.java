package brokerage.v3;

import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;

import static org.junit.jupiter.api.Assertions.*;

class DistributedBrokerageServiceTest {

    // Dummy implementation for testing
    static class DummyDistributedBrokerageService implements DistributedBrokerageService {
        List<OrderEvent> replicatedEvents = new ArrayList<>();
        Set<String> reconciledRegions = new HashSet<>();

        @Override
        public String routeOrderRegion(String userId, String symbol) {
            if (userId != null && userId.startsWith("eu")) {
                return "eu-west-1";
            }
            return "us-east-1";
        }

        @Override
        public void replicateOrderEvent(OrderEvent event) {
            replicatedEvents.add(event);
        }

        @Override
        public void reconcileRegion(String region) {
            reconciledRegions.add(region);
        }
    }

    @Test
    void routeOrderRegionReturnsCorrectRegion() {
        DummyDistributedBrokerageService service = new DummyDistributedBrokerageService();
        
        String regionEu = service.routeOrderRegion("eu_user1", "AAPL");
        assertEquals("eu-west-1", regionEu);
        
        String regionUs = service.routeOrderRegion("us_user1", "AAPL");
        assertEquals("us-east-1", regionUs);
    }

    @Test
    void replicateOrderEventRecordsEvent() {
        DummyDistributedBrokerageService service = new DummyDistributedBrokerageService();
        OrderEvent event = new OrderEvent("ord-1", "FILLED");
        
        service.replicateOrderEvent(event);
        
        assertEquals(1, service.replicatedEvents.size());
        assertEquals("ord-1", service.replicatedEvents.get(0).orderId);
        assertEquals("FILLED", service.replicatedEvents.get(0).eventType);
    }

    @Test
    void reconcileRegionRecordsRegion() {
        DummyDistributedBrokerageService service = new DummyDistributedBrokerageService();
        
        service.reconcileRegion("eu-west-1");
        service.reconcileRegion("us-east-1");
        
        assertTrue(service.reconciledRegions.contains("eu-west-1"));
        assertTrue(service.reconciledRegions.contains("us-east-1"));
    }
}
