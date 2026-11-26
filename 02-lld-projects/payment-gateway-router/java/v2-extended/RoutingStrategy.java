
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;




public interface RoutingStrategy {
    PaymentGateway route(List<PaymentGateway> gateways, PaymentRequest request);
}
