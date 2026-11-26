import java.util.List;

public interface RoutingStrategy {
    PaymentGateway route(List<PaymentGateway> gateways, PaymentRequest request);
}
