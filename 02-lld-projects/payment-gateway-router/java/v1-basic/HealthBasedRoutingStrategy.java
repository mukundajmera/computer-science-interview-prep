import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

public class HealthBasedRoutingStrategy implements RoutingStrategy {
    @Override
    public PaymentGateway route(List<PaymentGateway> gateways, PaymentRequest request) {
        // Filter out gateways with OPEN circuit breakers and sort by success rate descending
        List<PaymentGateway> available = gateways.stream()
            .filter(g -> {
                if (g instanceof AbstractPaymentGateway) {
                    return ((AbstractPaymentGateway) g).getCircuitBreaker().allowRequest();
                }
                return true;
            })
            .sorted(Comparator.comparingDouble(PaymentGateway::getSuccessRate).reversed())
            .collect(Collectors.toList());

        if (available.isEmpty()) {
            return null; // All gateways unavailable
        }
        return available.get(0); // Highest success rate
    }
}
