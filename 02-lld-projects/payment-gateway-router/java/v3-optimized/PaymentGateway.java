

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

public interface PaymentGateway {
    String getName();
    PaymentResponse processPayment(PaymentRequest request);
    double getSuccessRate();
    double getAverageLatency();
    void recordMetrics(boolean success, double latency);
}
