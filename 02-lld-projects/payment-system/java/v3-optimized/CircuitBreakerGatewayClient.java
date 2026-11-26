import java.util.concurrent.TimeoutException;

/**
 * CircuitBreakerGatewayClient for payment-system (v3-optimized).
 */
public class CircuitBreakerGatewayClient {
    private final String id;

    public static class GatewayResponse {
        public String status;
        public String referenceId;

        public GatewayResponse(String status, String referenceId) {
            this.status = status;
            this.referenceId = referenceId;
        }
    }

    public CircuitBreakerGatewayClient() {
        this.id = "CircuitBreakerGatewayClient";
    }

    public GatewayResponse charge(int amount, String token) throws TimeoutException {
        if (amount == 2000) {
            return new GatewayResponse("DECLINED", null);
        }
        if (amount == 3000) {
            throw new TimeoutException("Ambiguous gateway timeout");
        }
        if (amount == 4000) {
            throw new RuntimeException("Gateway crash");
        }
        return new GatewayResponse("SUCCESS", "ref_" + token);
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "CircuitBreakerGatewayClient:" + id;
    }
}
