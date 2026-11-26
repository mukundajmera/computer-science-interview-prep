/**
 * GatewayRouterStrategy for payment-system (v2-extended).
 */
public class GatewayRouterStrategy {
    private final String id;

    public GatewayRouterStrategy() {
        this.id = "GatewayRouterStrategy";
    }

    public static class GatewayResponse {
        public String status;
        public String referenceId;

        public GatewayResponse(String status, String referenceId) {
            this.status = status;
            this.referenceId = referenceId;
        }
    }

    public GatewayResponse charge(int amount, String token) throws Exception {
        if (amount == 2000) {
            return new GatewayResponse("DECLINED", null);
        }
        if (amount == 3000) {
            throw new Exception("Ambiguous gateway timeout");
        }
        return new GatewayResponse("SUCCESS", "ref_" + token);
    }

    public String getId() {
        return id;
    }

    public String describe() {
        return "GatewayRouterStrategy:" + id;
    }
}
