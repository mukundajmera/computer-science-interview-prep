import java.util.ArrayList;
import java.util.List;

public class GatewayRouter {
    private final List<PaymentGateway> gateways;
    private final RoutingStrategy routingStrategy;
    private final IdempotencyStore idempotencyStore;

    public GatewayRouter(List<PaymentGateway> gateways, RoutingStrategy routingStrategy, IdempotencyStore idempotencyStore) {
        this.gateways = gateways;
        this.routingStrategy = routingStrategy;
        this.idempotencyStore = idempotencyStore;
    }

    public PaymentResponse routePayment(PaymentRequest request) {
        String key = request.getIdempotencyKey();
        
        // Idempotency Check
        if (key != null) {
            synchronized (idempotencyStore) {
                IdempotencyStore.State state = idempotencyStore.getState(key);
                if (state == IdempotencyStore.State.COMPLETED || state == IdempotencyStore.State.FAILED) {
                    return idempotencyStore.getResponse(key);
                } else if (state == IdempotencyStore.State.IN_PROGRESS) {
                    return new PaymentResponse(null, PaymentResponse.Status.CONFLICT, "Concurrent request with same idempotency key", null);
                }
                
                // If not locked, lock it
                idempotencyStore.lockOrCheck(key);
            }
        }

        // Routing
        PaymentResponse response = null;
        List<PaymentGateway> attemptedGateways = new ArrayList<>();
        
        while (attemptedGateways.size() < gateways.size()) {
            List<PaymentGateway> remainingGateways = new ArrayList<>(gateways);
            remainingGateways.removeAll(attemptedGateways);
            
            PaymentGateway selectedGateway = routingStrategy.route(remainingGateways, request);
            if (selectedGateway == null) {
                break; // No more available gateways
            }
            
            attemptedGateways.add(selectedGateway);
            response = selectedGateway.processPayment(request);
            
            if (response.getStatus() == PaymentResponse.Status.SUCCESS) {
                break; // Successfully processed
            }
            // If failed/timeout, continue to fallback loop
        }

        if (response == null) {
            response = new PaymentResponse(null, PaymentResponse.Status.FAILED, "All gateways failed or unavailable", null);
        }

        // Update Idempotency Store
        if (key != null) {
            IdempotencyStore.State finalState = response.getStatus() == PaymentResponse.Status.SUCCESS ? 
                IdempotencyStore.State.COMPLETED : IdempotencyStore.State.FAILED;
            idempotencyStore.update(key, finalState, response);
        }

        return response;
    }
}
