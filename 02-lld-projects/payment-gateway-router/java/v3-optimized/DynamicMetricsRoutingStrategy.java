

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

public class DynamicMetricsRoutingStrategy implements RoutingStrategy {
    @Override
    public PaymentGateway route(List<PaymentGateway> gateways, PaymentRequest request) {
        List<PaymentGateway> available = gateways.stream()
            .filter(g -> {
                if (g instanceof AbstractPaymentGateway) {
                    return ((AbstractPaymentGateway) g).getCircuitBreaker().allowRequest();
                }
                return true;
            })
            .collect(Collectors.toList());

        if (available.isEmpty()) {
            return null;
        }

        // Sort by success rate descending, then latency ascending
        available.sort((g1, g2) -> {
            int successCompare = Double.compare(g2.getSuccessRate(), g1.getSuccessRate());
            if (successCompare != 0) {
                return successCompare;
            }
            return Double.compare(g1.getAverageLatency(), g2.getAverageLatency());
        });

        return available.get(0);
    }
}
